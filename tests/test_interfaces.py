import asyncio

from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.logger import TrajectoryLogger
from honest_agent.interfaces.mcp_server import verify_context_health
from honest_agent.interfaces.sdk import GuardrailPaused, guard
from honest_agent.schemas.models import DecisionStatus, EvaluationRequest


def test_every_core_evaluation_persists_a_trajectory(tmp_path):
    async def run():
        runtime = HonestGuard()
        decision = await runtime.evaluate(EvaluationRequest(context="Known record.", tool_name="lookup", tool_input={"id": 1}))
        assert decision.trajectory_path
    asyncio.run(run())


def test_approval_updates_persisted_trajectory(tmp_path):
    async def run():
        runtime = HonestGuard()
        pending = await runtime.evaluate(EvaluationRequest(context="Ambiguous maybe unknown.", tool_name="write_file", tool_input={"path": "unknown"}))
        approved = await runtime.approve(pending.trajectory_id, "alice")
        payload = __import__("json").loads(open(approved.trajectory_path).read())
        assert payload["trajectory"][0]["human_checkpoint"]["status"] == "APPROVED"
        assert payload["trajectory"][0]["action_taken"] == "APPROVED_AND_READY_TO_EXECUTE"
    asyncio.run(run())


def test_concurrent_approval_is_single_state_transition():
    async def run():
        runtime = HonestGuard()
        pending = await runtime.evaluate(EvaluationRequest(context="Ambiguous maybe unknown.", tool_name="write_file", tool_input={"path": "unknown"}))
        results = await asyncio.gather(
            runtime.approve(pending.trajectory_id, "alice"),
            runtime.approve(pending.trajectory_id, "alice"),
        )
        assert all(item.status == DecisionStatus.PROCEED for item in results)
        assert results[0].model_dump() == results[1].model_dump()
    asyncio.run(run())


def test_mcp_normalizes_and_returns_trace_fields():
    async def run():
        result = await verify_context_health({"context": "Known record.", "tool_name": "lookup", "tool_input": {"id": 1}})
        assert result["status"] == "PROCEED"
        assert result["verifier_tier"] == "fast"
        assert "trajectory_id" in result
    asyncio.run(run())


def test_sdk_does_not_call_wrapped_function_when_paused():
    calls = []

    @guard(tool_name="write_file")
    def write_file(*, context="", thought=""):
        calls.append(True)
        return "executed"

    try:
        write_file(context="missing dependency maybe unknown", thought="guess")
    except GuardrailPaused:
        pass
    assert calls == []
