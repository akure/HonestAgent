# Sprint Trace — B-4 platform security evidence

| Field | Value |
|---|---|
| Sprint | `B-4` |
| Objective | Close application-level DNS rebinding and transport-security gaps without claiming deployment evidence that was not run. |
| Timestamp UTC | `2026-08-29 07:40:00` |
| Status | `partial — application boundary complete; deployment evidence NOT MEASURED` |
| Commit | `bf82340` |

## Baseline risk

The existing SSRF guard rejected literal private addresses but did not resolve hostnames, leaving a DNS-rebinding gap. The upstream client also had no explicit TLS policy at its transport boundary.

## Implementation

1. Added injectable hostname resolution to `validate_outbound_url`; resolved private, loopback, link-local, multicast, reserved, and unspecified addresses fail closed.
2. Added `validate_transport_url` and optional `require_tls` enforcement to `UpstreamClient`.
3. Made managed staging/production configuration reject missing TLS policy.
4. Preserved deterministic offline tests by allowing injected transports to skip live DNS resolution; real clients perform resolution before use.

## Verification matrix

| Case | Expected | Result |
|---|---:|---:|
| Hostname resolves to private address | Blocked before request | PASS |
| Managed deployment without TLS requirement | Configuration error | PASS |
| HTTP upstream with TLS required | Configuration error | PASS |
| Existing SSRF, redaction, and security tests | No regression | PASS |
| Full regression suite | All tests pass | PASS — 74 passed |
| DNS rebinding against target resolver/network policy | Deployment test required | NOT MEASURED |
| Egress firewall and private-network enforcement | Deployment test required | NOT MEASURED |
| TLS certificate trust and rotation | Deployment test required | NOT MEASURED |
| Container/host hardening and vulnerability scan | Deployment/Security required | NOT MEASURED |

## Gate decision

**B-4 remains open for unrestricted production.** The application security boundary is hardened and regression-tested, but the release remains `NO-GO` until the target environment supplies egress, DNS, TLS, container, host, dependency, and vulnerability evidence.

## Next action

Run the deployment security probe in production-like staging, attach the redacted scan outputs and immutable artifact digest, then proceed to B-5 only after the platform owner reviews the results.
