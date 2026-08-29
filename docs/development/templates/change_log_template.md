# Change Log — `{feature_or_fix}`

| Field | Value |
|---|---|
| Change ID | `{FEATURE-000}` |
| Change type | `feature / fix / test / security / refactor` |
| Milestone / sprint | `{M0 / Sprint 1}` |
| Timestamp UTC | `{YYYY-MM-DD HH:MM:SS}` |
| Author | `{name or agent}` |
| Related task | `{HA-000}` |
| Related commit | `{hash after commit}` |

## Problem

Describe the observed failure mode, customer need, or product hypothesis. State what was wrong before the change and why it matters.

## Change

Describe the implementation at the boundary level. Name the public contract or behavior that changed and explain what remains intentionally unchanged.

## Files changed

| File | Role | Behavior impact |
|---|---|---|
| `{path}` | `{implementation / test / docs}` | `{summary}` |

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `{command}` | `PASS / FAIL` | `{output, metric, or artifact}` |

## Risk and limitations

State false-positive, false-negative, compatibility, security, latency, deployment, or data-retention risks. Do not claim production readiness without evidence.

## Rollback or mitigation

Describe how to disable, revert, or contain the change if it causes an incident.

## Next action

State the next builder task or decision required.
