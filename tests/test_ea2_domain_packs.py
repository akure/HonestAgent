import json
from pathlib import Path

from honest_agent.domain import Domain, DomainPolicyPack, PackStatus

PACK_DIR = Path(__file__).parents[1] / "examples" / "domain_packs"


def load(name):
    return DomainPolicyPack.model_validate(json.loads((PACK_DIR / name).read_text()))


def test_synthetic_healthcare_pack_is_dry_run_and_blocks_clinical_execution():
    pack = load("healthcare_operations_synthetic_v1.json")
    assert pack.domain == Domain.HEALTHCARE
    assert pack.status == PackStatus.DRAFT
    assert pack.rollout.mode == "dry_run"
    assert pack.metadata["synthetic"] is True
    assert pack.actions["export_phi"].prohibited is True
    assert pack.actions["place_clinical_order"].prohibited is True
    assert pack.evidence.required == ["authorization", "purpose_of_use"]


def test_synthetic_hr_pack_blocks_autonomous_employment_decisions():
    pack = load("recruiting_hr_synthetic_v1.json")
    assert pack.domain == Domain.RECRUITING_HR
    assert pack.status == PackStatus.DRAFT
    assert pack.rollout.dry_run_required is True
    assert pack.actions["reject_candidate"].prohibited is True
    assert pack.actions["make_hiring_decision"].prohibited is True
    assert pack.actions["schedule_interview"].idempotency_required is True
    assert pack.evidence.required == ["candidate_consent", "source_purpose"]
