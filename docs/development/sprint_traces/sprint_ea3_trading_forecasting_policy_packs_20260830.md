# Sprint Trace — EA-3 Trading and Forecasting Policy Packs

| Field | Value |
|---|---|
| Milestone | EA-3 |
| Sprint | Synthetic Trading and Forecasting policy packs |
| Objective | Add declarative pre-trade and forecast-planning controls while keeping live execution and committed plans outside HonestAgent. |
| Start UTC | 2026-08-30 14:05:00 |
| End UTC | 2026-08-30 14:07:00 |
| Status | complete |

## Scope

Added synthetic Trading and Forecasting packs, shared generic evaluator semantics for stale and contradictory evidence, numeric caps, allowed values, required lineage, idempotency, review, and prohibited actions, plus adversarial tests. Deferred are live brokerage/market integrations, investment advice, automatic plan commitment, production data lineage, distributed rate-limit state, and deployment-owned kill-switch drills.

## Execution trace

| Order | Task | Action | Result | Evidence |
|---:|---|---|---|---|
| 1 | EA-3 kernel | implemented | Added domain-neutral stale-evidence pause, contradictory-evidence rejection, and bounded age constraint handling. | `honest_agent/domain/policy_pack.py` |
| 2 | D2 | implemented | Added synthetic pre-trade pack with venue, account, side, quantity, notional, idempotency, review, and settlement hard stops. | `examples/domain_packs/trading_pretrade_synthetic_v1.json` |
| 3 | D4 | implemented | Added synthetic forecast pack with dataset version/lineage, horizon cap, freshness, review, and committed-plan hard stop. | `examples/domain_packs/forecasting_planning_synthetic_v1.json` |
| 4 | EA-3 | tested | Added stale, contradictory, cap, replay, scope, and hard-stop tests. | `tests/test_ea3_trading_forecasting_packs.py` |

## Failures discovered

Initial Forecasting fixture configuration used `irreversible + prohibited + requires_review=false`, which the approved schema correctly rejects. The fixture was corrected to `reversible + prohibited`, preserving unconditional rejection without a contradictory rule.

## Decisions and trade-offs

Freshness and contradiction handling were added to the generic evaluator rather than implemented as trading or forecasting branches. Evidence values may carry synthetic `age_seconds` and `contradictory` markers; production provenance and timestamps require a deployment-owned evidence service. The packs remain DRAFT with placeholder signatures and dry-run rollout. No test calls a live market, brokerage, planning system, or external API.

## Validation

| Gate | Command or artifact | Result |
|---|---|---|
| Focused | `pytest -q tests/test_ea3_trading_forecasting_packs.py tests/test_ea2_domain_packs.py tests/test_ea1_domain_policy_pack.py` | PASS — 11 tests |
| Regression | `pytest -q` | PASS — 99 tests |
| Artifact shape | `python -m json.tool examples/domain_packs/*_synthetic_v1.json` | PASS |
| Hygiene | `git diff --check` | PASS |

## Git publication

| Commit | Message | Remote status |
|---|---|---|
| Pending | `feat(domain): add synthetic trading and forecasting packs` | Pending commit and push |

## Milestone decision

EA-3 is complete for synthetic pre-trade and forecast-planning configuration and local tests. Proceed to EA-4 only after review. No production trading, investment-advice, or planning-commitment claim is supported by this sprint.
