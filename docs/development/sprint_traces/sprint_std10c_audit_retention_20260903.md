# Sprint Trace — STD-10C Immutable Audit and Evidence Retention

| Field | Value |
|---|---|
| Sprint | STD-10C |
| Objective | Harden the local audit boundary with serialized durable append, integrity-safe retrieval, retention filtering, and adversarial verification. |
| Date | 2026-09-03 |
| Status | Complete |
| Evidence class | Local synthetic / deployment-neutral |
| Commit | Pending |

## Baseline risk

The append-only audit sink used hash chaining but read the final record and appended without inter-process locking or an fsync durability boundary. Concurrent writers could race on `previous_hash`, and retrieval required consumers to parse the file themselves. Verification also mutated parsed records while checking them and did not provide a retention-aware query boundary.

## Delivered

The existing `AppendOnlyAuditSink` now serializes append operations with a lock file, computes the chain predecessor under the same lock, flushes and fsyncs the event before returning, and rejects missing audit identity fields. It supports integrity-checked retrieval by subject, trajectory, time window, and limit. Configured retention filters retrieval without deleting records, preserving the immutable local evidence file. Malformed, truncated, modified, and chain-broken records fail closed as `AuditIntegrityError`.

## Defect discovered and corrected

The defect was a durability and concurrency gap in the append boundary. The fix prevents concurrent predecessor races and makes the write durable before acknowledgement. Tests cover 32 concurrent writers, retention filtering without deletion, malformed records, tampering, chain verification, and required identity fields.

## Verification

| Check | Result |
|---|---|
| STD-10C audit tests | PASS — 4 tests |
| Existing LR-1 audit/authentication tests | PASS — 6 tests |
| Combined focused result | PASS — 10 tests |
| Full Python regression suite | PASS — 172 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

Every record is redacted before hashing and append. The hash covers all record fields except the hash itself, and each record commits to its predecessor. Retrieval verifies the entire chain before returning filtered results. Retention is non-destructive; no API silently deletes evidence. Secrets and token material are not written by the sink.

## Limitations

This is a local file-backed reference sink, not an externally immutable WORM store. It does not evidence object-lock retention, external replication, access-control separation, key custody, multi-region recovery, legal hold, or production retrieval latency. File permissions, volume durability, and external forwarding remain deployment responsibilities.

## Rollback

Revert the audit sink, tests, and STD-10C evidence artifacts. Existing audit files remain readable by the prior verifier unless they contain records written concurrently under the new boundary; validate and snapshot them before any rollback.

## Next checkpoint

STD-10D should address operational dashboards, alerting, and kill-switch operations in a separately scoped deployment-neutral checkpoint.
