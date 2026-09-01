# Change Log — STD-4 Durable Workflow State and Human Oversight

| Field | Value |
|---|---|
| Sprint | STD-4 |
| Change type | workflow state / approval / persistence / test |
| Date | 2026-09-01 |
| Related commit | Pending |
| Evidence class | Local SQLite state-machine evidence |

## Change

Added `DurableWorkflowStateStore` and explicit `WorkflowState` lifecycle values for proposal, evaluation, pause, approval, rejection, expiry, cancellation, handoff, execution, completion, and compensation. Records are keyed by run, step, and attempt and persist exact intent, evidence, and policy snapshots.

Approval is atomic and exact-scope. Execution consumption is atomic, accepts only approved/handoff-ready states, and rejects duplicate consumption or any changed intent/evidence/policy scope. Store restart persistence is covered by regression tests.

## Correction

Expiry behavior is deterministic: an expired nonterminal record transitions to terminal `EXPIRED`; it is never approved or consumed for execution. The test was corrected to assert this safe behavior.

## Validation

| Check | Result |
|---|---|
| STD-4 tests | PASS — 3 tests |
| Full regression suite | PASS — 138 tests |
| SQLite restart persistence | PASS |
| Approval scope and replay rejection | PASS |
| Expiry and cancellation | PASS |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security and limitations

This store is not a reviewer identity provider and does not guarantee exactly-once external side effects. Executors must still validate signed handoffs. Production deployment requires authenticated reviewer roster integration, protected storage, backup/recovery, audit integrity, and operational controls.

## Rollback

Revert the additive state-store module, exports, tests, and documentation. Existing checkpoint APIs and CX-1 budget storage remain available.

## Next action

Implement STD-5 policy composition and delegation attenuation.
