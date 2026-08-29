# Change Log — B-4 platform security hardening

| Field | Value |
|---|---|
| Date | `2026-08-29` |
| Blocker | `B-4` |
| Status | `application controls complete; deployment evidence NOT MEASURED` |

## Added

Added DNS-rebinding protection because the prior URL validator accepted a public hostname without checking whether it resolved to a private or link-local address. Added explicit TLS enforcement at the upstream transport boundary because managed deployment configuration must not rely on convention alone. Both checks remain deterministic and fail closed.

## Evidence

The full regression suite passes with 74 tests, including a resolver-injection test proving that a hostname resolving to `192.168.1.10` is blocked, managed-deployment TLS configuration checks, HTTP rejection when TLS is required, and the existing SSRF/redaction suite.

## Limitation

These tests do not prove target-platform firewall, resolver, certificate, container, host, SBOM, or vulnerability posture. B-4 therefore remains `PARTIAL`, and the unrestricted-production decision remains `NO-GO` until deployment evidence is attached.
