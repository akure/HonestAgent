import pytest

from honest_agent.core.policy_registry import PolicyRegistry, PolicyRegistryError
from honest_agent.schemas.models import ActionClass, PolicyRule


def _rules():
    return {"customer_lookup": PolicyRule(action_class=ActionClass.READ_ONLY, requires_review=False, reason="approved read")}


def test_tenant_scope_is_bound_into_signature_and_rejects_cross_tenant_access(tmp_path):
    path = str(tmp_path / "registry.json")
    registry = PolicyRegistry(path, signing_secret="tenant-secret", tenant_id="tenant-a")
    registry.import_policy("v1", _rules(), "importer", tenant_id="tenant-a")
    with pytest.raises(PolicyRegistryError, match="tenant scope"):
        registry.import_policy("v2", _rules(), "importer", tenant_id="tenant-b")
    other_tenant = PolicyRegistry(path, signing_secret="tenant-secret", tenant_id="tenant-b")
    with pytest.raises(PolicyRegistryError, match="tenant scope"):
        other_tenant.get_policy("v1")


def test_importer_cannot_approve_and_approver_cannot_activate(tmp_path):
    registry = PolicyRegistry(str(tmp_path / "registry.json"), approval_quorum=1, tenant_id="tenant-a")
    registry.import_policy("v1", _rules(), "alice")
    with pytest.raises(PolicyRegistryError, match="importer"):
        registry.approve("v1", "alice")
    registry.approve("v1", "reviewer")
    with pytest.raises(PolicyRegistryError, match="activation actor"):
        registry.activate("v1", "reviewer")
    assert registry.activate("v1", "operator").version == "v1"


def test_lifecycle_events_record_simulation_activation_and_tenant(tmp_path):
    registry = PolicyRegistry(
        str(tmp_path / "registry.json"),
        signing_secret="tenant-secret",
        tenant_id="tenant-a",
        require_simulation=True,
    )
    registry.import_policy("v1", _rules(), "alice")
    registry.approve("v1", "reviewer")
    registry.simulate([], "v1")
    registry.activate("v1", "operator")
    events = registry.events()
    assert [event["event"] for event in events] == [
        "POLICY_IMPORTED",
        "POLICY_APPROVED",
        "POLICY_SIMULATED",
        "POLICY_ACTIVATED",
    ]
    assert events[0]["tenant_id"] == "tenant-a"


def test_tampering_with_tenant_scope_invalidates_signature(tmp_path):
    import json

    path = tmp_path / "registry.json"
    registry = PolicyRegistry(str(path), signing_secret="tenant-secret", tenant_id="tenant-a")
    registry.import_policy("v1", _rules(), "alice")
    state = json.loads(path.read_text())
    state["versions"]["v1"]["tenant_id"] = "tenant-b"
    path.write_text(json.dumps(state))
    with pytest.raises(PolicyRegistryError, match="tenant scope"):
        registry.get_policy("v1")
