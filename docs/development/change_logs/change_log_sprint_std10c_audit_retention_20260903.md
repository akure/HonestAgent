# Change Log — STD-10C Immutable Audit and Evidence Retention

| Field | Value |
|---|---|
| Sprint | STD-10C |
| Change type | audit / integrity / durability / retention / retrieval |
| Date | 2026-09-03 |
| Related commit | Pending |
| Evidence class | Local synthetic / deployment-neutral |

## Change

Hardened `AppendOnlyAuditSink` with lock-serialized append, fsync-before-return durability, integrity-checked scoped retrieval, non-destructive retention filtering, strict required fields, and fail-closed malformed-record handling. Existing redaction and hash-chain semantics remain intact.

## Validation

| Check | Result |
|---|---|
| STD-10C audit tests | PASS — 4 tests |
| LR-1 audit/authentication regressions | PASS — 6 tests |
| Combined focused result | PASS — 10 tests |
| Full suite | PASS — 172 tests |

## Evidence boundary

The result is local synthetic reference evidence. It does not establish an external immutable/WORM sink, replicated retention, legal hold, production access controls, key custody, or recovery evidence.

## Rollback

Revert the audit implementation, tests, and STD-10C evidence files after validating any concurrently-written local audit file.

## Next action

Stage STD-10D operational dashboards, alerting, and kill-switch operations separately after review.
