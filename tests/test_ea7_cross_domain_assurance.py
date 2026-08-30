import json
from pathlib import Path

from honest_agent.domain import DeterministicDomainPolicyEvaluator, DomainPolicyPack, EvaluationOutcome, PackStatus
from honest_agent.schemas.models import EvaluationRequest

PACK_DIR = Path(__file__).parents[1] / "examples" / "domain_packs"
CASES = [
    ("healthcare_operations_synthetic_v1.json", "export_phi"),
    ("recruiting_hr_synthetic_v1.json", "reject_candidate"),
    ("trading_pretrade_synthetic_v1.json", "transfer_settlement"),
    ("forecasting_planning_synthetic_v1.json", "commit_planning_plan"),
    ("ecommerce_operations_synthetic_v1.json", "capture_payment"),
    ("customer_support_synthetic_v1.json", "collect_secret"),
]


def test_all_six_domain_packs_are_opt_in_draft_and_have_hard_stops():
    for filename, prohibited_action in CASES:
        pack = DomainPolicyPack.model_validate(json.loads((PACK_DIR / filename).read_text()))
        assert pack.status == PackStatus.DRAFT
        assert pack.metadata["synthetic"] is True
        assert pack.rollout.dry_run_required is True
        assert pack.actions[prohibited_action].prohibited is True
        finding = DeterministicDomainPolicyEvaluator(pack.model_copy(update={"status": PackStatus.ACTIVE})).evaluate(
            EvaluationRequest(tool_name=prohibited_action, metadata={"tenant_id": pack.tenant_id}), evidence={name: True for name in pack.evidence.required}
        )
        assert finding.outcome == EvaluationOutcome.REJECT


def test_all_domain_packs_reject_wrong_tenant_before_action_evaluation():
    for filename, _ in CASES:
        pack = DomainPolicyPack.model_validate(json.loads((PACK_DIR / filename).read_text()))
        evaluator = DeterministicDomainPolicyEvaluator(pack.model_copy(update={"status": PackStatus.ACTIVE}))
        finding = evaluator.evaluate(EvaluationRequest(tool_name=next(iter(pack.actions)), metadata={"tenant_id": "wrong-tenant"}), evidence={})
        assert finding.reason_codes == ("TENANT_SCOPE_MISMATCH",)
