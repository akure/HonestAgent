# Sprint Trace — B-1 live provider evidence

| Field | Value |
|---|---|
| Sprint | `B-1` |
| Objective | Collect approved live-provider fault and latency evidence without fabricating results or exposing credentials. |
| Timestamp UTC | `2026-08-29 07:17:00` |
| Status | `runner complete; evidence NOT MEASURED` |
| Commit | `{filled after commit}` |

## Implementation

Added a target-environment runner that requires `HONEST_AGENT_PROVIDER_ENDPOINT`, `HONEST_AGENT_PROVIDER_API_KEY`, and `HONEST_AGENT_PROVIDER_MODEL`. It runs synthetic requests through the existing provider observation and bounded-retry boundary, records typed outcomes and latency, closes the client, and writes JSON without payloads or secrets. Missing inputs produce an explicit `NOT_MEASURED` report and no network request.

## Verification matrix

| Case | Expected | Result |
|---|---:|---:|
| Runner without endpoint/key/model | NOT_MEASURED; zero network calls | PASS |
| Secret material in output | Absent | PASS |
| Existing provider fault and latency tests | No regression | PASS |
| Live approved provider p50/p95/p99 | Target environment required | NOT MEASURED |
| Live timeout/malformed/disagreement/cancellation matrix | Target environment required | NOT MEASURED |

## Gate decision

**B-1 remains open.** The reusable runner and evidence format are ready, but no approved live provider credentials or endpoint were available. The release remains **NO-GO for unrestricted production**.

## Next action

Provide approved target-environment provider configuration through deployment secrets, run the same script, attach the resulting redacted report, and review the latency/fault thresholds before marking B-1 closed.
