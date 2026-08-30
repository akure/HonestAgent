import asyncio
import json

import pytest

from honest_agent.core.guardrail import HonestGuard
from honest_agent.domain import (
    ActionRule,
    Constraint,
    ConstraintType,
    DataControls,
    DeterministicDomainPolicyEvaluator,
    Domain,
    DomainPolicyError,
    DomainPolicyPack,
    DomainPolicyRegistry,
    EvaluationOutcome,
    EvidencePolicy,
    Limits,
    PackStatus,
    RolloutPolicy,
)
from honest_agent.schemas.models import ActionClass, Config, EvaluationRequest


def make_pack(status=PackStatus.DRAFT):
    return DomainPolicyPack(
        schema_version="1.0",
        pack_id="healthcare-safety",
        pack_version="v1",
        tenant_id="tenant-a",
        domain=Domain.HEALTHCARE,
        policy_version="health-v1",
        status=status,
        actions={
            "read_patient": ActionRule(
                action_class=ActionClass.READ_ONLY,
                requires_review=False,
                prohibited=False,
                reason_code="PATIENT_READ_ALLOWED",
                constraints=[Constraint(type=ConstraintType.REQUIRED_FIELDS, field="patient_id")],
            ),
            "delete_patient": ActionRule(
                action_class=ActionClass.REVERSIBLE,
                requires_review=False,
                prohibited=True,
                reason_code="PATIENT_DELETE_PROHIBITED",
            ),
        },
        data_controls=DataControls(
            default_classification="regulated",
            allowed_egress_classes=["regulated"],
            redact_fields=["patient_id"],
            retention_seconds=3600,
        ),
        evidence=EvidencePolicy(required=["authorization"], max_age_seconds=300),
        approval={"required_for_irreversible": True, "quorum": 1, "allowed_roles": ["clinician"]},
        limits={"max_action_rate_per_minute": 10, "max_concurrent_actions": 2, "kill_switch_required": True},
        rollout=RolloutPolicy(mode="pilot", canary_percent=10, dry_run_required=True, stop_conditions=["error_rate"]),
        signature={"algorithm": "HMAC-SHA256", "key_id": "managed", "value": "0" * 64, "signed_fields": ["pack_id"]},
    )


def request(tool_name="read_patient", tool_input=None, **kwargs):
    payload = {"patient_id": "synthetic-1"} if tool_input is None else tool_input
    return EvaluationRequest(tool_name=tool_name, tool_input=payload, metadata={"tenant_id": "tenant-a", **kwargs})


def test_schema_rejects_unsafe_defaults_and_unknown_fields():
    with pytest.raises(ValueError):
        DomainPolicyPack.model_validate({**make_pack().model_dump(), "actions": {"x": {"action_class": "irreversible", "requires_review": False, "prohibited": False, "reason_code": "BAD_RULE"}}})
    with pytest.raises(ValueError):
        DataControls(default_classification="regulated", allowed_egress_classes=[], retention_seconds=1)


def test_registry_signs_approves_activates_and_rejects_tampering(tmp_path):
    registry = DomainPolicyRegistry(str(tmp_path / "packs.json"), signing_secret="managed-secret")
    registry.import_pack(make_pack(), "importer")
    registry.approve("tenant-a", "healthcare-safety", "v1", "reviewer")
    active = registry.activate("tenant-a", "healthcare-safety", "v1", "operator")
    assert active.status == PackStatus.ACTIVE
    assert registry.get_active("tenant-a", "healthcare-safety").pack_version == "v1"

    state = json.loads((tmp_path / "packs.json").read_text())
    state["packs"]["tenant-a:healthcare-safety:v1"]["actions"]["read_patient"]["reason_code"] = "TAMPERED"
    (tmp_path / "packs.json").write_text(json.dumps(state))
    restarted = DomainPolicyRegistry(str(tmp_path / "packs.json"), signing_secret="managed-secret")
    with pytest.raises(DomainPolicyError, match="signature"):
        restarted.get_active("tenant-a", "healthcare-safety")


def test_evaluator_is_deterministic_and_fail_closed():
    pack = make_pack(PackStatus.ACTIVE)
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    assert evaluator.evaluate(request(), evidence={"authorization": "synthetic"}).outcome == EvaluationOutcome.ALLOW
    assert evaluator.evaluate(request(), evidence={}).outcome == EvaluationOutcome.PAUSE
    assert evaluator.evaluate(request(tool_input={}), evidence={"authorization": "synthetic"}).outcome == EvaluationOutcome.REJECT
    assert evaluator.evaluate(request(tool_name="unknown"), evidence={"authorization": "synthetic"}).outcome == EvaluationOutcome.REJECT
    assert evaluator.evaluate(EvaluationRequest(tool_name="read_patient"), evidence={"authorization": "synthetic"}).reason_codes == ("TENANT_SCOPE_MISMATCH",)
    assert evaluator.evaluate(request(tool_name="delete_patient"), evidence={"authorization": "synthetic"}).outcome == EvaluationOutcome.REJECT
    assert evaluator.evaluate(request(), evidence="untrusted-string").reason_codes == ("MALFORMED_EVIDENCE",)


def test_guard_stops_domain_rejection_before_verifier(tmp_path):
    registry = DomainPolicyRegistry(str(tmp_path / "packs.json"), signing_secret="managed-secret")
    registry.import_pack(make_pack(), "importer")
    registry.approve("tenant-a", "healthcare-safety", "v1", "reviewer")
    registry.activate("tenant-a", "healthcare-safety", "v1", "operator")
    guard = HonestGuard(
        Config(trajectory_dir=str(tmp_path / "traces"), checkpoint_path=str(tmp_path / "checkpoints.json")),
        domain_evaluator=registry.evaluator("tenant-a", "healthcare-safety"),
    )
    decision = asyncio.run(guard.evaluate(request(tool_name="delete_patient", evidence={"authorization": "synthetic"})))
    assert decision.status.value == "REJECTED"
    assert decision.action_taken == "REJECTED_DOMAIN_POLICY"
    assert "PATIENT_DELETE_PROHIBITED" in decision.reasoning


def test_registry_requires_managed_secret():
    with pytest.raises(DomainPolicyError):
        DomainPolicyRegistry("/tmp/unused-domain-packs.json", signing_secret="development-secret")
