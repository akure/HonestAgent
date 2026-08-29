import asyncio

import pytest

from honest_agent.core.executor import ExecutionBlocked, ExecutorGateway
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, EvaluationRequest


class RecordingUpstream:
    enabled = True

    def __init__(self):
        self.calls = []

    async def chat_completions(self, payload):
        self.calls.append(payload)
        return {"id": "executed", "choices": []}


def _proceed(tmp_path):
    config = Config(
        trajectory_dir=str(tmp_path / "trajectories"),
        checkpoint_path=str(tmp_path / "checkpoints.json"),
    )
    guard = HonestGuard(config=config)
    request = EvaluationRequest(context="known verified record", tool_name="lookup", tool_input={"id": 1})
    decision = asyncio.run(guard.evaluate(request))
    assert decision.handoff_token
    return guard, request, decision


def test_executor_requires_valid_handoff_before_upstream_call(tmp_path):
    guard, request, decision = _proceed(tmp_path)
    upstream = RecordingUpstream()
    result = asyncio.run(ExecutorGateway(guard, upstream).execute(request, decision.handoff_token, decision.trajectory_id, {"model": "x"}))
    assert result["id"] == "executed"
    assert len(upstream.calls) == 1


@pytest.mark.parametrize("token", [None, "malformed", "invalid.signature"])
def test_executor_blocks_missing_or_invalid_handoff_without_side_effect(tmp_path, token):
    guard, request, decision = _proceed(tmp_path)
    upstream = RecordingUpstream()
    with pytest.raises(ExecutionBlocked):
        asyncio.run(ExecutorGateway(guard, upstream).execute(request, token, decision.trajectory_id, {"model": "x"}))
    assert upstream.calls == []


def test_executor_blocks_payload_and_trajectory_mismatch(tmp_path):
    guard, request, decision = _proceed(tmp_path)
    upstream = RecordingUpstream()
    altered = request.model_copy(update={"tool_input": {"id": 999}})
    with pytest.raises(ExecutionBlocked):
        asyncio.run(ExecutorGateway(guard, upstream).execute(altered, decision.handoff_token, decision.trajectory_id, {"model": "x"}))
    with pytest.raises(ExecutionBlocked):
        asyncio.run(ExecutorGateway(guard, upstream).execute(request, decision.handoff_token, "wrong-trajectory", {"model": "x"}))
    assert upstream.calls == []


def test_paused_decision_cannot_reach_executor(tmp_path):
    config = Config(
        trajectory_dir=str(tmp_path / "trajectories"),
        checkpoint_path=str(tmp_path / "checkpoints.json"),
    )
    guard = HonestGuard(config=config)
    request = EvaluationRequest(context="unknown dependency", tool_name="db_migrate", tool_input={"table": "accounts"}, irreversible=True)
    decision = asyncio.run(guard.evaluate(request))
    assert decision.handoff_token is None
    upstream = RecordingUpstream()
    with pytest.raises(ExecutionBlocked):
        asyncio.run(ExecutorGateway(guard, upstream).execute(request, decision.handoff_token, decision.trajectory_id, {"model": "x"}))
    assert upstream.calls == []
