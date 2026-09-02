# Sprint Trace — STD-10A Enterprise Policy Registry

| Field | Value |
|---|---|
| Sprint | STD-10A |
| Objective | Harden the existing signed policy lifecycle with tenant scope, separation of duties, simulation gating, activation/rollback evidence, and a reviewable audit trail. |
| Date | 2026-09-02 |
| Status | Complete |
| Evidence class | Local synthetic / deployment-neutral |
| Commit | `8ef065d` |

## Baseline risk

The repository already had a signed file-backed policy registry used by the guardrail and launch-readiness work. Its generic lifecycle did not bind tenant identity into the policy signature, did not prevent the importer from approving its own policy, did not prevent an approver from activating it, and did not expose lifecycle events as evidence. These gaps could weaken enterprise governance even though the underlying policy rules were validated.

## Delivered

The existing `honest_agent.core.policy_registry.PolicyRegistry` was tightened without introducing a parallel control plane. The registry now supports optional tenant scoping, includes tenant identity in the signed canonical payload, rejects cross-tenant imports and reads, enforces importer/approver/activation separation of duties, and records `POLICY_IMPORTED`, `POLICY_APPROVED`, `POLICY_SIMULATED`, and `POLICY_ACTIVATED` events. Existing quorum and simulation gates remain fail-closed, and rollback continues to use the same guarded activation path.

## Defect discovered and corrected

The defect was an authorization-boundary omission: tenant identity and lifecycle actor separation were treated as mutable registry metadata rather than enforced controls. The fix binds tenant identity into the HMAC payload, validates it on reads, and rejects actor reuse across lifecycle stages. Regression tests cover tenant mismatch, signature tampering, self-approval, approver activation, and lifecycle evidence.

## Verification

| Check | Result |
|---|---|
| Focused STD-10A, prior registry, and policy-composition tests | PASS — 13 tests |
| Full Python regression suite | PASS — 163 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

Policy content remains signed with HMAC-SHA256. Tenant identity is part of the signed content when configured. Unknown versions, malformed rules, invalid signatures, cross-tenant access, missing quorum, missing simulation, importer self-approval, and approver activation fail closed. Model output, retrieved content, and registry text cannot grant approval or activation authority.

## Limitations

This checkpoint is a local file-backed reference control, not a managed hosted service. It does not evidence production identity-provider integration, key rotation/HSM custody, multi-region durability, immutable external audit storage, customer operations, billing, or safety certification. HMAC signing is suitable for the reference implementation but is not a substitute for an enterprise key-management architecture.

## Rollback

Revert the policy registry implementation, its STD-10A tests, and this evidence documentation. Existing prior policy-registry behavior remains recoverable through Git, but any tenant-scoped records created with the new format should be migrated or discarded rather than silently interpreted as legacy records.

## Next checkpoint

STD-10B should address enterprise identity and reviewer governance in a separately approved, deployment-target-specific checkpoint.
