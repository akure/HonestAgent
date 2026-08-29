# Honest Agent — Deep Evaluation Plan

## Current baseline observation

The first 12-case run reports **100% unsafe-action catch rate** and **0.061 ms mean latency**, but it is too narrow to establish precision, robustness, or correct interface semantics. It contains almost no safe write-like actions, no concurrency, no replay behavior, no provider failure, no malformed HTTP payloads, and no direct MCP or SDK contract coverage.

## Hypotheses

| ID | Hypothesis | Measurement | Failure severity |
|---|---|---|---|
| H1 | Deterministic keyword routing is too sensitive to substrings and will escalate benign tools such as `runtime_status` or `rewrite_summary`. | False escalation rate on labeled safe cases. | Medium: latency/cost inflation, not unsafe execution. |
| H2 | Treating every empty `tool_input` as invalid rejects legitimate zero-argument read-only tools. | Safe-action false-block rate on zero-argument fixtures. | High for availability; low for safety. |
| H3 | Low-confidence and irreversible actions are blocked before execution, but approval state may be replayed or resolved concurrently. | Replay, double-approval, and concurrent approval tests. | Critical: could permit an unintended action or corrupt audit state. |
| H4 | Context telemetry with a deterministic approximation may undercount or overcount structured messages and non-ASCII text. | Count fixtures with punctuation, code, JSON, and Unicode; compare expected contract behavior. | Medium: incorrect escalation. |
| H5 | Provider failure behavior is unspecified and may fail open or crash rather than fail closed. | Inject verifier exceptions and timeouts. | Critical if execution can continue. |
| H6 | Trajectory logging is reliable on the proxy path but may be absent or inconsistent for SDK/MCP paths. | Interface parity and log-schema validation. | High: audit gap. |
| H7 | A single configurable threshold produces avoidable false positives near the boundary. | Threshold sweep on confidence-labeled cases; report precision/recall tradeoff. | Medium: review burden. |
| H8 | The baseline comparison is valid for safety catch rate but not for operational utility; safe-action pass-through and approval latency need separate reporting. | Confusion matrix: TP, FN, FP, TN plus p50/p95 latency. | Medium: misleading product decision. |

## Expanded evaluation matrix

The next fixture set will include at least 40 deterministic cases across: safe reads, safe zero-argument calls, benign tool names containing risk substrings, missing context, contradictory context, unsupported identifiers, high context ratios, irreversible actions, malformed inputs, provider errors, repeated approvals, concurrent approvals, and interface-specific requests. At least five cases will be deliberately hard: plausible-but-unsupported identifiers, context that says “do not execute” while the tool says execute, a safe tool with a misleading name, an irreversible action with high confidence, and a provider timeout.

## Metrics

The primary safety metric remains **unsafe-action interception rate before execution**, but it will be paired with a confusion matrix. Secondary metrics are **false-block rate on labeled safe actions** and **p50/p95 guard latency**. Audit completeness and approval-state correctness are release gates, not cosmetic metrics.

## Acceptance gates

The next revision is not accepted unless it maintains zero false negatives on the critical-action fixtures, reports all false positives explicitly, fails closed on verifier errors, makes approval transitions idempotent and non-replayable, and produces a valid trajectory for every interface path.
