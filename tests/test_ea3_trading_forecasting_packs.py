import json
from pathlib import Path

from honest_agent.domain import DeterministicDomainPolicyEvaluator, Domain, DomainPolicyPack, EvaluationOutcome, PackStatus
from honest_agent.schemas.models import EvaluationRequest

PACK_DIR = Path(__file__).parents[1] / "examples" / "domain_packs"


def load(name):
    value = json.loads((PACK_DIR / name).read_text())
    value["status"] = "ACTIVE"
    return DomainPolicyPack.model_validate(value)


def req(pack, tool_name, tool_input, **metadata):
    return EvaluationRequest(tool_name=tool_name, tool_input=tool_input, metadata={"tenant_id": pack.tenant_id, **metadata})


def evidence(**values):
    return {name: {"present": True, "age_seconds": 10} if value is True else value for name, value in values.items()}


def test_trading_pack_blocks_live_submission_and_enforces_caps():
    pack = load("trading_pretrade_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    good = req(pack, "draft_order", {"account_id": "acct-1", "instrument_id": "SYN-1", "side": "BUY", "quantity": 10, "notional": 1000}, idempotency_key="order-1")
    assert evaluator.evaluate(good, evidence=evidence(quote=True, buying_power=True)).outcome == EvaluationOutcome.ALLOW
    over_cap = req(pack, "draft_order", {"account_id": "acct-1", "instrument_id": "SYN-1", "side": "BUY", "quantity": 10001, "notional": 1000}, idempotency_key="order-2")
    assert evaluator.evaluate(over_cap, evidence=evidence(quote=True, buying_power=True)).outcome == EvaluationOutcome.REJECT
    assert evaluator.evaluate(req(pack, "submit_order", {"account_id": "acct-1", "instrument_id": "SYN-1", "quantity": 1, "notional": 1}, idempotency_key="order-3"), evidence=evidence(quote=True, buying_power=True)).outcome == EvaluationOutcome.PAUSE
    assert evaluator.evaluate(req(pack, "transfer_settlement", {}), evidence=evidence(quote=True, buying_power=True)).outcome == EvaluationOutcome.REJECT


def test_trading_pack_rejects_unknown_venue_and_duplicate_prone_missing_key():
    pack = load("trading_pretrade_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    bad_venue = req(pack, "market_data_lookup", {"instrument_id": "SYN-1", "venue": "REAL_MARKET"})
    assert evaluator.evaluate(bad_venue, evidence=evidence(quote=True, buying_power=True)).outcome == EvaluationOutcome.REJECT
    missing_key = req(pack, "draft_order", {"account_id": "acct-1", "instrument_id": "SYN-1", "side": "BUY", "quantity": 1, "notional": 1})
    assert evaluator.evaluate(missing_key, evidence=evidence(quote=True, buying_power=True)).reason_codes == ("IDEMPOTENCY_KEY_REQUIRED",)


def test_forecasting_pack_pauses_stale_or_contradictory_data_and_blocks_commit():
    pack = load("forecasting_planning_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    payload = {"dataset_version": "ds-v1", "horizon": 12}
    assert evaluator.evaluate(req(pack, "generate_forecast", payload), evidence=evidence(dataset_lineage=True, freshness=True)).outcome == EvaluationOutcome.ALLOW
    stale = evidence(dataset_lineage=True, freshness={"present": True, "age_seconds": 61})
    assert evaluator.evaluate(req(pack, "generate_forecast", payload), evidence=stale).outcome == EvaluationOutcome.PAUSE
    contradiction = evidence(dataset_lineage={"present": True, "contradictory": True}, freshness=True)
    assert evaluator.evaluate(req(pack, "generate_forecast", payload), evidence=contradiction).outcome == EvaluationOutcome.REJECT
    commit = req(pack, "commit_planning_plan", {})
    assert evaluator.evaluate(commit, evidence=evidence(dataset_lineage=True, freshness=True)).outcome == EvaluationOutcome.REJECT


def test_forecasting_pack_requires_lineage_and_limits_horizon():
    pack = load("forecasting_planning_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    missing = req(pack, "generate_forecast", {"horizon": 12})
    assert evaluator.evaluate(missing, evidence=evidence(dataset_lineage=True, freshness=True)).outcome == EvaluationOutcome.REJECT
    too_long = req(pack, "generate_forecast", {"dataset_version": "ds-v1", "horizon": 53})
    assert evaluator.evaluate(too_long, evidence=evidence(dataset_lineage=True, freshness=True)).outcome == EvaluationOutcome.REJECT
