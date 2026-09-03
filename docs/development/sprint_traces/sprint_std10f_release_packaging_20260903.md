# Sprint Trace — STD-10F Release Packaging Verification

| Field | Value |
|---|---|
| Sprint | STD-10F |
| Objective | Add a reproducible release-input verifier and measure packaging-tool availability without fabricating image, SBOM, or vulnerability results. |
| Date | 2026-09-03 |
| Status | Complete |
| Evidence class | Local synthetic / source-packaging verification |
| Commit | Pending |

## Baseline risk

STD-10E added a deployment manifest boundary but deliberately did not build or scan the Docker image. This environment has no Docker, Podman, Syft, Trivy, Grype, or pip-audit executable. A repeatable command was needed to verify source inputs and report unavailable release evidence explicitly.

## Delivered

Added `honest_agent.ops.release_packaging.verify_release_inputs` and the direct command `python scripts/verify_release_packaging.py`. The verifier checks required release files, computes a deterministic SHA-256 source-manifest hash, checks non-root Dockerfile and dependency-manifest markers, inventories packaging tools, and reports image build, SBOM, and vulnerability scan states as `NOT_RUN` when tools are unavailable. It explicitly reports production readiness, safety certification, and commercial entitlement as false.

## Defect discovered and corrected

The first direct script run failed with `ModuleNotFoundError` because Python did not automatically include the repository root when executing a script from `scripts/`. The script was corrected to add its resolved repository root to `sys.path`. The exact direct command then produced valid JSON and the expected honest unavailable-tool states.

## Verification

| Check | Result |
|---|---|
| STD-10F packaging tests | PASS — 3 tests |
| STD-10E deployment regressions | PASS — 4 tests |
| Combined focused result | PASS — 7 tests |
| Exact offline verifier command | PASS — valid JSON; source hash generated; build/SBOM/scan `NOT_RUN` |
| Docker/Podman availability | NOT AVAILABLE |
| Syft/Trivy/Grype/pip-audit availability | NOT AVAILABLE |
| Full Python regression suite | PASS — 183 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

The verifier does not contact external services, read secret values, or claim a scan that did not run. Managed release claims remain false until target tooling produces evidence. Source-manifest hashing is deterministic and limited to named release inputs. Dockerfile checks are structural markers, not proof of image behavior.

## Limitations

No container build, SBOM generation, vulnerability scan, image signing, registry push, deployment rehearsal, or production evidence was possible or claimed. The source hash is not an image digest. Tool availability is environment-specific and must be rechecked in CI or the target release environment.

## Rollback

Revert the verifier, script, tests, documentation, and changelog entry. The STD-10E deployment manifest validator remains independent.

## Next checkpoint

STD-10G should run real image build, SBOM, signing, and vulnerability evidence only in an environment with approved container and security tooling.
