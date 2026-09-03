import pytest

from honest_agent.core.reliable_execution import ExecutionError, ExecutionSemantics, IntentStore
from honest_agent.ops.operations import AlertRule, build_operational_dashboard, evaluate_alerts


def _submit(store, tenant="tenant-a", workflow="run-1", tool="charge", key="k-1"):
    return store.submit(tenant, workflow, tool, {"amount": 1}, idempotency_key=key, semantics=ExecutionSemantics.AT_MOST_ONCE)


def test_kill_switch_blocks_claim_and_snapshot_records_authorized_actor(tmp_path):
    store = IntentStore(str(tmp_path / "execution.sqlite3"))
    intent = _submit(store)
    store.set_kill_switch("tenant:tenant-a", enabled=False, actor="ops-alice")
    with pytest.raises(ExecutionError, match="tenant:tenant-a"):
        store.claim(intent.intent_id)
    snapshot = store.operational_snapshot()
    assert snapshot["controls"] == [{"scope": "tenant:tenant-a", "enabled": 0, "quota": None}]
    assert snapshot["control_events"][0]["actor"] == "ops-alice"
    assert snapshot["control_events"][0]["action"] == "ENABLE_KILL_SWITCH"


def test_snapshot_and_alerts_are_read_only_and_threshold_based(tmp_path):
    store = IntentStore(str(tmp_path / "execution.sqlite3"))
    first = _submit(store, key="k-1")
    store.claim(first.intent_id)
    store.fail(first.intent_id, "provider unavailable", retryable=False)
    snapshot = store.operational_snapshot()
    alerts = evaluate_alerts(snapshot, (AlertRule("failed-actions", "FAILED", 1),))
    dashboard = build_operational_dashboard(snapshot, alerts)
    assert alerts[0].severity == "critical"
    assert dashboard["alerts"][0]["name"] == "failed-actions"
    assert store.get(first.intent_id).state.value == "FAILED"


def test_alerts_fail_closed_on_malformed_snapshot_and_rule():
    with pytest.raises(ValueError, match="malformed"):
        evaluate_alerts({"intents": {"by_state": "not-a-map"}})
    with pytest.raises(ValueError, match="positive"):
        evaluate_alerts({"intents": {"by_state": {}}}, (AlertRule("bad", "FAILED", 0),))


def test_control_updates_require_actor_identity(tmp_path):
    store = IntentStore(str(tmp_path / "execution.sqlite3"))
    with pytest.raises(ValueError, match="actor"):
        store.set_kill_switch("global", actor="")
    with pytest.raises(ValueError, match="actor"):
        store.set_quota("global", 2, actor="")
