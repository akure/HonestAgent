# Production Readiness

The repository is suitable for local development, controlled pilots, and synthetic evaluation. It is not production-ready for unrestricted side effects without the controls below.

## Required before production

| Control | Why it matters |
|---|---|
| Authentication on all proxy and reviewer endpoints | Prevent unauthorized submissions or approvals. |
| Durable shared checkpoint storage | Preserve state across processes and restarts. |
| Append-only audit storage | Prevent silent mutation or loss of review history. |
| Explicit action policy registry | Avoid assuming that tool names fully describe consequence. |
| Reviewer identity and authorization | Ensure the person approving an action is qualified and attributable. |
| Provider timeout, schema, and disagreement policies | Fail closed when verification is unavailable or ambiguous. |
| Data minimization and retention policy | Avoid storing sensitive prompts or tool arguments longer than needed. |
| Load and failure testing | Validate latency and availability under realistic concurrency. |

## Operating model

Run the gateway as a separate service or library boundary. Emit structured logs for request ID, trajectory ID, policy version, verifier tier, decision status, reviewer identity, latency, and provider outcome. Do not log secrets, raw credentials, or unnecessary personal data. Monitor the ratio of paused actions, reviewer turnaround time, provider failure rate, and unresolved checkpoints as operational signals; these are not substitutes for the primary safety metric.

## Release gate

A release should be blocked if any critical-action fixture has a false negative, if verifier failure can produce `PROCEED`, if approval is unauthenticated, if the persisted audit state disagrees with the returned decision, or if a clean-checkout reproduction fails.
