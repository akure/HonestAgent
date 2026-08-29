# Change Log — reviewer authentication

| Field | Value |
|---|---|
| Change ID | `LR-1` |
| Feature | `Authenticated reviewer identity` |
| Timestamp UTC | `2026-08-29 06:36:24` |
| Related sprint trace | `sprint_lr1_20260829_063624.md` |
| Status | `complete` |

## Problem

Reviewer approval and rejection endpoints accepted a caller-provided reviewer name without an authenticated identity boundary. This allowed attribution spoofing and provided no production-mode distinction between authenticated and development-only operation.

## Change

Added a signed bearer-token reviewer authenticator using HMAC-SHA256, with subject, role, and expiration claims. The webhook boundary now returns `401` for missing, malformed, invalid, or expired credentials and `403` for insufficient reviewer roles. When authentication is enabled, the authenticated subject overrides the request-body reviewer field and is persisted as the audit attribution. Admins may perform reviewer operations. Development compatibility remains explicit through `require_reviewer_auth=False`; production configuration rejects development secrets when authentication is required.

Added configuration for reviewer secret, required-auth mode, and token lifetime. Added regression tests covering missing credentials, expiry, invalid authorization, unauthorized roles, identity binding, and persisted audit attribution.

## Safety invariants

| Invariant | Result |
|---|---|
| Fail closed when required authentication is missing or invalid | `PASS` |
| No reviewer identity taken from untrusted body when auth is enabled | `PASS` |
| Core evaluation remains side-effect free apart from existing trajectory persistence | `PASS` |
| Approval/rejection remains an explicit post-evaluation operation | `PASS` |
| Existing development integrations remain compatible only when explicitly configured | `PASS` |

## Validation

- `pytest -q`: **35 passed**
- `git diff --check`: **PASS**

## Known limitations

The current authenticator is intentionally a local HMAC boundary for the MVP-to-pilot transition. Secret injection, rotation, and managed storage are reserved for LR-4. Token issuance is not exposed as an application endpoint; deployment-specific identity-provider integration remains a later hardening concern.
