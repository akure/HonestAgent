import asyncio
import time

import pytest

from honest_agent.core.executor import CallableExecutor, ExecutionBlocked
from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.handoff import HandoffError, HandoffSigner
from honest_agent.schemas.models import Config
from honest_agent.schemas.workflow import IntentProvenance, SideEffectMode, ToolIntent, WorkflowRunContext


def _context(**overrides):
    values = dict(run_id="run-2", tenant_id="tenant-a", root_agent_id="agent", step_id="step-1", attempt=1, workflow_version="wf-v1", deadline=time.time() + 60, policy_snapshot_id="policy-v1", allowed_tools=frozenset({"lookup"}))
    values.update(overrides)
    return WorkflowRunContext(**values)


def _intent(**overrides):
    values = dict(tool_name="lookup", argument_schema_version="v1", canonical_arguments={"id": "a-1"}, declared_action_class="read_only", destination="crm", idempotency_key="idem-1", expected_side_effect_mode=SideEffectMode.NONE, provenance=IntentProvenance.MODEL)
    values.update(overrides)
    return ToolIntent(**values)


def test_v2_handoff_binds_all_workflow_and_intent_scope():
    signer = HandoffSigner("cx2-secret", ttl_seconds=30)
    context = _context()
    intent = _intent()
    handoff = signer.issue_v2(context, intent, "evidence-snapshot-1")
    assert signer.validate_v2(handoff.token, context, intent, "evidence-snapshot-1").contract_version == "cx2"
    for changed_context, changed_intent, evidence, destination in [
        (_context(tenant_id="tenant-b"), intent, "evidence-snapshot-1", None),
        (_context(step_id="step-2"), intent, "evidence-snapshot-1", None),
        (_context(attempt=2), intent, "evidence-snapshot-1", None),
        (context, _intent(canonical_arguments={"id": "a-2"}), "evidence-snapshot-1", None),
        (context, intent, "evidence-snapshot-2", None),
        (context, intent, "evidence-snapshot-1", "other-destination"),
    ]:
        with pytest.raises(HandoffError):
            signer.validate_v2(handoff.token, changed_context, changed_intent, evidence, destination)


def test_v2_expiry_is_fail_closed():
    signer = HandoffSigner("cx2-secret", ttl_seconds=1)
    context = _context(deadline=time.time() + 1)
    handoff = signer.issue_v2(context, _intent(), "evidence")
    time.sleep(1.1)
    with pytest.raises(HandoffError):
        signer.validate_v2(handoff.token, context, _intent(), "evidence")


def test_callable_executor_v2_blocks_side_effect_on_invalid_handoff(tmp_path):
    guard = HonestGuard(Config(trajectory_dir=str(tmp_path / "traces"), checkpoint_path=str(tmp_path / "checkpoints.json"), handoff_secret="cx2-secret"))
    executor = CallableExecutor(guard)
    context = _context()
    intent = _intent()
    handoff = guard.signer.issue_v2(context, intent, "evidence")
    calls = []
    assert asyncio.run(executor.execute_v2(context, intent, "evidence", handoff.token, lambda: calls.append("called") or "ok")) == "ok"
    with pytest.raises(ExecutionBlocked):
        asyncio.run(executor.execute_v2(context, _intent(canonical_arguments={"id": "tampered"}), "evidence", handoff.token, lambda: calls.append("called")))
    assert calls == ["called"]
