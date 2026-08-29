# Change Log — executor-enforced handoff validation

| Field | Value |
|---|---|
| Change ID | `LR-3` |
| Feature | `Executor-enforced handoff validation` |
| Timestamp UTC | `2026-08-29 06:53:16` |
| Status | `complete` |

## Problem

The MVP validated handoffs through the guardrail API, but the actual upstream execution path could still be called without proving that the request matched an approved, unexpired, signed handoff. This left a critical gap between policy approval and the side-effect boundary.

## Change

Added `ExecutorGateway`, a deterministic final boundary that validates the handoff immediately before any upstream call. It rejects missing, malformed, invalid, expired, decision-mismatched, trajectory-mismatched, and payload-mismatched handoffs before invoking the upstream client. Added `/v1/execute` as an explicit executor-facing gateway route. The OpenAI-compatible proxy now routes approved forwarding through the same executor boundary and returns `EXECUTION_BLOCKED` rather than simulating an unverified execution.

The implementation deliberately keeps the model outside the consequential step: the guard proposes and evaluates, a human checkpoint can approve, the signer issues a request-bound token, and the executor deterministically validates before forwarding.

## Live experiment log

| Stage | What was tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Guard-level `validate_handoff` existed, while upstream forwarding trusted the application path | Existing tests covered token binding but not executor-side side-effect prevention | Replaced as an insufficient boundary |
| Iteration 1 | Added `ExecutorGateway` and routed upstream calls through it | Valid handoff forwarded once; invalid cases made zero upstream calls | Kept |
| Iteration 2 | Added explicit `/v1/execute` endpoint and blocked unverified chat passthrough | Proxy regression suite passed; execution without a handoff is blocked | Kept |

## Safety invariants

| Invariant | Result |
|---|---|
| No upstream side effect without a valid handoff | `PASS` |
| Handoff is bound to trajectory, tool, and payload | `PASS` |
| Expired or non-PROCEED decisions cannot execute | `PASS` |
| Missing or invalid credentials fail closed | `PASS` |
| Human approval remains required for paused consequential actions | `PASS` |
| Executor remains deterministic and model-independent | `PASS` |

## Validation

- `pytest -q`: **44 passed**
- Valid handoff reaches upstream exactly once: **PASS**
- Missing/invalid handoffs reach upstream zero times: **PASS**
- Payload and trajectory mismatches reach upstream zero times: **PASS**
- Paused decision reaches upstream zero times: **PASS**
- `git diff --check`: **PASS**

## Known limitations

The gateway currently uses the existing in-process `HonestGuard` and configured upstream client. Deployment-level executor isolation, managed secrets, and live provider fault testing remain LR-4 and LR-5 work. The current `/v1/execute` route is an enforcement seam, not a claim that arbitrary third-party executors have already been instrumented.
