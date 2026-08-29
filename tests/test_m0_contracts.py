from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.policy import ActionPolicy
from honest_agent.schemas.models import ActionClass, EvaluationRequest, PolicyRule, DecisionStatus


def test_policy_registry_is_explicit_and_versioned():
    policy = ActionPolicy(version="customer-v2")
    policy.register("invoice_lookup", PolicyRule(action_class=ActionClass.READ_ONLY, reason="invoice reads are safe"))
    policy.register("invoice_update", PolicyRule(action_class=ActionClass.REVERSIBLE, requires_review=True, reason="customer policy requires review"))

    read = policy.classify("invoice_lookup")
    update = policy.classify("invoice_update")
    unknown = policy.classify("third_party_action")

    assert read.action_class == ActionClass.READ_ONLY
    assert read.requires_escalation is False
    assert update.action_class == ActionClass.REVERSIBLE
    assert update.requires_escalation is True
    assert unknown.action_class == ActionClass.UNKNOWN
    assert unknown.requires_escalation is True
    assert {read.policy_version, update.policy_version, unknown.policy_version} == {"customer-v2"}


def test_guard_propagates_policy_contract_and_unknown_action_pauses(tmp_path: Path):
    async def run():
        policy = ActionPolicy(version="policy-test-v1")
        guard = HonestGuard(policy=policy)
        decision = await guard.evaluate(EvaluationRequest(context="The request is complete.", tool_name="third_party_action", tool_input={"id": 1}))
        assert decision.status == DecisionStatus.PAUSED
        assert decision.action_class == ActionClass.UNKNOWN
        assert decision.policy_version == "policy-test-v1"
        assert decision.trajectory_path
        payload = Path(decision.trajectory_path).read_text(encoding="utf-8")
        assert '"action_class": "unknown"' in payload
        assert '"policy_version": "policy-test-v1"' in payload

    asyncio.run(run())


@pytest.mark.parametrize("bad", ["", "   "])
def test_empty_tool_names_are_fail_closed(bad: str):
    async def run():
        guard = HonestGuard()
        decision = await guard.evaluate(EvaluationRequest(context="context", tool_name=bad))
        assert decision.status == DecisionStatus.REJECTED

    asyncio.run(run())
