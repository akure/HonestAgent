# Honest Agent — Next Enhancement Roadmap

## Priority 0: close the production-safety boundary

| Enhancement | Why now | Acceptance criteria |
|---|---|---|
| Explicit policy registry | Tool-name conventions cannot fully express consequence. | Applications declare `read_only`, `reversible`, `irreversible`, and `unknown`; unknown external actions default to review. Policy conflicts are deterministic and tested. |
| Durable checkpoint store | In-process dictionaries are not safe across restarts or multiple workers. | Approval state survives restart, has expiry, supports concurrent resolution, and preserves append-only events. |
| Authentication and reviewer authorization | `/approve` is currently a development endpoint. | Caller authentication, reviewer identity, role checks, and audit attribution are required before resolution. |
| Separate webhook adapter | The planned integration boundary is currently embedded in `proxy.py`. | `interfaces/webhooks.py` owns approval routes and can be deployed independently from the proxy. |

## Priority 1: provider and protocol fidelity

| Enhancement | Why now | Acceptance criteria |
|---|---|---|
| Verifier provider adapters | Initial requirements name Groq, Gemini Flash, and Ollama, but only the offline verifier exists. | Each provider implements the same async protocol with timeout, schema validation, cost/latency metadata, and fail-closed behavior. |
| Official MCP implementation | The current adapter is line-delimited JSON rather than standard MCP transport. | Tool discovery, schemas, errors, and invocation pass official MCP client contract tests. |
| True OpenAI-compatible passthrough | The current route returns a simulated completion. | Request is forwarded only after guard approval; streaming, upstream errors, timeouts, and response metadata are covered. |

## Priority 2: measurement quality

| Enhancement | Why now | Acceptance criteria |
|---|---|---|
| Model-specific tokenizers | Regex counts are deterministic but not exact for providers. | Tokenizer is configurable per model; telemetry distinguishes estimated from provider-reported counts. |
| Provider failure and disagreement suite | Safety depends on behavior when verifiers fail or disagree. | Fixtures cover timeout, malformed JSON, low confidence, disagreement, cancellation, and retry limits. No failure path returns `PROCEED`. |
| Separate hot-path and audit latency | Local persistence is part of current timing, but provider and I/O costs need attribution. | Report verifier, policy, persistence, and end-to-end p50/p95/p99 separately. |
| Mutation and paraphrase evaluation | Fixed keyword fixtures can overstate generalization. | Generate reviewed, deterministic paraphrases and adversarial mutations with labeled expected outcomes; preserve the same baseline cases. |

## Priority 3: client value and operations

| Enhancement | Why now | Acceptance criteria |
|---|---|---|
| Review queue API | A real customer needs more than a single approval endpoint. | List, filter, claim, approve, reject, expire, and audit pending checkpoints. |
| Policy simulation mode | Buyers need to estimate review burden before enforcement. | Dry-run shows would-block and would-escalate rates without executing actions. |
| Evidence export | Security reviews need portable proof. | Export sanitized trajectories, policy versions, benchmark results, and reviewer events. |
| Pilot instrumentation | Commercial pilots need comparable before/after evidence. | One workflow can report baseline risk, guard interception, review burden, latency, and unresolved cases. |

## Sequencing recommendation

Build Priority 0 first because it closes the real side-effect boundary. Build Priority 1 second because the current HTTP, MCP, and provider integrations are the main requirement gaps. Build Priority 2 third to ensure later performance and accuracy claims are meaningful. Build Priority 3 when a pilot customer has confirmed the operational workflow; do not build a dashboard before the review and policy semantics are stable.

## Definition of done for the next major release

The next major release is ready for a controlled customer pilot when a true upstream passthrough is covered, official MCP clients can discover and invoke tools, providers fail closed under fault injection, approval state is durable and authenticated, an explicit action policy is enforced, and the evaluation reports a confusion matrix plus latency breakdown on a reviewed adversarial set.
