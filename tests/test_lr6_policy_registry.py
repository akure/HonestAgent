import asyncio

import pytest

from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.policy_registry import PolicyRegistry, PolicyRegistryError
from honest_agent.schemas.models import ActionClass, Config, EvaluationRequest, PolicyRule


def _rules(requires_review=False):
    return {"customer_lookup": PolicyRule(action_class=ActionClass.READ_ONLY, requires_review=requires_review, reason="customer-approved rule")}


def test_policy_import_requires_valid_identity_and_rules(tmp_path):
    registry = PolicyRegistry(str(tmp_path / "registry.json"))
    with pytest.raises(PolicyRegistryError):
        registry.import_policy("v1", {}, "alice")
    with pytest.raises(PolicyRegistryError):
        registry.import_policy("v1", _rules(), "")
    with pytest.raises(PolicyRegistryError):
        registry.import_policy("unsafe version", _rules(), "alice")


def test_policy_requires_approval_before_activation_and_persists(tmp_path):
    path = str(tmp_path / "registry.json")
    registry = PolicyRegistry(path)
    registry.import_policy("customer-v1", _rules(requires_review=True), "alice")
    with pytest.raises(PolicyRegistryError):
        registry.activate("customer-v1", "alice")
    registry.approve("customer-v1", "reviewer-1")
    active = registry.activate("customer-v1", "ops-1")
    assert active.version == "customer-v1"
    restarted = PolicyRegistry(path)
    assert restarted.active_version == "customer-v1"
    assert restarted.get_policy().classify("customer_lookup").requires_escalation is True


def test_simulation_previews_policy_without_activation_or_side_effect(tmp_path):
    registry = PolicyRegistry(str(tmp_path / "registry.json"))
    registry.import_policy("customer-v1", _rules(requires_review=True), "alice")
    request = EvaluationRequest(context="known", tool_name="customer_lookup", tool_input={"id": 1})
    simulation = registry.simulate([request], "customer-v1")
    assert simulation.rows[0].would_execute is False
    assert simulation.rows[0].policy_version == "customer-v1"
    assert registry.active_version == "default-v1"


def test_guard_activation_and_rollback_change_runtime_policy(tmp_path):
    registry = PolicyRegistry(str(tmp_path / "registry.json"))
    registry.import_policy("customer-v1", _rules(requires_review=True), "alice")
    registry.approve("customer-v1", "reviewer-1")
    registry.import_policy("customer-v2", _rules(requires_review=False), "alice")
    registry.approve("customer-v2", "reviewer-1")
    guard = HonestGuard(Config(trajectory_dir=str(tmp_path / "traces"), checkpoint_path=str(tmp_path / "checkpoints.json")), policy_registry=registry)
    guard.activate_policy("customer-v1", "ops-1")
    request = EvaluationRequest(context="known", tool_name="customer_lookup", tool_input={"id": 1})
    first = asyncio.run(guard.evaluate(request))
    assert first.policy_version == "customer-v1"
    guard.activate_policy("customer-v2", "ops-1")
    second = asyncio.run(guard.evaluate(request))
    assert second.policy_version == "customer-v2"
    guard.rollback_policy("customer-v1", "ops-1")
    third = asyncio.run(guard.evaluate(request))
    assert third.policy_version == "customer-v1"
