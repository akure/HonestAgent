# Honest Agent — Client Business Model

## Executive positioning

**Honest Agent is the pre-execution safety layer for AI agents.** It sits between an agent and consequential tools, independently checks whether the proposed action is grounded, escalates risky actions, pauses uncertainty for human review, and leaves an audit-ready decision trail.

The product should not compete as a generic LLM gateway or full observability platform. Public market offerings already provide broad gateway functions, logging, routing, analytics, and guardrails; Cloudflare AI Gateway, for example, publishes a free core with persistent-log limits and usage-based guardrail inference [1]. Arize AX positions around tracing, evaluations, experimentation, human annotations, and enterprise deployment options [2]. Portkey’s buyer guidance describes gateways as centralized layers for routing, governance, credentials, policy enforcement, and observability [3].

Honest Agent’s wedge is narrower and more defensible: **prove that a high-consequence tool action was stopped or explicitly approved before execution**. This makes it complementary to an existing gateway, observability platform, or agent framework.

## Ideal customer profile

The initial buyer is a **Head of AI Platform, VP Engineering, or CTO** at a company deploying agents into finance operations, healthcare administration, legal workflows, customer support, or internal developer tooling. The champion is usually an AI infrastructure or platform engineer. The economic buyer cares about incident prevention, deployment confidence, customer assurance, and reduced time spent building bespoke controls.

A qualified prospect has at least two of the following signals: agents can write to a system of record; the company needs reviewer approval or audit evidence; multiple frameworks or model providers are in use; a security or compliance review is delaying production deployment; or the platform team is maintaining custom guard code in several services.

## Product packaging

The commercial model assumes a proprietary core. Public repository visibility is for evaluation and does not grant rights to copy, fork, redistribute, host, resell, or use the software in a client engagement. Every paid pilot, subscription, implementation, private deployment, or managed service requires a written commercial license or services agreement that states the permitted customer, environment, term, support, and data boundaries. The prices below are discovery hypotheses, not automatic permissions.

| Package | Intended customer | Proposed price | Included |
|---|---|---:|---|
| Evaluation | Prospective customers evaluating the product | Free or time-limited | Unaltered internal evaluation with synthetic data; no redistribution, client delivery, production use, or commercial deployment. |
| Team | One product team moving an agent into controlled production | $1,500/month | Hosted control endpoint or supported self-hosting, policy registry, shared review queue, retention controls, integration support, monthly reliability review. |
| Business | Multiple teams with governance and audit requirements | $5,000–$10,000/month | SSO/RBAC, durable audit storage, environment separation, policy versioning, provider adapters, SLA, quarterly control review, priority support. |
| Enterprise | Regulated or high-volume organizations | Custom annual contract, typically $75k–$200k ARR starting range | Private deployment, data residency, dedicated tenant, custom integrations, security review support, uptime and response commitments, implementation services. |
| Advisory / implementation | Teams that need help designing controls | $15k–$40k fixed engagement | Threat model, policy taxonomy, integration into one agent workflow, benchmark design, reviewer operating procedure, handoff documentation. |

The proposed prices are **business hypotheses for client discovery**, not claims about competitor list prices or automatic license grants. The pricing logic separates limited evaluation from paid risk reduction: governance, durable audit, support, private deployment, and integration work create the commercial value.

## Value proposition by buyer

| Buyer | Pain | Honest Agent outcome |
|---|---|---|
| CTO / VP Engineering | Production launch is blocked by uncertainty around agent side effects. | A reviewable control boundary and evidence package for go-live decisions. |
| AI platform engineer | Bespoke guards are duplicated across frameworks and tools. | One normalized contract with proxy, SDK, MCP, and IDE adoption paths. |
| Security / compliance | Logs show what happened but not why an action was allowed. | Decision traces with context ratio, confidence, policy reason, reviewer, and final action. |
| Product owner | Human review can destroy workflow speed. | Risk-based escalation so low-risk actions stay fast while consequential actions pause. |

## Commercial motion

The first sale should be a **two-week control-readiness pilot**, not a broad platform replacement. The pilot instruments one real or sanitized workflow, defines the customer’s action taxonomy, runs a shared baseline-versus-guard benchmark, and produces a go-live recommendation. The pilot converts to Team or Business when the customer wants durable policy management, shared review operations, or retained audit evidence.

The sales conversation should begin with a consequential action map: what can the agent read, change, send, delete, publish, or spend? The demo should then show one action that proceeds, one that pauses, and one that is approved by a reviewer. Avoid selling a generic “AI accuracy” promise. Sell **controlled execution, attributable approval, and shorter security review cycles**.

## Expansion path

Expansion follows operational complexity rather than raw token volume: one workflow to multiple workflows; local JSON to durable audit storage; one team to organization-wide policy; self-hosted to supported private deployment; and technical integration to formal control evidence. Usage-based pricing can be added later for very high check volume, but request volume should not be the primary early pricing axis because the customer’s willingness to pay is driven by consequence and governance, not merely tokens.

## Differentiation and defensibility

Honest Agent is differentiated by its narrow control objective, framework-neutral normalized trajectory schema, deterministic action gate, and explicit distinction between verifier confidence and authorization. The durable moat will not be a keyword list or a single model provider. It will be the customer’s policy taxonomy, labeled checkpoint outcomes, integration depth, and evidence of reduced unsafe execution across real workflows.

## Proof plan for sales

A credible proof package should contain the customer’s baseline pass-through result, a shared fixture set, the guard’s confusion matrix, p50/p95 decision latency, the percentage of actions requiring review, sample trajectory records, and a written list of what the guard does not protect. Any claim should be tied to a reproducible run; “100% catch rate” must always be qualified by the case set and verifier configuration.

## Sources

[1]: https://developers.cloudflare.com/ai-gateway/reference/pricing/ "Cloudflare AI Gateway pricing"
[2]: https://arize.com/pricing/ "Arize AX pricing"
[3]: https://portkey.ai/buyers-guide/leading-llm-gateway-platforms "Portkey / Prisma AIRS AI Gateway buyer guide"
