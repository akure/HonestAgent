# Sprint Trace — STD-4 Durable Workflow State and Human Oversight

| Field | Value |
|---|---|
| Sprint | STD-4 |
| Objective | Add a durable, scoped workflow lifecycle around approval and execution. |
| Date | 2026-09-01 |
| Status | Complete |
| Evidence class | Local SQLite state-machine and regression evidence |
| Commit | `49d0cb3` |

## Delivered

| Deliverable | Artifact |
|---|---|
| Durable state store | `honest_agent/core/workflow_state.py` |
| Public state exports | `honest_agent/__init__.py` |
| State and approval tests | `tests/test_std4_workflow_state.py` |
| Architecture documentation | `docs/architecture/durable-workflow-state-human-oversight-std4_20260901.md` |

The store uses `(run_id, step_id, attempt)` as its identity and records intent, evidence, policy, reviewer, expiry, and lifecycle state. Approval and execution consumption are atomic and require exact snapshot scope matches.

## Defect discovered and corrected

The first expiry test expected an exception when requesting a transition after expiry. The implementation intentionally converts that request into a deterministic terminal `EXPIRED` state. The test was corrected to assert the safe terminal state; no expired record can proceed to approval or execution.

## Validation

| Check | Result |
|---|---|
| STD-4 state tests | PASS — 3 tests |
| Full regression suite | PASS — 138 tests |
| Restart persistence | PASS |
| Scoped approval and duplicate consume | PASS |
| Expiry and cancellation | PASS |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Limitations

The store does not authenticate reviewers by itself; production must combine it with reviewer authentication and roster enforcement. It does not claim exactly-once external side effects, full audit-stream durability, backup/failover evidence, or regulatory certification. Existing guard/handoff validation remains required.

## Next checkpoint

Proceed to **STD-5 — Policy Composition and Delegation Attenuation**.
