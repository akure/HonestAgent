# Sprint Trace — EA-4 Ecommerce and Customer Support Policy Packs

| Field | Value |
|---|---|
| Milestone | EA-4 |
| Sprint | Synthetic Ecommerce and Customer Support policy packs |
| Objective | Add declarative refund, account-change, identity, escalation, sensitive-data, and knowledge-freshness boundaries without adding domain branches to the generic kernel. |
| Start UTC | 2026-08-30 14:08:00 |
| End UTC | 2026-08-30 14:10:00 |
| Status | complete |

## Scope

Added synthetic Ecommerce and Customer Support packs, shared README entries, and adversarial tests. Ecommerce covers customer authentication/ownership evidence, quantity and refund caps, idempotency, review for remediation, and payment-capture blocking. Support covers ticket scope, queue allowlisting, knowledge freshness, review for credits and entitlement changes, secret-collection blocking, and account-recovery blocking. Deferred are live commerce/support connectors, payment execution, account identity proofing, production knowledge sources, and deployment-owned stop-condition drills.

## Execution trace

| Order | Task | Action | Result | Evidence |
|---:|---|---|---|---|
| 1 | D5 | implemented | Added synthetic Ecommerce pack with ownership, quantity, refund, address-change, idempotency, review, and payment-capture hard-stop controls. | `examples/domain_packs/ecommerce_operations_synthetic_v1.json` |
| 2 | D6 | implemented | Added synthetic Support pack with customer/ticket scope, queue allowlist, knowledge freshness, remediation review, and secret/account-recovery hard stops. | `examples/domain_packs/customer_support_synthetic_v1.json` |
| 3 | EA-4 | tested | Added deterministic tests for ownership evidence, caps, duplicate prevention, identity scope, stale knowledge, routing, and hard stops. | `tests/test_ea4_ecommerce_support_packs.py` |

## Failures discovered

Initial Ecommerce fixture configuration used `irreversible + prohibited + requires_review=false`, which the approved schema correctly rejects. The fixture was corrected to `reversible + prohibited`, preserving unconditional payment-capture rejection without an internally contradictory rule.

## Decisions and trade-offs

The packs remain DRAFT, synthetic, credential-free, and dry-run only. Customer ownership, identity proof, and knowledge freshness are represented as evidence signals; production systems must supply independently verified evidence. No customer data, payment system, account-recovery system, or support platform is contacted.

## Validation

| Gate | Command or artifact | Result |
|---|---|---|
| Focused | `pytest -q tests/test_ea4_ecommerce_support_packs.py tests/test_ea3_trading_forecasting_packs.py` | PASS — 8 tests |
| Regression | `pytest -q` | PASS — 103 tests |
| Artifact shape | `python -m json.tool examples/domain_packs/ecommerce_operations_synthetic_v1.json` and Support equivalent | PASS |
| Hygiene | `git diff --check` | PASS |

## Git publication

| Commit | Message | Remote status |
|---|---|---|
| `4352e4e` | `feat(domain): add synthetic ecommerce and support packs` | Published on `origin/main` |

## Milestone decision

EA-4 is complete for synthetic configuration and local validation. Proceed to EA-5 only after review. These artifacts do not claim payment, account-recovery, identity, customer-support, or regulatory production readiness.
