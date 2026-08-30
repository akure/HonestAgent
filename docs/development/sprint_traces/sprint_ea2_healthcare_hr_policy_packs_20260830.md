# Sprint Trace — EA-2 Healthcare and Recruiting/HR Policy Packs

| Field | Value |
|---|---|
| Milestone | EA-2 |
| Sprint | Synthetic Healthcare and Recruiting/HR policy packs |
| Objective | Provide reviewed synthetic domain configurations that demonstrate industry adaptability without adding domain branches to the generic kernel. |
| Start UTC | 2026-08-30 14:01:00 |
| End UTC | 2026-08-30 14:03:00 |
| Status | complete |

## Scope

Added two source-controlled, credential-free, dry-run policy-pack artifacts and validation tests. Healthcare is limited to clinical-support and healthcare operations; HR is limited to recruiting workflow assistance. Deferred are production regulatory controls, real PHI/candidate data, live system integrations, autonomous clinical or employment decisions, and the remaining four domain packs.

## Execution trace

| Order | Task | Action | Result | Evidence |
|---:|---|---|---|---|
| 1 | D1 | implemented | Added synthetic Healthcare pack with minimum-necessary scope evidence, idempotent scheduling, prohibited PHI export, and prohibited clinical-order action. | `examples/domain_packs/healthcare_operations_synthetic_v1.json` |
| 2 | D3 | implemented | Added synthetic Recruiting/HR pack with consent/source-purpose evidence, idempotent scheduling, review boundaries, and prohibited autonomous employment decisions. | `examples/domain_packs/recruiting_hr_synthetic_v1.json` |
| 3 | EA-2 | documented | Added explicit import/signing instructions and production limitations. | `examples/domain_packs/README.md` |
| 4 | EA-2 | tested | Validated both artifacts against the runtime contract and asserted hard stops. | `tests/test_ea2_domain_packs.py` |

## Failures discovered

Initial artifact fixtures configured prohibited irreversible actions with `requires_review=false`. The approved contract rejects that combination because irreversible actions must require review. Since prohibited actions are unconditional hard stops, the fixtures were corrected to `reversible + prohibited`, preserving the hard stop without an internally contradictory rule.

## Decisions and trade-offs

The artifacts intentionally remain DRAFT and use a non-authoritative zeroed signature placeholder. The registry signs content during import with managed custody; checked-in examples must never be treated as authorization. Both packs use dry-run rollout and synthetic tenant identifiers. No domain name is inspected by `HonestGuard`; the existing generic evaluator consumes the normalized pack.

## Validation

| Gate | Command or artifact | Result |
|---|---|---|
| Unit / integration | `pytest -q tests/test_ea2_domain_packs.py tests/test_ea1_domain_policy_pack.py` | PASS — 7 tests |
| Regression | `pytest -q` | PASS — 94 tests |
| Artifact shape | `python -m json.tool examples/domain_packs/*.json` | PASS |
| Hygiene | `git diff --check` | PASS |

## Git publication

| Commit | Message | Remote status |
|---|---|---|
| `9fb01c3` | `feat(domain): add synthetic healthcare and hr policy packs` | Published on `origin/main` |

## Milestone decision

EA-2 is complete for synthetic configuration examples and local validation. Proceed to EA-3 only after review. EA-3 should implement the next approved domain pack pair or shared validator coverage, while retaining dry-run and no-autonomous-action boundaries.
