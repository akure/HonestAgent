# Change Log — STD-10A Enterprise Policy Registry

| Field | Value |
|---|---|
| Sprint | STD-10A |
| Change type | policy registry / tenant isolation / governance |
| Date | 2026-09-02 |
| Related commit | Pending |
| Evidence class | Local synthetic / deployment-neutral |

## Change

Hardened the existing signed policy registry rather than adding a second control plane. Tenant scope is validated and included in the HMAC canonical payload; importer self-approval and approver activation are rejected when separation of duties is enabled; lifecycle events are persisted for import, approval, simulation, and activation. Existing quorum, simulation, signature, and rollback behavior remains fail-closed.

## Validation

| Check | Result |
|---|---|
| STD-10A focused tests | PASS — 4 tests |
| Prior policy-registry regressions | PASS — 6 tests |
| Policy-composition regressions | PASS — 3 tests |
| Combined focused result | PASS — 13 tests |
| Full suite | Pending final run |

## Evidence boundary

The result is local synthetic reference evidence. It does not establish managed-service, production IAM, external immutable-audit, key-management, recovery, customer, regulatory, billing, or safety-certification evidence.

## Rollback

Revert the registry implementation, tests, and STD-10A evidence files. Do not silently reuse new tenant-scoped records with an older registry implementation.

## Next action

Stage STD-10B identity and reviewer governance separately after review of this checkpoint.
