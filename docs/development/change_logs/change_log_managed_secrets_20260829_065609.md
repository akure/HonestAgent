# Change Log — managed secret configuration and rotation

| Field | Value |
|---|---|
| Change ID | `LR-4` |
| Feature | `Managed secret configuration and rotation` |
| Timestamp UTC | `2026-08-29 06:56:09` |
| Status | `complete` |

## Problem

Handoff signing and reviewer authentication retained development secret defaults in runtime constructors. Without an environment boundary, a staging or production deployment could accidentally run with predictable development credentials, and rotating keys would invalidate already-issued short-lived handoffs or reviewer tokens immediately.

## Change

Added a managed secret configuration loader that reads current secrets and optional previous rotation keys from environment-backed deployment configuration. Staging and production environments, or explicitly managed mode, now fail startup configuration validation when secrets are absent, short, or equal to development defaults. Development retains explicit defaults only when the environment is not managed.

Added current-key issuance and current-or-previous-key validation to both HandoffSigner and ReviewerAuthenticator. This supports overlap during rotation: new credentials are issued with the current key, while short-lived credentials signed by the immediately previous key remain valid until expiry. Added non-reversible 12-character fingerprints for operational identification without exposing secret material. Proxy startup now constructs runtime configuration through the managed loader.

## Live experiment log

| Stage | What was tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Constructor-level development defaults | Existing tests passed, but production startup could silently use predictable secrets | Replaced at runtime startup boundary |
| Iteration 1 | Environment loader with production/staging validation | Missing, short, and development secrets are rejected | Kept |
| Iteration 2 | Current-and-previous validation during rotation | Old handoff and reviewer credentials validate during overlap; new credentials use current key | Kept |
| Iteration 3 | Secret fingerprints instead of raw values in operational identity | Fingerprint tests confirm raw secret values are absent | Kept |

## Safety invariants

| Invariant | Result |
|---|---|
| Managed environments cannot start without non-development secrets | `PASS` |
| Raw secret values are not returned by fingerprints | `PASS` |
| New credentials are always issued with the current key | `PASS` |
| Previous keys are validation-only rotation slots | `PASS` |
| Rotation does not weaken handoff payload binding or reviewer role checks | `PASS` |
| Missing configuration fails closed before serving requests | `PASS` |

## Validation

- `pytest -q`: **49 passed**
- Managed configuration validation: **PASS**
- Handoff key rotation: **PASS**
- Reviewer key rotation: **PASS**
- Secret fingerprint redaction: **PASS**
- `git diff --check`: **PASS**

## Known limitations

The loader currently uses environment-backed injection rather than a cloud-specific secret manager SDK. Deployment wiring to a managed provider, rotation runbooks, and production secret scanning remain deployment-specific hardening work. LR-4 establishes the application contract and prevents development defaults in managed modes.
