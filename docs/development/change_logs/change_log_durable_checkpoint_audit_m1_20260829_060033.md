# Change Log — durable checkpoint and audit foundation

| Field | Value |
|---|---|
| Change ID | `HA-M1-001` |
| Change type | `feature` and boundary refactor |
| Milestone / sprint | `M1 / Sprint 2` |
| Timestamp UTC | `2026-08-29 06:00:33` |
| Related tasks | `HA-004`, `HA-005`, `HA-006` |
| Related commit | `{filled after commit}` |

## Problem

Pending approvals were held only in process memory. A restart or a second worker could lose the checkpoint, making the reviewer flow unreliable. Approval routes were also embedded in `proxy.py`, which made the HTTP boundary harder to replace or test independently.

## Change

Added a replaceable `CheckpointStore` interface and an atomic file-backed implementation. Pending and resolved decisions now survive a guard restart, duplicate resolutions remain idempotent, and the final decision is retained alongside the request. Approval and rejection routes moved into `interfaces/webhooks.py` and are included by the proxy as an adapter.

## Files changed

| File | Role | Behavior impact |
|---|---|---|
| `honest_agent/core/checkpoints.py` | Storage boundary | Adds atomic JSON persistence for pending and resolved checkpoints. |
| `honest_agent/core/guardrail.py` | Core lifecycle | Loads and resolves checkpoints through the storage interface. |
| `honest_agent/schemas/models.py` | Configuration | Adds configurable checkpoint path. |
| `honest_agent/interfaces/webhooks.py` | Integration boundary | Owns approval and rejection endpoints. |
| `honest_agent/interfaces/proxy.py` | Adapter | Includes the webhook router without owning its business logic. |
| `tests/test_m1_durability.py` | Regression tests | Proves restart-safe approval and route separation. |

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `python3 -m pytest -q` | `PASS` | 22 tests passed. |
| Restart simulation | `PASS` | A new `HonestGuard` instance approved a pending trajectory created by the prior instance. |
| Audit persistence | `PASS` | Persisted trajectory and checkpoint store both show final `APPROVED` state. |

## Risk and limitations

The file store is suitable for local development and a single-writer pilot, not for multi-worker production. Reviewer authentication, expiry, append-only event history, and payload-bound execution handoffs remain open launch blockers.

## Rollback or mitigation

Revert the M1 commit to restore in-process state, or configure a dedicated checkpoint path per development/test process. Do not use the file store for multiple production workers without a stronger storage implementation.

## Next action

Proceed to M2: add authenticated reviewer semantics, payload-bound executor handoffs, and verifier-provider contract tests before allowing any real passthrough.
