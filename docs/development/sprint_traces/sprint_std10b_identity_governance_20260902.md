# Sprint Trace — STD-10B Enterprise Identity and Reviewer Governance

| Field | Value |
|---|---|
| Sprint | STD-10B |
| Objective | Add tenant-bound reviewer identity validation, expiry and revocation controls, and authenticated audit attribution without introducing a live IdP dependency. |
| Date | 2026-09-02 |
| Status | Complete |
| Evidence class | Local synthetic / deployment-neutral |
| Commit | Pending |

## Baseline risk

Reviewer authentication already supported HMAC bearer tokens, role checks, roster revocation, token revocation, expiry, and authenticated webhook attribution. It did not bind a reviewer token to a tenant, did not offer subject-level revocation independent of a roster, used a non-strict expiry boundary, and did not expose the authenticated role and tenant context in webhook audit details.

## Delivered

`ReviewerPrincipal` now carries an optional tenant identity. `ReviewerAuthenticator` can require a configured tenant claim, rejects mismatches, rejects tokens at the exact expiry boundary, and supports subject-level revocation in addition to token and roster revocation. The webhook router accepts an optional tenant context, validates it through the authenticator, ignores a spoofed body reviewer when a valid principal is present, and records role/tenant attribution in the redacted append-only audit event.

Existing unscoped deployments and prior API calls remain compatible: tenant enforcement is opt-in and the existing reviewer/admin role model is unchanged.

## Defect discovered and corrected

The defect was an incomplete identity authorization boundary: a valid signed reviewer token was not tenant-bound, and subject revocation required mutating the roster or enumerating individual tokens. The fix adds tenant claim binding, subject revocation, strict expiry comparison, and explicit authenticated audit context. Tests cover wrong-tenant tokens, subject revocation, exact-expiry rejection, roster revocation, body spoofing, and audit-chain verification.

## Verification

| Check | Result |
|---|---|
| STD-10B identity tests | PASS — 5 tests |
| Prior LR-1 authentication tests | PASS — 6 tests |
| Prior LR-4 secret tests | PASS — 5 tests |
| Combined focused result | PASS — 16 tests |
| Full Python regression suite | PASS — 168 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

Invalid schemes, malformed tokens, invalid signatures, expired tokens, revoked tokens, revoked subjects, inactive roster identities, insufficient roles, and tenant mismatches fail closed. The request body cannot override an authenticated principal. Audit events contain the authenticated subject and non-secret role/tenant context; token material and secrets are never logged.

## Limitations

This is deployment-neutral reference evidence. It does not evidence a production OIDC/SAML provider, centralized reviewer directory, MFA, key rotation/HSM custody, distributed revocation propagation, session introspection, or an external immutable audit sink. Those controls remain required before an enterprise pilot is treated as production-ready.

## Rollback

Revert the authentication and webhook changes, the STD-10B tests, and the evidence artifacts. Any tenant-scoped deployment relying on the new claim binding must be migrated deliberately rather than silently downgraded to unscoped validation.

## Next checkpoint

STD-10C should address immutable audit and evidence retention in a separately scoped deployment-target checkpoint.
