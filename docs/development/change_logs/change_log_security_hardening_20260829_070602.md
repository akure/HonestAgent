# Change Log — security review and deployment hardening

| Field | Value |
|---|---|
| Change ID | `LR-7` |
| Feature | `Security review, SSRF controls, payload redaction, and deployment hardening` |
| Timestamp UTC | `2026-08-29 07:06:02` |
| Status | `complete for application-level controls` |

## Problem

The runtime accepted configured upstream URLs without application-level SSRF validation, persisted raw tool payload fields in trajectory logs, and had no explicit deployment validation for private-network access or oversized requests. These gaps could expose metadata endpoints, credentials, or sensitive customer payloads in a pilot deployment.

## Change

Added `validate_outbound_url` to allow only HTTP(S) URLs without embedded credentials and reject localhost, private, loopback, link-local, multicast, unspecified, reserved, and literal special-use addresses unless explicitly allowed. Added recursive sensitive-field redaction for passwords, secrets, tokens, API keys, authorization, cookies, and credentials before trajectory persistence. Added managed deployment validation that rejects private upstream access in staging/production and validates positive payload limits. Proxy routes now reject oversized JSON requests before evaluation or execution, and the upstream client applies SSRF validation at construction.

## Live experiment log

| Stage | What was tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Raw upstream URL construction and raw tool-input persistence | Existing tests passed, but local/private targets and sensitive fields were not explicitly controlled | Replaced at network and logging boundaries |
| Iteration 1 | URL parsing and special-use IP rejection | Localhost, private IP, metadata IP, and embedded-credential URL tests passed | Kept |
| Iteration 2 | Recursive key-based redaction | Nested secret, password, and authorization values are replaced before logging | Kept |
| Iteration 3 | Deployment and payload-size validation | Managed private-network configuration and invalid size are rejected | Kept |
| Test fixture correction | Initial redaction fixture used `credentials` as a container key, which the policy correctly redacted wholesale | Fixture corrected; final suite passes | Kept behavior; confirmed redaction is intentionally conservative |

## Safety invariants

| Invariant | Result |
|---|---|
| Private or special-use literal outbound targets are blocked by default | `PASS` |
| Embedded URL credentials are rejected | `PASS` |
| Sensitive payload fields are redacted before trajectory persistence | `PASS` |
| Oversized requests are rejected before guardrail/executor work | `PASS` |
| Managed deployment cannot enable private upstream access through this boundary | `PASS` |
| Security controls do not alter deterministic policy classification | `PASS` |

## Validation

- `pytest -q`: **67 passed**
- SSRF URL validation: **PASS**
- Upstream constructor enforcement: **PASS**
- Recursive payload redaction: **PASS**
- Trajectory log redaction: **PASS**
- Deployment security validation: **PASS**
- `git diff --check`: **PASS**

## Known limitations

Hostname DNS resolution and DNS-rebinding defenses require deployment-aware egress controls or a resolver policy beyond this local client boundary. The redactor is key-based rather than a full content-level PII detector. Container, network, TLS, dependency, and platform security review remain deployment responsibilities for the final launch decision.
