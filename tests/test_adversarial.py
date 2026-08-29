import asyncio

import pytest

from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.verifier import VerifierEngine
from honest_agent.interfaces.mcp_server import verify_context_health
from honest_agent.schemas.models import Config, DecisionStatus, EvaluationRequest, VerifierTier


class ExplodingProvider:
    async def verify(self, request, telemetry, tier):
        raise TimeoutError("provider timeout")


def run(coro):
    return asyncio.run(coro)


def test_benign_tool_names_do_not_escalate_or_block():
    guard = HonestGuard()
    for name in ("runtime_status", "rewrite_summary"):
        decision = run(guard.evaluate(EvaluationRequest(context="Known facts are available.", tool_name=name, tool_input={"id": 1})))
        assert decision.status == DecisionStatus.PROCEED, name
        assert decision.verifier_tier == VerifierTier.FAST, name


def test_safe_input_text_does_not_change_tool_risk():
    guard = HonestGuard()
    decision = run(guard.evaluate(EvaluationRequest(context="Documentation is available.", tool_name="search_docs", tool_input={"query": "how to run a write-safe example"})))
    assert decision.status == DecisionStatus.PROCEED
    assert decision.verifier_tier == VerifierTier.FAST


def test_zero_argument_read_only_tool_is_allowed():
    guard = HonestGuard()
    decision = run(guard.evaluate(EvaluationRequest(context="Health endpoint is read-only.", tool_name="health_check", tool_input={})))
    assert decision.status == DecisionStatus.PROCEED


def test_provider_failure_fails_closed():
    guard = HonestGuard(verifier=VerifierEngine(ExplodingProvider()))
    decision = run(guard.evaluate(EvaluationRequest(context="Known facts.", tool_name="lookup", tool_input={"id": 1})))
    assert decision.status in {DecisionStatus.REJECTED, DecisionStatus.PAUSED}
    assert decision.action_taken != "PROCEEDED"


def test_approval_replay_is_idempotent_and_audit_safe():
    guard = HonestGuard()
    decision = run(guard.evaluate(EvaluationRequest(context="Reviewed migration.", tool_name="db_migrate", tool_input={"version": 1}, irreversible=True)))
    approved = run(guard.approve(decision.trajectory_id, "alice"))
    replay = run(guard.approve(decision.trajectory_id, "alice"))
    assert approved.status == DecisionStatus.PROCEED
    assert replay.status == DecisionStatus.PROCEED
    assert replay.human_checkpoint.reviewer == "alice"


def test_mcp_adapter_returns_normalized_decision():
    result = run(verify_context_health({"context": "Known facts.", "tool_name": "lookup", "tool_input": {"id": 1}}))
    assert result["status"] == "PROCEED"
    assert "confidence_score" in result
    assert "verifier_tier" in result
