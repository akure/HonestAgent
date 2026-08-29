# Change Log — policy contract and registry

| Field | Value |
|---|---|
| Change ID | `HA-M0-001` |
| Change type | `feature` plus safety hardening |
| Milestone / sprint | `M0 / Sprint 1` |
| Timestamp UTC | `2026-08-29 05:48:52` |
| Author | `Honest Agent Contributors` |
| Related tasks | `HA-001`, `HA-002`, `HA-003` |
| Related commit | [`47f40b2`](https://github.com/akure/HonestAgent/commit/47f40b2) |

## Problem

The first prototype carried confidence and verifier data but did not expose an explicit application action class or policy version. Its implicit tool-name conventions were insufficient for a customer-owned policy boundary, and whitespace-only tool names were not rejected consistently.

## Change

Added versioned `ActionClass` and `PolicyRule` contracts, a deterministic `ActionPolicy` registry, policy propagation into guard decisions and trajectories, and documented safety invariants. Unknown actions now fail closed into review unless the application or built-in safe policy explicitly classifies them. The core still never executes customer side effects.

## Files changed

| File | Role | Behavior impact |
|---|---|---|
| `honest_agent/core/policy.py` | Policy implementation | Adds explicit registration and safe unknown-action behavior. |
| `honest_agent/schemas/models.py` | Public contract | Adds action class, policy rule, and policy version fields. |
| `honest_agent/core/guardrail.py` | Decision engine | Propagates policy metadata and rejects invalid tool names. |
| `honest_agent/core/logger.py` | Audit persistence | Persists policy metadata in trajectory steps. |
| `tests/test_m0_contracts.py` | Regression tests | Covers registry, unknown actions, metadata, persistence, and invalid names. |
| `docs/architecture/safety-invariants.md` | Architecture | Documents enforcement and deferred threats. |

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `python3 -m pytest -q` | `PASS` | 20 tests passed. |
| `python3 tests/deep_eval.py` | `PASS` | 40/40 cases correct; 0 false negatives; 0 false positives. |
| Deep evaluation latency | `PASS` | p50 0.186 ms; p95 0.239 ms including local trajectory persistence in the final M0 run. |

## Failure found during implementation

The first M0 evaluation produced one safe-action false positive because the new unknown-action default correctly paused the pure `calculate` fixture, which lacked an explicit safe rule. A whitespace-only tool name also returned `PAUSED` instead of structured rejection. Both were fixed without weakening the unknown-action default: `calculate` is explicitly classified as a pure reversible operation, and blank names are rejected using `strip()`.

## Risk and limitations

The registry is currently in-process and uses a small built-in safe list. It does not yet support durable customer policy storage, payload-bound execution handoffs, authenticated reviewers, or provider-backed verification. Those are launch blockers for real consequential side effects.

## Rollback or mitigation

Revert commit `47f40b2` to return to the prior policy behavior, or configure an explicit application policy for any safe tool that is currently treated as unknown. Do not bypass the guard to resolve a false positive in production.

## Next action

Proceed to M1 only after review of this trace. The next implementation target is durable checkpoint and audit state, beginning with a storage interface and restart-safe pending approvals.
