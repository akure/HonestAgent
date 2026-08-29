import asyncio

import pytest

from honest_agent.core.executor import CallableExecutor, ExecutionBlocked
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, EvaluationRequest


def _proceed(tmp_path):
    guard = HonestGuard(Config(trajectory_dir=str(tmp_path / "traces"), checkpoint_path=str(tmp_path / "checkpoints.json")))
    request = EvaluationRequest(context="known", tool_name="lookup", tool_input={"id": 1})
    decision = asyncio.run(guard.evaluate(request))
    return guard, request, decision


def test_callable_executor_validates_before_sync_tool_invocation(tmp_path):
    guard, request, decision = _proceed(tmp_path)
    calls = []
    result = asyncio.run(CallableExecutor(guard).execute(request, decision.trajectory_id, decision.handoff_token, lambda: calls.append("called") or "ok"))
    assert result == "ok"
    assert calls == ["called"]


@pytest.mark.parametrize("token", [None, "bad-token"])
def test_callable_executor_blocks_invalid_handoff_without_invoking_tool(tmp_path, token):
    guard, request, decision = _proceed(tmp_path)
    calls = []
    with pytest.raises(ExecutionBlocked):
        asyncio.run(CallableExecutor(guard).execute(request, decision.trajectory_id, token, lambda: calls.append("called")))
    assert calls == []


def test_callable_executor_blocks_replay_for_altered_payload(tmp_path):
    guard, request, decision = _proceed(tmp_path)
    altered = request.model_copy(update={"tool_input": {"id": 2}})
    calls = []
    with pytest.raises(ExecutionBlocked):
        asyncio.run(CallableExecutor(guard).execute(altered, decision.trajectory_id, decision.handoff_token, lambda: calls.append("called")))
    assert calls == []


def test_callable_executor_supports_async_tools(tmp_path):
    guard, request, decision = _proceed(tmp_path)
    async def tool():
        return "async-ok"
    assert asyncio.run(CallableExecutor(guard).execute(request, decision.trajectory_id, decision.handoff_token, tool)) == "async-ok"
