# Sprint Trace — STD-10G Real Image Build, SBOM, Signing, Vulnerability Scan, and Deployment Rehearsal

| Field | Value |
|---|---|
| Sprint | STD-10G |
| Objective | Verify whether the approved environment can perform real image build, SBOM, signing, vulnerability scanning, and deployment rehearsal; fail closed when prerequisites are unavailable. |
| Date | 2026-09-04 |
| Status | Blocked |
| Evidence class | Local environment capability check |
| Commit | Pending |

## Baseline risk

STD-10F established source-packaging verification but explicitly recorded that release tooling was unavailable. STD-10G requires real container build, SBOM generation, signing, vulnerability scanning, and deployment rehearsal. These actions cannot be honestly simulated as release evidence.

## Delivered

Added `verify_std10g_prerequisites()` and the direct command `python scripts/verify_std10g_gate.py`. The gate inventories Docker/Podman, Syft, Cosign, Trivy/Grype/pip-audit, and kubectl/Helm. It reports capability groups and returns `NO_RELEASE_EXECUTION` whenever any required tool is missing. The gate does not invoke external systems, require credentials, or produce fake artifacts.

## Defect discovered and corrected

No product defect was found. The environment lacks every required STD-10G tool: Docker, Podman, Syft, Cosign, Trivy, Grype, pip-audit, kubectl, and Helm. The implementation closes the process gap by making the blocked state machine-readable and fail-closed.

## Verification

| Check | Result |
|---|---|
| STD-10G gate tests | PASS — 2 tests |
| STD-10F packaging regressions | PASS — 3 tests |
| Combined focused result | PASS — 5 tests |
| Exact prerequisite command | PASS — valid JSON; status `BLOCKED`; action `NO_RELEASE_EXECUTION` |
| Image builder | BLOCKED — Docker and Podman unavailable |
| SBOM generator | BLOCKED — Syft unavailable |
| Image signer | BLOCKED — Cosign unavailable |
| Vulnerability scanner | BLOCKED — Trivy, Grype, and pip-audit unavailable |
| Deployment client | BLOCKED — kubectl and Helm unavailable |
| Real image build | NOT RUN |
| SBOM generation | NOT RUN |
| Signing | NOT RUN |
| Vulnerability scan | NOT RUN |
| Deployment rehearsal | NOT RUN |
| Full Python regression suite | PASS — 185 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

A missing tool never becomes a passing release check. The gate refuses to authorize a partial release workflow. No credentials, registry, cluster, or external deployment target were contacted. No artifact digest, SBOM, signature, vulnerability status, or deployment success is claimed.

## Limitations

STD-10G remains blocked. The repository has no real image, SBOM, signature, vulnerability report, registry evidence, or deployment-rehearsal evidence from this checkpoint. A future run requires an approved CI or target environment with pinned tooling, registry/cluster access, signing-key custody, scan policy, and rollback ownership.

## Unblocking requirements

Install or provision approved versions of a container builder, Syft or equivalent SBOM generator, Cosign or equivalent signer, Trivy/Grype/pip-audit scanner, and kubectl/Helm for the target. Then build from a pinned commit, generate and retain the SBOM, sign the immutable digest, scan both image and dependencies, rehearse deployment and rollback in a production-like environment, and attach signed outputs.

## Rollback

Revert the gate, tests, script, and evidence files. Do not bypass the gate to claim STD-10G completion.

## Next checkpoint

STD-10G must be resumed in an approved tool-enabled environment; no STD-10H should be started until the release gate is either completed with real evidence or formally re-scoped.
