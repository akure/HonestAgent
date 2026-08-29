# Change Log — CP-1 immutable build and supply chain

| Field | Value |
|---|---|
| Sprint | `CP-1` |
| Date | `2026-08-29` |
| Change type | Evidence generation and release-readiness documentation |
| Application feature change | None |
| Status | `PARTIAL` |

## Work completed

Generated a reproducible Python wheel, provenance manifest, CycloneDX SBOM, JSON dependency audit, and repository secret-scan artifact. The clean PEP 517 build passed, `pip-audit` reported no known vulnerabilities, and the clean editable-install test suite passed 81 tests.

## Finding during execution

The first build attempt used `--no-isolation` without Hatchling installed and failed with `BackendUnavailable: Cannot import hatchling.build`. This was a build-command issue, not a source defect. Re-running with the standard isolated PEP 517 command installed the declared Hatchling backend and passed.

## Evidence limitation

Docker, Syft, and Trivy are unavailable in the current environment. Therefore, container image digest, image SBOM, image scan, and container provenance remain `NOT MEASURED`. No `PASS` claim is made for those controls.
