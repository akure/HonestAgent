import asyncio

from fastapi.testclient import TestClient

from honest_agent.core.evaluator import ContextEvaluator
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, DecisionStatus, EvaluationRequest
from honest_agent.interfaces.proxy import app


def test_exact_token_count_and_capacity_flag():
    evaluator = ContextEvaluator()
    telemetry = evaluator.evaluate("one two, three!", 4, 0.8)
    assert telemetry.token_count == 5
    assert telemetry.ratio == 1.0
    assert telemetry.near_capacity


def test_ambiguous_action_is_paused():
    async def run():
        guard = HonestGuard()
        decision = await guard.evaluate(EvaluationRequest(context="missing dependency; maybe unknown", tool_name="write_file", tool_input={"path": "unknown"}))
        assert decision.status == DecisionStatus.PAUSED
        assert decision.trajectory_id in guard.pending
    asyncio.run(run())


def test_approval_resumes_without_reverification():
    async def run():
        guard = HonestGuard()
        decision = await guard.evaluate(EvaluationRequest(context="reviewed migration", tool_name="db_migrate", tool_input={"version": 1}, irreversible=True))
        approved = await guard.approve(decision.trajectory_id, "alice")
        assert approved.status == DecisionStatus.PROCEED
        assert approved.human_checkpoint.reviewer == "alice"
    asyncio.run(run())


def test_cap_is_enforced():
    async def run():
        guard = HonestGuard(Config(max_checks=1))
        request = EvaluationRequest(context="known", tool_name="lookup", tool_input={"id": 1})
        assert (await guard.evaluate(request)).status == DecisionStatus.PROCEED
        assert (await guard.evaluate(request)).status == DecisionStatus.CAP_EXCEEDED
    asyncio.run(run())


def test_proxy_health_and_paused_shape():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/v1/guard", json={"context": "missing maybe", "tool_name": "write_file", "tool_input": {"path": "unknown"}})
    assert response.status_code == 200
    assert response.json()["decision"]["status"] == "PAUSED"
