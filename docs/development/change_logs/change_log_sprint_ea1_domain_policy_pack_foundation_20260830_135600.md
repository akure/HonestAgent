# Change Log — Domain Policy-Pack Foundation

| Field | Value |
|---|---|
| Change ID | EA-1 |
| Change type | feature / security / test |
| Milestone / sprint | EA-0 / EA-1 |
| Timestamp UTC | 2026-08-30 13:56:00 |
| Author | HonestAgent development agent |
| Related task | 7YvScDgTHokKogC36QYAFt |
| Related commit | `f1c6cdf` |

## Problem

The generic safety gateway had no declarative, tenant-scoped boundary for industry-specific constraints. Adding domain logic directly to `HonestGuard` would create conditionals, increase prompt-injection and authorization risk, and make policy review difficult.

## Change

Added a closed Pydantic policy-pack contract covering six domain labels, action rules, bounded constraints, data controls, evidence requirements, approval safeguards, limits, rollout settings, and HMAC-SHA256 signatures. Added a deterministic evaluator that fails closed for tenant mismatch, unknown actions, prohibited actions, missing constraints, missing evidence, and missing idempotency keys. Added a file-backed registry with import, approval, activation, retirement, signature verification, and active version lookup. Integrated the evaluator as an optional restrictive gate before verifier execution; it cannot issue a handoff or authorize an action by itself.

## Files changed

| File | Role | Behavior impact |
|---|---|---|
| `honest_agent/domain/policy_pack.py` | implementation | New EA-1 models, evaluator, signing, and lifecycle registry. |
| `honest_agent/domain/__init__.py` | API | Public exports for the domain package. |
| `honest_agent/core/guardrail.py` | integration | Domain `PAUSE`/`REJECT` decisions persist and log before verifier execution. |
| `tests/test_ea1_domain_policy_pack.py` | regression | Covers malformed safety settings, tamper detection, tenant isolation, constraints, evidence, and guard integration. |
| `docs/architecture/domain-policy-pack-schema-ea1_20260830.md` | contract | Marks the approved schema as implemented and links the runtime boundary. |
| `docs/development/sprint_traces/sprint_ea1_domain_policy_pack_foundation_20260830.md` | evidence | Records scope, decisions, validation, and deferred work. |

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `pytest -q` | PASS | 91 tests passed. |
| `pytest -q tests/test_ea1_domain_policy_pack.py tests/test_lr6_policy_registry.py` | PASS | 11 focused tests passed. |
| `python -m compileall -q honest_agent tests/test_ea1_domain_policy_pack.py` | PASS | No syntax errors. |
| `ruff check ...` | NOT RUN | Ruff is unavailable in this environment; no lint result is claimed. |

## Risk and limitations

This is a local file-backed lifecycle, not production-grade distributed registry storage or managed key custody. The `max_age_seconds`, rate-limit, egress, and freshness vocabulary is represented in the contract but requires subsequent runtime services before it can be used as a complete production control. No industry pack is being represented as production-compliant. Local synthetic tests do not establish deployment or regulatory evidence.

## Rollback or mitigation

Do not pass `domain_evaluator` to `HonestGuard` to disable the optional domain gate, or revert the single integration change. Existing generic policy, verifier, handoff, and executor controls remain unchanged. Remove any unactivated registry file if a malformed pack is found; activation always re-verifies the signature.

## Next action

Review EA-1 evidence, then begin EA-2 with synthetic Healthcare and HR pack artifacts and tests only.
