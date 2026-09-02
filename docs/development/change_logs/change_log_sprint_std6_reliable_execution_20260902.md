# Change Log — STD-6 Reliable Execution Semantics and Operational Controls

| Field | Value |
|---|---|
| Sprint | STD-6 |
| Change type | execution / reliability / persistence / operational controls / test |
| Date | 2026-09-02 |
| Related commit | Pending |
| Evidence class | Local SQLite, synthetic tool, deterministic failure evidence |

## Change

Added a durable SQLite intent inbox/outbox and `ReliableExecutor`. Execution semantics are explicit: `AT_MOST_ONCE` forces one attempt, while `IDEMPOTENT_AT_LEAST_ONCE` permits bounded retry after retryable provider failure or timeout. Intent claims, terminal success/failure, cancellation, and crash recovery are persisted. Kill switches and aggregate scope quotas block execution before claim.

Added deterministic failure tests for duplicate idempotency submissions, provider failure, timeout, cancellation, crash recovery, kill switches, and quotas.

## Defect discovered and corrected

An initial insert statement supplied 15 values to a 14-column SQLite table. The defect was caught by the focused tests before publication; the placeholder count was corrected and all tests passed.

## Validation

| Check | Result |
|---|---|
| STD-6 tests | PASS — 4 tests |
| Full regression suite | PASS — 145 tests |
| Provider failure never reports success | PASS |
| At-most-once crash recovery does not replay | PASS |
| Idempotent retry bound | PASS |
| Duplicate idempotency submission | PASS |
| Timeout, cancellation, kill switch, quota | PASS |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security and limitations

The implementation does not claim exactly-once external side effects. Unknown post-crash outcomes require reconciliation. Operational controls are local SQLite controls, not an authenticated distributed control plane. Circuit-breaker health aggregation, external failover, and production crash drills remain future evidence work.

## Rollback

Revert `reliable_execution.py`, public exports, tests, changelog, and sprint evidence. Existing checkpoint and budget controls remain available.

## Next action

Implement STD-7 version-pinned framework integrations and native pause/resume/cancellation coverage.
