# Sprint Trace — STD-6 Reliable Execution Semantics and Operational Controls

| Field | Value |
|---|---|
| Sprint | STD-6 |
| Objective | Add a durable generic execution boundary with explicit at-most-once/idempotent semantics, bounded retries, timeout, cancellation, recovery, kill switches, and quotas. |
| Date | 2026-09-02 |
| Status | Complete |
| Evidence class | Local SQLite, synthetic tool, deterministic failure evidence |
| Commit | Pending |

## Baseline risk

The framework had durable checkpoints and workflow budgets but no generic transactional intent inbox/outbox or explicit execution claim semantics. Provider failure and worker crash handling could not be represented in a reusable execution record.

## Delivered

| Deliverable | Artifact |
|---|---|
| Durable intent store and executor | `honest_agent/core/reliable_execution.py` |
| Public execution exports | `honest_agent/__init__.py` |
| Reliability regression matrix | `tests/test_std6_reliable_execution.py` |

The store persists intent identity, tenant/workflow/tool scope, payload, idempotency key, semantics, attempt cap, timeout, state, error, and result. Duplicate submissions with the same tenant/tool/idempotency key return the original intent. At-most-once intents are capped to one attempt. Idempotent-at-least-once intents may retry only after retryable failure. Claims are transactional. Kill switches and aggregate quotas block claims before tool invocation.

## Defect discovered and corrected

The first implementation used 15 SQL placeholders for a 14-column intent table, causing every submission to fail before persistence. The insert statement was corrected and the full matrix rerun successfully.

## Verification

| Check | Result |
|---|---|
| STD-6 focused tests | PASS — 4 tests |
| Full regression suite | PASS — 145 tests |
| Idempotency deduplication | PASS |
| Retry only for idempotent semantics | PASS |
| Timeout cannot create success | PASS |
| Crash recovery to unknown state | PASS |
| Cancellation before claim | PASS |
| Kill switch and aggregate quota | PASS |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

Provider exceptions and timeouts never become success. At-most-once protected mutations are not silently replayed after an unknown crash. A claim is required before execution, and kill switches/quotas are evaluated transactionally before claim. A duplicate idempotency submission cannot create a second intent.

## Limitations

The local store does not guarantee exactly-once behavior for external systems. `UNKNOWN_AFTER_CRASH` requires operator reconciliation; automatic replay is intentionally not enabled for at-most-once work. The reference executor does not yet include a distributed circuit breaker, external health registry, authenticated operational control plane, or production crash/failover evidence.

## Rollback

Revert the additive reliable-execution module, public exports, tests, and documentation. Existing checkpoint and workflow-budget stores remain available.

## Next checkpoint

Proceed to **STD-7 — Version-Pinned Framework Integrations**.
