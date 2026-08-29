# Sprint Trace — CP-1 immutable build and supply chain

| Field | Value |
|---|---|
| Sprint | `CP-1` |
| Status | `PARTIAL — source/package evidence PASS; container image digest NOT MEASURED` |
| Timestamp UTC | `2026-08-29 08:45:00` |
| Source commit | `d1fad93fbd8a5ca1559be710068a850bf6e375c0` |
| Result commit | `26905ef` |

## Scope

This sprint established reproducible source and Python-package evidence without changing application behavior. Docker, Syft, and Trivy were unavailable in the audit environment, so no container digest or container-native scan is claimed.

## Evidence and verification

The standard isolated PEP 517 build command `python -m build --wheel` successfully built `honest_agent-0.1.0-py3-none-any.whl`. The wheel SHA-256 is recorded in `docs/development/evidence/cp1_20260829/wheel-sha256.txt`. The source commit and requirements hash are recorded in `provenance.json`.

The CycloneDX SBOM and JSON `pip-audit` report are recorded in the CP-1 evidence directory. The dependency scan reported **No known vulnerabilities found** for the pinned requirements. A repository secret scan produced a zero-byte result: no candidate API keys, private keys, or provider credentials were found.

The clean editable-install verification passed **81 tests**, and the project’s deterministic evaluation completed successfully. The generated evidence uses Python 3.12.3.

## Gate decision

CP-1 is **PARTIAL**, not `PASS`, because the immutable container image digest, container scan, and image provenance could not be measured without Docker/Syft/Trivy. The next environment with container tooling must build the Dockerfile, record the immutable image digest, generate image SBOM/provenance, and rerun the scan before CP-1 can be accepted for a pilot.
