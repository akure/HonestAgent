# Sprint Trace — B-3 third-party executor coverage

| Field | Value |
|---|---|
| Sprint | `B-3` |
| Objective | Ensure supported third-party callable executors validate request-bound handoffs before any side effect. |
| Timestamp UTC | `2026-08-29 07:22:53` |
| Status | `complete for supported adapter boundary` |
| Commit | `{filled after commit}` |

## Baseline risk

The application executor gateway was enforced, but integrations that directly called tools could bypass it. A shared adapter was needed to make the pre-invocation validation contract reusable and testable.

## Implementation

1. Added `CallableExecutor` around third-party synchronous and asynchronous tool callables.
2. Reused guardrail handoff validation for trajectory, payload, decision, signature, and expiry binding.
3. Raised `ExecutionBlocked` before invocation when validation fails.
4. Added tests with side-effect counters proving invalid paths invoke zero times.

## Verification matrix

| Case | Expected | Result |
|---|---:|---:|
| Valid synchronous callable | Invoked once | PASS |
| Missing token | Zero invocation | PASS |
| Invalid token | Zero invocation | PASS |
| Altered payload | Zero invocation | PASS |
| Async callable | Awaited and returned | PASS |
| Full regression suite | No regressions | 75 passed |

## Gate decision

**B-3 is closed for integrations using `CallableExecutor`.** The deployment owner must still inventory all actual third-party executors and attach equivalent bypass-resistance evidence for each before unrestricted production.

## Next action

Proceed to B-4: complete deployment platform security evidence, including DNS rebinding, egress, TLS, container, host, dependency, and vulnerability checks.
