# Sprint Trace — EA-0 / EA-1 Domain Policy-Pack Foundation

| Field | Value |
|---|---|
| Milestone | EA-0 / EA-1 |
| Sprint | Domain Policy-Pack Foundation |
| Objective | Add a generic, tenant-scoped, declarative policy-pack boundary without weakening the core safety kernel. |
| Start UTC | 2026-08-30 13:50:00 |
| End UTC | 2026-08-30 13:56:00 |
| Status | complete |

## Scope

Implemented the approved Pydantic contract, bounded deterministic constraint evaluator, HMAC-SHA256 integrity boundary, file-backed tenant/version lifecycle, and an optional additional gate in `HonestGuard`. Explicitly deferred are the six populated industry packs, production key custody, IdP integration, distributed registry concurrency, evidence freshness service, rate-limit state, and framework examples; these belong to subsequent EA sprints.

## Execution trace

| Order | Task | Action | Result | Evidence |
|---:|---|---|---|---|
| 1 | EA-0 | implemented | Added domain-neutral models with closed schemas, tenant scope, irreversible-review invariant, mandatory kill-switch and dry-run safeguards. | `honest_agent/domain/policy_pack.py` |
| 2 | EA-1 | implemented | Added deterministic `ALLOW` / `PAUSE` / `REJECT` evaluator for action, tenant, evidence, idempotency, and bounded constraints. | `DeterministicDomainPolicyEvaluator` |
| 3 | EA-1 | implemented | Added signed import, approval, activation, retirement, tamper verification, and active-pack lookup. | `DomainPolicyRegistry` |
| 4 | EA-1 | integrated | Added domain findings as a second gate before verifier/execution; rejects and pauses are persisted and logged. | `honest_agent/core/guardrail.py` |
| 5 | EA-1 | tested | Added adversarial schema, signature, tenant-isolation, prohibited-action, and guard-integration tests. | `tests/test_ea1_domain_policy_pack.py` |

## Failures discovered

The first focused test run exposed fixture errors: a prohibited action was incorrectly configured as review-authorized, and an empty payload was replaced by the fixture default. Both were test-fixture defects, not runtime findings, and were corrected before the passing run.

## Decisions and trade-offs

The implementation uses a deliberately small constraint vocabulary and no expression evaluation, callbacks, model calls, network calls, or executable policy content. Pack status is registry-controlled metadata and excluded from the content signature so activation and retirement do not invalidate a signed artifact. The domain evaluator is intentionally additive: the existing generic `ActionPolicy`, verifier, handoff signer, and executor boundary remain authoritative. A pack can make a request stricter but cannot authorize an action that the generic kernel would not authorize.

## Validation

| Gate | Command or artifact | Result |
|---|---|---|
| Unit / integration | `pytest -q` | PASS — 91 tests |
| Adversarial | `pytest -q tests/test_ea1_domain_policy_pack.py tests/test_lr6_policy_registry.py` | PASS — 11 tests |
| Compilation | `python -m compileall -q honest_agent tests/test_ea1_domain_policy_pack.py` | PASS |
| Security / hygiene | `ruff check ...` | NOT RUN — Ruff is not installed in the environment; no result is claimed |

## Git publication

| Commit | Message | Remote status |
|---|---|---|
| `f1c6cdf` | `feat(domain): add signed tenant-scoped policy-pack foundation` | Published on `origin/main` |

## Milestone decision

EA-0 and EA-1 are complete for the approved foundation boundary. Proceed to EA-2 only after review of this trace. EA-2 must add synthetic Healthcare and HR packs as data artifacts plus domain-specific regression cases; it must not add domain conditionals to `HonestGuard`.
