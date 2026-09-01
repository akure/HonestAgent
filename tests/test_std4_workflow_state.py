import time

import pytest

from honest_agent.core.workflow_state import DurableWorkflowStateStore, WorkflowState, WorkflowStateError


def _create(store, **overrides):
    values = dict(run_id="run-1", step_id="step-1", attempt=1, intent_hash="intent-a", evidence_snapshot_id="evidence-a", policy_snapshot_id="policy-a", expires_at=time.time() + 30)
    values.update(overrides)
    return store.create(**values)


def test_state_machine_requires_safe_order_and_scopes_approval(tmp_path):
    store = DurableWorkflowStateStore(str(tmp_path / "state.sqlite3"))
    record = _create(store)
    assert record.state is WorkflowState.PROPOSED
    assert store.transition("run-1", "step-1", 1, WorkflowState.EVALUATING).state is WorkflowState.EVALUATING
    assert store.transition("run-1", "step-1", 1, WorkflowState.PAUSED).state is WorkflowState.PAUSED
    with pytest.raises(WorkflowStateError):
        store.approve("run-1", "step-1", 1, reviewer="alice", intent_hash="intent-tampered", evidence_snapshot_id="evidence-a", policy_snapshot_id="policy-a")
    approved = store.approve("run-1", "step-1", 1, reviewer="alice", intent_hash="intent-a", evidence_snapshot_id="evidence-a", policy_snapshot_id="policy-a")
    assert approved.state is WorkflowState.APPROVED
    started = store.consume_for_execution("run-1", "step-1", 1, intent_hash="intent-a", evidence_snapshot_id="evidence-a", policy_snapshot_id="policy-a")
    assert started.state is WorkflowState.EXECUTION_STARTED
    with pytest.raises(WorkflowStateError):
        store.consume_for_execution("run-1", "step-1", 1, intent_hash="intent-a", evidence_snapshot_id="evidence-a", policy_snapshot_id="policy-a")


def test_expired_checkpoint_and_cancelled_step_fail_closed(tmp_path):
    store = DurableWorkflowStateStore(str(tmp_path / "state.sqlite3"))
    _create(store, expires_at=time.time() + 0.02)
    time.sleep(0.04)
    assert store.transition("run-1", "step-1", 1, WorkflowState.EVALUATING).state is WorkflowState.EXPIRED

    cancelled = DurableWorkflowStateStore(str(tmp_path / "cancelled.sqlite3"))
    _create(cancelled)
    assert cancelled.cancel("run-1", "step-1", 1).state is WorkflowState.CANCELLED
    with pytest.raises(WorkflowStateError):
        cancelled.transition("run-1", "step-1", 1, WorkflowState.EVALUATING)


def test_state_survives_store_restart(tmp_path):
    path = str(tmp_path / "restart.sqlite3")
    first = DurableWorkflowStateStore(path)
    _create(first)
    first.transition("run-1", "step-1", 1, WorkflowState.EVALUATING)
    second = DurableWorkflowStateStore(path)
    assert second.get("run-1", "step-1", 1).state is WorkflowState.EVALUATING
