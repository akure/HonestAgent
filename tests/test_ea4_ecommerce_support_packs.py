import json
from pathlib import Path

from honest_agent.domain import DeterministicDomainPolicyEvaluator, Domain, DomainPolicyPack, EvaluationOutcome
from honest_agent.schemas.models import EvaluationRequest

PACK_DIR = Path(__file__).parents[1] / "examples" / "domain_packs"


def load(name):
    value = json.loads((PACK_DIR / name).read_text())
    value["status"] = "ACTIVE"
    return DomainPolicyPack.model_validate(value)


def req(pack, tool_name, tool_input, **metadata):
    return EvaluationRequest(tool_name=tool_name, tool_input=tool_input, metadata={"tenant_id": pack.tenant_id, **metadata})


def evidence(**values):
    return {name: {"present": True, "age_seconds": 20} if value is True else value for name, value in values.items()}


def test_ecommerce_pack_enforces_ownership_caps_and_review():
    pack = load("ecommerce_operations_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    good = req(pack, "refund_request", {"order_id": "ord-1", "amount": 50}, idempotency_key="refund-1")
    assert evaluator.evaluate(good, evidence=evidence(customer_auth=True, order_ownership=True)).outcome == EvaluationOutcome.PAUSE
    over_cap = req(pack, "refund_request", {"order_id": "ord-1", "amount": 251}, idempotency_key="refund-2")
    assert evaluator.evaluate(over_cap, evidence=evidence(customer_auth=True, order_ownership=True)).outcome == EvaluationOutcome.REJECT
    missing_owner = req(pack, "order_draft", {"customer_id": "cust-1", "quantity": 1}, idempotency_key="order-1")
    assert evaluator.evaluate(missing_owner, evidence=evidence(customer_auth=True)).outcome == EvaluationOutcome.PAUSE
    assert evaluator.evaluate(req(pack, "capture_payment", {}), evidence=evidence(customer_auth=True, order_ownership=True)).outcome == EvaluationOutcome.REJECT


def test_ecommerce_pack_blocks_duplicate_prone_mutations_and_excessive_discount():
    pack = load("ecommerce_operations_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    no_key = req(pack, "cart_update", {"customer_id": "cust-1", "quantity": 1})
    assert evaluator.evaluate(no_key, evidence=evidence(customer_auth=True, order_ownership=True)).reason_codes == ("IDEMPOTENCY_KEY_REQUIRED",)
    discount = req(pack, "discount_proposal", {"discount_percent": 26})
    assert evaluator.evaluate(discount, evidence=evidence(customer_auth=True, order_ownership=True)).outcome == EvaluationOutcome.REJECT


def test_support_pack_enforces_identity_scope_freshness_and_hard_stops():
    pack = load("customer_support_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    guidance = req(pack, "issue_knowledge_guidance", {"ticket_id": "ticket-1", "source_id": "kb-1"})
    assert evaluator.evaluate(guidance, evidence=evidence(customer_auth=True, ticket_scope=True, knowledge_freshness=True)).outcome == EvaluationOutcome.ALLOW
    stale = evidence(customer_auth=True, ticket_scope=True, knowledge_freshness={"present": True, "age_seconds": 301})
    assert evaluator.evaluate(guidance, evidence=stale).outcome == EvaluationOutcome.PAUSE
    wrong_queue = req(pack, "classify_route_ticket", {"ticket_id": "ticket-1", "queue": "admin"})
    assert evaluator.evaluate(wrong_queue, evidence=evidence(customer_auth=True, ticket_scope=True)).outcome == EvaluationOutcome.REJECT
    assert evaluator.evaluate(req(pack, "collect_secret", {}), evidence=evidence(customer_auth=True, ticket_scope=True)).outcome == EvaluationOutcome.REJECT
    assert evaluator.evaluate(req(pack, "account_recovery", {}), evidence=evidence(customer_auth=True, ticket_scope=True)).outcome == EvaluationOutcome.REJECT


def test_support_pack_requires_review_and_idempotency_for_remediation():
    pack = load("customer_support_synthetic_v1.json")
    evaluator = DeterministicDomainPolicyEvaluator(pack)
    refund = req(pack, "refund_credit_request", {"ticket_id": "ticket-1", "amount": 10}, idempotency_key="credit-1")
    assert evaluator.evaluate(refund, evidence=evidence(customer_auth=True, ticket_scope=True)).outcome == EvaluationOutcome.PAUSE
    missing_key = req(pack, "refund_credit_request", {"ticket_id": "ticket-1", "amount": 10})
    assert evaluator.evaluate(missing_key, evidence=evidence(customer_auth=True, ticket_scope=True)).reason_codes == ("IDEMPOTENCY_KEY_REQUIRED",)
