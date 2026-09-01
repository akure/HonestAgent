# STD-4 Durable Workflow State and Human Oversight

## Objective

STD-4 adds a durable state-machine boundary around long-running workflow decisions. It prevents stale approvals, changed proposals, duplicate resume, expiry, and cancellation from reaching execution. The implementation is deliberately additive and does not replace the existing checkpoint API.

## Lifecycle

```text
PROPOSED → EVALUATING → PAUSED → APPROVED → HANDOFF_ISSUED → EXECUTION_STARTED → COMPLETED
                   ↘ REJECTED / EXPIRED / CANCELLED
```

`COMPENSATED` is available after execution for a tool-specific recovery path. Terminal states cannot be re-opened. An expiry request against a nonterminal record deterministically records `EXPIRED` rather than allowing the requested transition.

## Durable record

`DurableWorkflowStateStore` stores the run ID, step ID, attempt, intent hash, evidence snapshot, policy snapshot, current state, reviewer, expiry, and update time in SQLite. The primary key is `(run_id, step_id, attempt)`, preventing accidental reuse of an attempt.

## Approval and execution rules

Approval requires:

- a non-empty reviewer;
- current `PAUSED` state;
- an unexpired record;
- exact intent hash match;
- exact evidence snapshot match;
- exact policy snapshot match.

Execution consumption requires the same scope and accepts only `APPROVED` or `HANDOFF_ISSUED`. Atomic state updates prevent the same approval from being consumed twice. Changed arguments, evidence, policy, tenant, step, or attempt must create a new evaluation rather than reuse an old approval.

The store does not itself authenticate a reviewer. Production deployments must combine it with the existing reviewer authentication and roster controls, and must bind the authenticated subject to the reviewer value recorded in the state transition.

## Example

```python
from honest_agent import DurableWorkflowStateStore, WorkflowState

store = DurableWorkflowStateStore("trajectories/workflow-state.sqlite3")
store.create(
    "run-1", "step-1", 1,
    intent_hash="intent-hash",
    evidence_snapshot_id="evidence-v1",
    policy_snapshot_id="policy-v1",
    expires_at=time.time() + 300,
)
store.transition("run-1", "step-1", 1, WorkflowState.EVALUATING)
store.transition("run-1", "step-1", 1, WorkflowState.PAUSED)
store.approve(
    "run-1", "step-1", 1,
    reviewer="synthetic-reviewer",
    intent_hash="intent-hash",
    evidence_snapshot_id="evidence-v1",
    policy_snapshot_id="policy-v1",
)
```

## Security boundary

This state store is not an authorization oracle by itself. The executor must still validate the current signed handoff, and the deployment must provide authenticated reviewers, protected SQLite/storage access, backup and recovery controls, and operational audit. This checkpoint provides local durable state and deterministic lifecycle behavior, not production identity, exactly-once external execution, or regulatory certification.
