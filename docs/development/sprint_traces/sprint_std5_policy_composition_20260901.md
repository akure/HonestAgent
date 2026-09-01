# Sprint Trace — STD-5 Policy Composition and Delegation Attenuation

| Field | Value |
|---|---|
| Sprint | STD-5 |
| Objective | Resolve layered policies monotonically and prevent child workflows from escalating authority, tools, budgets, or policy scope. |
| Date | 2026-09-01 |
| Status | Complete |
| Evidence class | Local deterministic policy and delegation tests |
| Commit | Pending |

## Baseline risk

`ActionPolicy` classified one request at a time and `WorkflowRunContext` enforced basic parent-child attenuation. There was no immutable effective-policy snapshot combining platform, tenant, domain, workflow, tool, and step restrictions, and no explicit bridge applying policy ceilings to delegated child contexts.

## Delivered

| Deliverable | Artifact |
|---|---|
| Layered resolver | `honest_agent/core/policy_composition.py` |
| Public exports | `honest_agent/__init__.py` |
| Adversarial tests | `tests/test_std5_policy_composition.py` |

`PolicyComposer` selects the strictest action/review rule, intersects tool allowlists, selects minimum budgets, records layer sources and conflict explanations, and creates a deterministic snapshot ID. `attenuate_child` applies the effective policy snapshot and validates child tools and budgets against both policy and parent constraints.

## Defect discovered and corrected

The first implementation calculated effective minimum budgets but did not enforce them in delegated child creation. A regression requesting three tool calls against an effective ceiling of two exposed the gap. The helper now applies the effective budget ceiling before deriving the child context.

## Verification

| Check | Result |
|---|---|
| STD-5 focused tests | PASS — 3 tests |
| Full regression suite | PASS — 141 tests |
| Strictest rule and review monotonicity | PASS |
| Snapshot determinism | PASS |
| Tool/budget/deadline delegation attenuation | PASS |
| Invalid layer fail-closed behavior | PASS |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

A child cannot add tools, increase budgets, extend a deadline, change tenant scope, or replace the effective policy snapshot. Stricter action class and review requirements win across layers. Effective policy is immutable by value and explainable through its snapshot ID and layer sources.

## Limitations

This checkpoint provides local in-process policy resolution and delegation checks. It does not yet persist policy snapshots to an external registry, enforce identity across distributed workers, implement aggregate runtime reservations under concurrency, or provide production audit-stream evidence.

## Rollback

Revert the additive policy composition module, exports, tests, and documentation. Existing `ActionPolicy` and workflow-context attenuation remain available.

## Next checkpoint

Proceed to **STD-6 — Reliable Execution Semantics and Operational Controls**.
