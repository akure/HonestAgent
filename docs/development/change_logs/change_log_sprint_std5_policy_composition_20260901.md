# Change Log — STD-5 Policy Composition and Delegation Attenuation

| Field | Value |
|---|---|
| Sprint | STD-5 |
| Change type | policy / delegation / workflow safety / test |
| Date | 2026-09-01 |
| Related commit | Pending |
| Evidence class | Local deterministic policy and delegation tests |

## Change

Added `PolicyComposer`, `PolicyLayer`, `EffectivePolicy`, and `EffectiveRule`. The resolver composes platform, tenant, domain, workflow, tool, and step layers without allowing later layers to weaken stricter action or review rules. It computes minimum configured budgets, intersects capability allowlists, records source layers and conflict explanations, and derives a deterministic immutable snapshot ID.

Added `attenuate_child`, which applies the effective snapshot while enforcing tool and budget ceilings before delegating to the existing `WorkflowRunContext.derive_child` checks for parent tools, budgets, tenant, lineage, and deadline.

## Defect discovered and corrected

Effective policy budgets were initially calculated but not applied to child delegation. A focused negative test exposed that a child could request three tool calls against an effective ceiling of two. The helper now validates requested budgets against the effective policy before deriving the child.

## Validation

| Check | Result |
|---|---|
| STD-5 tests | PASS — 3 tests |
| Full regression suite | PASS — 141 tests |
| Snapshot determinism | PASS |
| Strictest-policy selection | PASS |
| Delegation escalation rejection | PASS |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security and limitations

The resolver fails closed on invalid layers, duplicate layer names, empty layer names, unauthorized child tools, and budget escalation. It does not yet provide durable cross-worker policy snapshot storage, distributed identity enforcement, runtime aggregate reservation, or production audit evidence.

## Rollback

Revert the policy composition module, public exports, tests, and documentation. Existing policy and context controls remain available.

## Next action

Implement STD-6 reliable execution semantics and operational controls.
