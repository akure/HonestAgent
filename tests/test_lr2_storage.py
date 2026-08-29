import asyncio
import multiprocessing
import time

from honest_agent.core.checkpoints import FileCheckpointStore
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import CheckpointStatus, Config, DecisionStatus, EvaluationRequest, HumanCheckpoint


def _resolve_worker(path, request, decision, reviewer, output):
    store = FileCheckpointStore(path)
    decision.status = DecisionStatus.REJECTED
    decision.action_taken = "REJECTED_BY_HUMAN"
    decision.human_checkpoint = HumanCheckpoint(status=CheckpointStatus.REJECTED, reviewer=reviewer)
    winner = store.resolve_pending(request, decision)
    output.put(winner.human_checkpoint.reviewer)


def _pending(tmp_path):
    config = Config(
        trajectory_dir=str(tmp_path / "trajectories"),
        checkpoint_path=str(tmp_path / "checkpoints.json"),
    )
    guard = HonestGuard(config=config)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="ambiguous unknown", tool_name="write_file", tool_input={"path": "x"})))
    return config, guard, pending


def test_checkpoint_survives_store_restart(tmp_path):
    config, guard, pending = _pending(tmp_path)
    restarted = FileCheckpointStore(config.checkpoint_path)
    request, decision = restarted.get_pending(pending.trajectory_id)
    assert request.tool_name == "write_file"
    assert decision.trajectory_id == pending.trajectory_id


def test_cross_process_resolution_is_compare_and_set(tmp_path):
    config, guard, pending = _pending(tmp_path)
    store = FileCheckpointStore(config.checkpoint_path)
    request, decision = store.get_pending(pending.trajectory_id)
    context = multiprocessing.get_context("fork")
    output = context.Queue()
    workers = [context.Process(target=_resolve_worker, args=(config.checkpoint_path, request, decision.model_copy(deep=True), reviewer, output)) for reviewer in ("alice", "bob")]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=10)
        assert worker.exitcode == 0
    reviewers = {output.get(timeout=2), output.get(timeout=2)}
    resolved = FileCheckpointStore(config.checkpoint_path).get_resolved(pending.trajectory_id)
    assert len(reviewers) == 1
    assert resolved is not None
    assert resolved.human_checkpoint.reviewer in {"alice", "bob"}
    assert FileCheckpointStore(config.checkpoint_path).get_pending(pending.trajectory_id) is None


def test_retention_prunes_old_records(tmp_path):
    config, guard, pending = _pending(tmp_path)
    path = config.checkpoint_path
    store = FileCheckpointStore(path, retention_seconds=1)
    time.sleep(1.1)
    fresh_store = FileCheckpointStore(path, retention_seconds=1)
    assert fresh_store.get_pending(pending.trajectory_id) is None
