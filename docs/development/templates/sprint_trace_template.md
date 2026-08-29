# Sprint Trace — `{milestone} / {sprint}`

| Field | Value |
|---|---|
| Milestone | `{M0}` |
| Sprint | `{Sprint 1}` |
| Objective | `{one sentence}` |
| Start UTC | `{timestamp}` |
| End UTC | `{timestamp}` |
| Status | `planned / active / complete / blocked` |

## Scope

State the exact builder tasks included in this sprint and the tasks explicitly deferred.

## Execution trace

| Order | Task | Action | Result | Evidence |
|---:|---|---|---|---|
| 1 | `{HA-000}` | `{implemented / tested / investigated}` | `{result}` | `{file, command, or metric}` |

## Failures discovered

Record failed tests or unexpected behavior before describing the fix. Include the impact and severity.

## Decisions and trade-offs

Explain why the implementation choice was made, what alternatives were rejected, and which assumptions remain.

## Validation

| Gate | Command or artifact | Result |
|---|---|---|
| Unit / integration | `{command}` | `PASS / FAIL` |
| Adversarial | `{command}` | `PASS / FAIL` |
| Benchmark | `{artifact}` | `{metric}` |
| Security / hygiene | `{command}` | `PASS / FAIL` |

## Git publication

| Commit | Message | Remote status |
|---|---|---|
| `{hash}` | `{conventional commit}` | `{origin/main hash}` |

## Milestone decision

State whether the sprint is complete, blocked, or requires another iteration. Do not start the next sprint until this decision is published and reviewed.
