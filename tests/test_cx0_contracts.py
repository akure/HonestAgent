import time

import pytest

from honest_agent.schemas.workflow import (
    DataClassification,
    EvidenceEnvelope,
    IntentProvenance,
    SideEffectMode,
    ToolIntent,
    TrustClass,
    WorkflowBudgets,
    WorkflowRunContext,
)


def _context():
    return WorkflowRunContext(run_id="run-1", tenant_id="tenant-a", root_agent_id="agent-a", step_id="step-1", workflow_version="wf-v1", deadline=time.time() + 60, policy_snapshot_id="policy-1", allowed_tools=frozenset({"lookup", "summarize"}))


def test_workflow_child_cannot_escalate_tools_budgets_or_deadline():
    context = _context()
    child = context.derive_child("step-2", WorkflowBudgets(verifier_calls=2, tool_calls=2, retries=1, tokens=1000, fan_out=1, concurrency=1, cumulative_amount=0), allowed_tools=frozenset({"lookup"}), deadline=context.deadline - 1)
    assert child.parent_step_id == "step-1"
    with pytest.raises(ValueError):
        context.derive_child("step-3", WorkflowBudgets(tool_calls=11), allowed_tools=frozenset({"lookup"}))
    with pytest.raises(ValueError):
        context.derive_child("step-4", WorkflowBudgets(), allowed_tools=frozenset({"charge"}))
    with pytest.raises(ValueError):
        context.derive_child("step-5", WorkflowBudgets(), deadline=context.deadline + 1)


def test_tool_intent_hash_is_deterministic_and_changes_on_semantic_mutation():
    first = ToolIntent(tool_name="lookup", argument_schema_version="v1", canonical_arguments={"b": 2, "a": 1}, declared_action_class="read_only", idempotency_key="idem-1", provenance=IntentProvenance.MODEL)
    second = ToolIntent(tool_name="lookup", argument_schema_version="v1", canonical_arguments={"a": 1, "b": 2}, declared_action_class="read_only", idempotency_key="idem-1", provenance=IntentProvenance.MODEL)
    altered = first.model_copy(update={"canonical_arguments": {"a": 2, "b": 2}})
    assert first.canonical_hash() == second.canonical_hash()
    assert first.canonical_hash() != altered.canonical_hash()


def test_authorization_bearing_evidence_requires_trusted_producer_and_redacted_reference():
    now = time.time()
    with pytest.raises(ValueError):
        EvidenceEnvelope(evidence_id="e-1", source_id="source", source_type="retrieval", tenant_scope="tenant-a", content_hash="a" * 64, observed_at=now, trust_class=TrustClass.UNTRUSTED, authorization_bearing=True, redacted_reference="ref")
    evidence = EvidenceEnvelope(evidence_id="e-1", source_id="source", source_type="retrieval", tenant_scope="tenant-a", content_hash="a" * 64, observed_at=now - 1, expires_at=now + 10, trust_class=TrustClass.TRUSTED, data_classification=DataClassification.INTERNAL, authorization_bearing=True, redacted_reference="ref:e-1")
    assert evidence.is_fresh(now)
    assert evidence.redacted_reference == "ref:e-1"


def test_evidence_rejects_raw_or_expired_contracts():
    now = time.time()
    with pytest.raises(ValueError):
        EvidenceEnvelope(evidence_id="e-1", source_id="source", source_type="retrieval", tenant_scope="tenant-a", content_hash="a" * 64, observed_at=now, redacted_reference=None)
    with pytest.raises(ValueError):
        EvidenceEnvelope(evidence_id="e-1", source_id="source", source_type="retrieval", tenant_scope="tenant-a", content_hash="a" * 64, observed_at=now, expires_at=now - 1, redacted_reference="ref:e-1")
    evidence = EvidenceEnvelope(evidence_id="e-2", source_id="source", source_type="retrieval", tenant_scope="tenant-a", content_hash="b" * 64, observed_at=now - 10, expires_at=now - 1, redacted_reference="ref:e-2")
    assert evidence.is_fresh(now) is False


def test_workflow_contract_rejects_unknown_fields():
    with pytest.raises(ValueError):
        WorkflowRunContext.model_validate({**_context().model_dump(), "unexpected": "reject"})
