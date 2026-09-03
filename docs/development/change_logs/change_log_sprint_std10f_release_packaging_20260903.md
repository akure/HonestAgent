# Change Log — STD-10F Release Packaging Verification

| Field | Value |
|---|---|
| Sprint | STD-10F |
| Change type | release packaging / provenance / tool availability |
| Date | 2026-09-03 |
| Related commit | Pending |
| Evidence class | Local synthetic / source-packaging verification |

## Change

Added a direct, credential-free release verifier that checks required source inputs, computes a deterministic source-manifest SHA-256, validates Dockerfile non-root and dependency-manifest markers, inventories build/SBOM/scan tools, and emits explicit `NOT_RUN` results when tools are unavailable. Corrected direct script execution by resolving the repository root before importing project modules.

## Validation

| Check | Result |
|---|---|
| STD-10F packaging tests | PASS — 3 tests |
| STD-10E deployment regressions | PASS — 4 tests |
| Combined focused result | PASS — 7 tests |
| Exact verifier command | PASS — valid JSON |
| Docker, Podman, Syft, Trivy, Grype, pip-audit | NOT AVAILABLE in environment |
| Full suite | PASS — 183 tests |

## Evidence boundary

This is local source-packaging evidence. No image build, SBOM, vulnerability scan, image signature, registry, deployment, customer, commercial-entitlement, or safety-certification claim is made.

## Rollback

Revert the verifier, script, tests, and STD-10F evidence files.

## Next action

Run real release tooling in approved CI or target infrastructure before making a release decision.
