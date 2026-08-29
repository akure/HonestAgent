# Honest Agent — MVP Launch and Product-Market-Fit Roadmap

## Product thesis

Honest Agent should launch as a **control-readiness product for one consequential AI workflow**, not as a broad observability platform. The first customer does not need another dashboard or a promise of perfect model accuracy. They need a defensible answer to a narrower question:

> **Before this agent changes a system of record or triggers an external side effect, can we prove what it proposed, why it was allowed or paused, and who approved it?**

The MVP should make that question easy to answer for one workflow in two weeks. The product can expand only after customers repeatedly value the control boundary enough to keep it in production.

## Target launch customer

The beachhead customer is a **platform or infrastructure team at a 50–500 person company** that has one agent in a controlled production pilot. The agent performs actions such as invoice reconciliation, customer-record updates, internal ticket changes, deployment operations, or document workflow transitions. The team already has an application and an agent framework, but lacks a consistent pre-execution policy and reviewer trail.

The champion is an AI platform engineer. The buyer is the Head of AI Platform, VP Engineering, or CTO. Security or compliance becomes an important co-sponsor when production approval depends on evidence. The customer is a poor fit if the agent is purely conversational, has no tools, or has no owner willing to define action policy and review responsibility.

## MVP promise

**Install one SDK or proxy integration, define the customer’s action policy, and obtain a measurable pre-execution control for one workflow without replacing the customer’s agent framework or model provider.**

The MVP should promise four concrete outputs: a deterministic action-policy decision; a fail-closed verifier boundary; a human review queue for paused actions; and an exportable audit package containing the action, context summary, policy version, verifier result, reviewer, and final disposition.

## MVP scope

| Area | Launch scope | Explicitly deferred |
|---|---|---|
| Integrations | Production-quality Python SDK and true OpenAI-compatible HTTP guard/proxy. | Official MCP protocol and additional framework adapters until customer demand is proven. |
| Policy | Explicit registry for read-only, reversible, irreversible, and unknown actions; unknown external actions default to review. | Fully automated policy discovery. |
| Verification | Offline deterministic verifier for development plus one supported hosted provider adapter with timeout and schema validation. | Multi-provider optimization and custom enterprise scoring models. |
| HITL | Authenticated review queue with approve, reject, expire, and replay-safe state transitions. | Complex workflow orchestration and delegated approval chains. |
| Audit | Durable append-only event storage, exportable JSON, retention controls, and policy/version identifiers. | Full SIEM/APM replacement and broad analytics dashboards. |
| Deployment | Docker image and one documented hosted or private deployment path. | Multi-region active-active and multi-tenant control plane. |
| Commercial | Two-week paid control-readiness pilot converting to Team or Business. | Usage-based pricing experiments before value and review burden are understood. |

## Launch blockers

The MVP must not be marketed as production-ready until the following are complete:

| Blocker | Acceptance criterion |
|---|---|
| Real execution boundary | The guard forwards or releases an action only after the deterministic policy and checkpoint decision; no bypass path exists in the supported integration. |
| Durable state | Pending, approved, rejected, expired, and replayed checkpoints survive restart and behave correctly across workers. |
| Reviewer security | Caller authentication, reviewer identity, authorization, and audit attribution are enforced. |
| Policy registry | Unknown or consequential actions cannot silently proceed because a keyword heuristic missed them. |
| Provider failure | Timeout, malformed response, disagreement, and cancellation all fail closed and are observable. |
| Audit evidence | A sanitized export reconstructs the original proposal, policy version, verifier result, checkpoint, and final disposition. |
| Customer workflow | A pilot owner can configure one policy, review one paused action, and explain the result without engineering intervention. |
| Measurement | A before/after benchmark reports unsafe interception, safe-action block rate, review burden, and p50/p95 latency. |

## PMF feature sequence

### Wave 1 — Make the control trustworthy

Build the explicit policy registry, durable checkpoint store, authenticated reviewers, true upstream passthrough, provider adapter contract, and append-only audit events. These features reduce existential risk and are more valuable than adding more integrations.

### Wave 2 — Make the control adoptable

Add a configuration file and policy simulator, framework examples for LangGraph and one common agent stack, deployment templates, sanitized evidence export, and a review queue that a non-author can operate. The goal is to reduce time-to-first-controlled-action from days to hours.

### Wave 3 — Make the control habit-forming

Add policy version comparison, replayable evaluation datasets, drift alerts, reviewer workload reporting, action-level risk analytics, and regression gates in CI/CD. The product becomes part of the customer’s release process rather than a one-time compliance project.

### Wave 4 — Make the control expandable

Add official MCP support, additional framework adapters, private deployment options, organization-level policy administration, regional data controls, and service-level reporting. Build these only when at least three customers request the same capability or when pilot evidence shows it is required for expansion.

## Validation plan

| Experiment | Method | Success signal |
|---|---|---|
| Problem validation | Interview 12 platform or infrastructure leads who operate tool-using agents. Ask for the last unsafe or delayed deployment decision and the evidence requested. | At least 8 report the same pre-execution or audit bottleneck without being prompted. |
| Concierge pilot | Instrument one customer workflow manually with a policy registry and review process before automating the full product. | Customer completes a controlled production or staging run and requests continued use. |
| Safety value | Run the customer’s baseline pass-through and guarded workflow on identical replay data. | Zero critical unsafe actions proceed; safe-action block rate remains acceptable to the workflow owner. |
| Workflow value | Measure setup time, reviewer turnaround, unresolved checkpoints, and engineer intervention. | First controlled action in under one business day; reviewers resolve common cases without engineering help. |
| Willingness to pay | Offer a fixed-scope paid pilot with a clear conversion path. | At least 3 of the first 5 qualified pilots pay; at least 2 request a recurring deployment. |
| Retention | Review the same workflow after 30, 60, and 90 days. | Customer keeps the guard enabled and adds either another workflow or a paid governance feature. |

## North-star and guardrail metrics

The north-star metric is **protected consequential actions per active customer workflow**, because it combines real usage with the product’s control purpose. It should not be optimized by increasing review volume alone.

| Metric | Why it matters | Initial target for PMF evidence |
|---|---|---:|
| Protected consequential actions | Demonstrates the product is in the execution path where risk matters. | 1,000+ per active workflow per month during pilot. |
| Critical unsafe actions released | Safety gate. | 0 in reviewed pilot fixtures and incident review. |
| Safe-action block rate | Detects over-blocking and reviewer fatigue. | Under 5% for labeled safe actions after policy tuning. |
| Review turnaround | Measures operational usability. | Median under 10 minutes during staffed hours. |
| Time to first protected action | Measures adoption friction. | Under 1 business day. |
| Pilot-to-recurring conversion | Measures commercial pull. | At least 40% after the first five qualified pilots. |
| 90-day retained workflows | Measures real PMF rather than demo enthusiasm. | At least 60% of converted pilots. |

Targets are working hypotheses for customer discovery and must be revised from observed data, not treated as guaranteed outcomes.

## Pricing and packaging for launch

Keep the Community edition free and self-hosted to create developer adoption. Sell the **control-readiness pilot** first at a fixed fee of **$15,000–$25,000**, depending on integration and review complexity. Convert successful pilots to a Team plan around **$1,500–$3,000 per month** when one team needs a durable review queue, policy registry, and support. Move to Business or Enterprise pricing when customers need SSO, private deployment, retention controls, regional deployment, multiple workflows, or contractual support.

Price around **risk governed and operational control**, not raw token volume. A workflow that performs fewer but more consequential actions should be more valuable than a high-volume low-risk chatbot. Usage limits can protect infrastructure, but they should not define the value proposition.

## Go-to-market sequence

Start with founder-led design partnerships and one narrow vertical at a time. The first outbound message should not ask whether a prospect wants “AI guardrails.” It should ask which agent actions they would not allow to execute without a reviewer, what evidence their security team requires, and how they currently prove that a tool action was safe.

The demo should take less than ten minutes: one safe read proceeds, one ambiguous action pauses, one irreversible action is approved by a reviewer, and the evidence export reconstructs the sequence. The sales artifact should be a control-readiness report with baseline, guarded result, review burden, latency, open risks, and a production recommendation.

## Decision gates

| Gate | Decision |
|---|---|
| Gate A — Problem | Continue only if interviews reveal a repeated pre-execution or audit bottleneck with a named owner. |
| Gate B — Pilot | Continue only if a customer supplies a sanitized replay set or allows a controlled staging integration. |
| Gate C — Paid value | Continue only if the customer pays for a pilot or signs a written procurement path. |
| Gate D — Retention | Invest in PMF features only when customers keep the guard enabled and request expansion. |
| Gate E — Scale | Add hosted multi-tenant capabilities only after repeated demand and a clear security model. |

## Recommended next 90 days

| Period | Focus | Deliverable |
|---|---|---|
| Days 1–30 | Close launch blockers. | Explicit policy registry, durable checkpoints, reviewer auth, provider adapter contract, true passthrough, and production-readiness tests. |
| Days 31–60 | Run design-partner pilots. | Two sanitized or staging integrations, control-readiness reports, review-burden data, and pricing feedback. |
| Days 61–90 | Convert learning into PMF. | Policy simulator, evidence export, deployment templates, one framework example, paid pilot conversion decision, and revised roadmap based on observed retention. |

## Bottom line

The MVP should sell **confidence in controlled execution**, not generic AI accuracy. Build the smallest product that sits on the real action boundary, produces evidence a buyer can use, and earns the right to expand through repeated customer workflows. The next engineering investment should be durable policy and approval semantics; the next commercial investment should be design-partner pilots with measurable before-and-after evidence.
