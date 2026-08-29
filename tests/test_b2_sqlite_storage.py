import asyncio
import multiprocessing

from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.sqlite_checkpoints import SQLiteCheckpointStore
from honest_agent.schemas.models import Config, EvaluationRequest


def _worker(path, request, decision, queue, reviewer):
    from honest_agent.schemas.models import CheckpointStatus, DecisionStatus, HumanCheckpoint
    store = SQLiteCheckpointStore(path)
    decision.status = DecisionStatus.REJECTED
    decision.action_taken = "REJECTED_BY_HUMAN"
    decision.human_checkpoint = HumanCheckpoint(status=CheckpointStatus.REJECTED, reviewer=reviewer)
    queue.put(store.resolve_pending(request, decision).human_checkpoint.reviewer)


def _guard(tmp_path):
    config = Config(
        trajectory_dir=str(tmp_path / "traces"),
        checkpoint_backend="sqlite",
        checkpoint_database_path=str(tmp_path / "checkpoints.sqlite3"),
    )
    return HonestGuard(config=config), config


def test_sqlite_checkpoint_survives_restart(tmp_path):
    guard, config = _guard(tmp_path)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="unknown", tool_name="write_file", tool_input={"path": "x"})))
    restarted = SQLiteCheckpointStore(config.checkpoint_database_path)
    assert restarted.get_pending(pending.trajectory_id) is not None


def test_sqlite_resolution_is_single_winner_across_processes(tmp_path):
    guard, config = _guard(tmp_path)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="unknown", tool_name="write_file", tool_input={"path": "x"})))
    request, decision = SQLiteCheckpointStore(config.checkpoint_database_path).get_pending(pending.trajectory_id)
    context = multiprocessing.get_context("fork")
    queue = context.Queue()
    workers = [context.Process(target=_worker, args=(config.checkpoint_database_path, request, decision.model_copy(deep=True), queue, name)) for name in ("alice", "bob")]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=10)
        assert worker.exitcode == 0
    assert queue.get(timeout=2) == queue.get(timeout=2)
    resolved = SQLiteCheckpointStore(config.checkpoint_database_path).get_resolved(pending.trajectory_id)
    assert resolved is not None
    assert SQLiteCheckpointStore(config.checkpoint_database_path).get_pending(pending.trajectory_id) is None


def test_sqlite_backup_and_restore(tmp_path):
    guard, config = _guard(tmp_path)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="unknown", tool_name="write_file", tool_input={"path": "x"})))
    source = SQLiteCheckpointStore(config.checkpoint_database_path)
    backup = tmp_path / "backup.sqlite3"
    restored_path = tmp_path / "restored.sqlite3"
    source.backup(str(backup))
    restored = SQLiteCheckpointStore.restore(str(backup), str(restored_path))
    assert restored.get_pending(pending.trajectory_id) is not None
