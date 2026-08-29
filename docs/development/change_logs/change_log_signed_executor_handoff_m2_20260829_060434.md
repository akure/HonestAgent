# Change Log — signed executor handoff

| Field | Value |
|---|---|
| Change ID | `HA-M2-001` |
| Change type | `feature` and safety hardening |
| Milestone / sprint | `M2 / Sprint 3` |
| Timestamp UTC | `2026-08-29 06:04:34` |
| Related tasks | `HA-007`, `HA-009` |
| Related commit | `{filled after commit}` |

## Problem

A `PROCEED` or approved decision did not yet produce a request-bound artifact that an executor could validate. Without that binding, a caller could theoretically change tool arguments or reuse a decision for another trajectory.

## Change

Added `HandoffSigner`, payload hashing, HMAC-signed claims, expiry, and `HonestGuard.validate_handoff()`. A handoff is issued only for `PROCEED`, includes trajectory ID, tool name, payload hash, policy version, action class, and expiration, and is rejected when the payload, trajectory, status, signature, or expiry does not match.

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `python3 -m pytest -q` | `PASS` | 24 tests passed. |
| Payload mutation test | `PASS` | Changing `{id: 42}` to `{id: 43}` invalidates the handoff. |
| Paused-action test | `PASS` | Paused actions have no handoff token. |

## Failure found during implementation

The first implementation attempted to issue a handoff for every non-paused outcome, including structured rejections for empty tool names. The regression suite caught this immediately. Handoff issuance is now restricted to `DecisionStatus.PROCEED`.

## Risk and limitations

The development default uses a local secret and in-process resolved-decision cache with file-backed fallback. Production requires secret-manager injection, durable shared state, replay policy, authenticated callers, and an executor that actually validates the handoff before performing a side effect.

## Rollback or mitigation

Do not execute any tool unless the executor validates the handoff against the original request. Revert the M2 commit if the signing secret cannot be managed securely in the deployment environment.

## Next action

Proceed to M3: implement the real OpenAI-compatible passthrough boundary and one provider adapter contract without making live credentials a CI dependency.
