import time

import pytest

from honest_agent import EffectivePolicy, PolicyCompositionError, PolicyComposer, PolicyLayer
from honest_agent.schemas.models import ActionClass, PolicyRule
from honest_agent.schemas.workflow import WorkflowBudgets, WorkflowRunContext


def _context():
    return WorkflowRunContext(run_id="run-std5", tenant_id="tenant-a", root_agent_id="agent", step_id="root", workflow_version="v1", deadline=time.time() + 60, policy_snapshot_id="base", allowed_tools=frozenset({"lookup", "charge"}))


def test_stricter_layer_wins_and_snapshot_is_deterministic():
    layers = [
        PolicyLayer("platform", {"charge": PolicyRule(action_class=ActionClass.REVERSIBLE, reason="platform")}, allowed_tools=frozenset({"lookup", "charge"}), budgets=WorkflowBudgets(tool_calls=8, retries=2)),
        PolicyLayer("tenant", {"charge": PolicyRule(action_class=ActionClass.IRREVERSIBLE, requires_review=True, reason="tenant review")}, allowed_tools=frozenset({"lookup"}), budgets=WorkflowBudgets(tool_calls=5, retries=1)),
    ]
    policy = PolicyComposer().resolve(layers)
    again = PolicyComposer().resolve(layers)
    assert isinstance(policy, EffectivePolicy)
    assert policy.snapshot_id == again.snapshot_id
    assert policy.rule_for("charge").rule.action_class is ActionClass.IRREVERSIBLE
    assert policy.rule_for("charge").rule.requires_review is True
    assert policy.allowed_tools == frozenset({"lookup"})
    assert policy.budgets.tool_calls == 5
    assert "strictest rule" in policy.rule_for("charge").conflict_reason


def test_child_delegation_cannot_add_tool_raise_budget_or_change_policy_scope():
    policy = PolicyComposer().resolve([PolicyLayer("tenant", {"lookup": PolicyRule(action_class=ActionClass.READ_ONLY)}, allowed_tools=frozenset({"lookup"}), budgets=WorkflowBudgets(tool_calls=2))])
    composer = PolicyComposer()
    parent = _context()
    child = composer.attenuate_child(parent, policy, "child-1", WorkflowBudgets(tool_calls=1, retries=0, verifier_calls=0, tokens=1000, fan_out=1, concurrency=1, cumulative_amount=0), allowed_tools=frozenset({"lookup"}))
    assert child.allowed_tools == frozenset({"lookup"})
    assert child.policy_snapshot_id == policy.snapshot_id
    with pytest.raises(PolicyCompositionError):
        composer.attenuate_child(parent, policy, "child-2", WorkflowBudgets(tool_calls=1), allowed_tools=frozenset({"charge"}))
    with pytest.raises(ValueError):
        composer.attenuate_child(parent, policy, "child-3", WorkflowBudgets(tool_calls=3), allowed_tools=frozenset({"lookup"}))


def test_invalid_layers_fail_closed():
    composer = PolicyComposer()
    with pytest.raises(PolicyCompositionError):
        composer.resolve([])
    with pytest.raises(PolicyCompositionError):
        composer.resolve([PolicyLayer("", {})])
    with pytest.raises(PolicyCompositionError):
        composer.resolve([PolicyLayer("same", {}), PolicyLayer("same", {})])
