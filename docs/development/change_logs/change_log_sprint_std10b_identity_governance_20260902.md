# Change Log — STD-10B Enterprise Identity and Reviewer Governance

| Field | Value |
|---|---|
| Sprint | STD-10B |
| Change type | identity / reviewer governance / tenant authorization / audit attribution |
| Date | 2026-09-02 |
| Related commit | `9ad11ac` |
| Evidence class | Local synthetic / deployment-neutral |

## Change

Added optional tenant-bound reviewer claims, strict expiry validation, subject-level revocation, tenant-aware webhook authentication, and authenticated role/tenant audit attribution. Existing HMAC signature, token revocation, roster revocation, role checks, body-spoof resistance, and redacted hash-chain audit behavior remain intact.

## Validation

| Check | Result |
|---|---|
| STD-10B identity tests | PASS — 5 tests |
| LR-1 authentication regressions | PASS — 6 tests |
| LR-4 secret regressions | PASS — 5 tests |
| Combined focused result | PASS — 16 tests |
| Full suite | PASS — 168 tests |

## Evidence boundary

The result is local synthetic reference evidence. It does not establish production IdP, MFA, centralized roster, distributed revocation, HSM, external immutable audit, customer, regulatory, or safety-certification evidence.

## Rollback

Revert the authentication, webhook, tests, and STD-10B evidence artifacts. Tenant-bound deployments must not silently downgrade to unscoped authentication during rollback.

## Next action

Stage STD-10C immutable audit and evidence retention separately after review.
