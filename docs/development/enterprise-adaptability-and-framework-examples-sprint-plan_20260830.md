# HonestAgent Enterprise Adaptability and Framework Examples

## Status

**Draft for review only.** No application features are implemented by this plan, and no commit is proposed until the plan is approved.

## Objective

Extend HonestAgent from a generic pre-execution guardrail into an adaptable enterprise control plane for healthcare, financial trading, recruiting and HR, forecasting, ecommerce, and customer support while preserving one generic runtime contract. Provide five practical integration examples showing how applications built with mainstream agent frameworks can add HonestAgent before tool execution without surrendering framework ownership, provider choice, or human approval authority.

## MVP contract

> For teams operating AI agents with consequential tools, HonestAgent evaluates a normalized action proposal against configurable domain policy, context and verifier controls, and returns a fail-closed decision or signed execution handoff before the caller—not HonestAgent—executes the tool.

Everything below must preserve this contract. HonestAgent must not become an industry-specific workflow engine, autonomous executor, replacement identity provider, trading system, clinical system, ATS, CRM, or support platform.

## Non-negotiable enterprise fears to address

The domain packs and examples must make the following controls explicit and testable:

| Fear | Required control |
|---|---|
| An agent takes an irreversible action without approval | Action classification, explicit policy, human checkpoint, signed expiring handoff, and caller-side enforcement |
| The agent acts outside its permitted business scope | Tenant/domain policy, tool and argument constraints, scope checks, and unknown-action fail-closed behavior |
| Prompt injection changes the agent's authority | Treat instructions and retrieved content as untrusted evidence; never derive authorization from model text |
| The agent leaks confidential or regulated data | Data classification, field-level redaction, egress policy, minimization, retention, and safe audit records |
| The agent makes a high-impact decision with weak evidence | Evidence requirements, confidence thresholds, verifier escalation, disagreement fail-closed behavior, and mandatory review |
| The agent repeats or duplicates a transaction | Idempotency key, replay detection, request binding, expiry, and durable decision state |
| Operators cannot explain or reverse an action | Immutable or tamper-evident audit events, policy version, reviewer identity, reason codes, and rollback evidence |
| A compromised integration bypasses the guard | Adapter contract tests, signed handoff validation, executor inventory, negative bypass tests, and least-privilege deployment |
| The system fails open during provider, storage, or network failure | Explicit `REJECTED`, `PAUSED`, or `CAP_EXCEEDED` outcomes, bounded retries, cancellation handling, and no unverified success |
| Broad rollout creates unknown blast radius | Tenant-scoped rollout, dry-run/simulation mode, kill switch, rate and spend caps, canary scope, and stop conditions |

## Proposed architecture

### Preserve the generic kernel

The existing core remains domain-neutral. The minimum stable kernel contract is:

1. `EvaluationRequest` carries the normalized proposal and metadata.
2. `ActionPolicy` classifies the tool and determines escalation.
3. `ContextEvaluator` and verifier providers assess context sufficiency and risk.
4. `HonestGuard` produces a decision, persists checkpoint state, and issues a signed handoff only when permitted.
5. `PolicyRegistry` manages signed versioned policy lifecycle.
6. SDK, HTTP, and MCP interfaces remain transport adapters.

### Add configuration, not forks

Introduce a versioned, validated `DomainPolicyPack` or equivalent configuration layer that composes with `ActionPolicy`:

- domain identifier and pack version;
- action taxonomy and default classification;
- required approval roles and quorum;
- data classifications and egress rules;
- evidence and freshness requirements;
- limits for amount, quantity, recipients, geography, time window, and rate;
- idempotency and replay requirements;
- mandatory simulation and rollout mode;
- domain-specific reason codes and escalation rules;
- kill-switch and stop-condition references.

The core should consume normalized policy decisions rather than branching on industry names. Domain packs should be declarative wherever possible. Domain-specific validators must be isolated, deterministic, independently testable, and unable to authorize execution by themselves.

### Add a thin framework adapter contract

Each framework example should implement the same conceptual adapter:

```text
framework tool proposal
  -> normalize to EvaluationRequest
  -> await HonestGuard.evaluate()
  -> if PROCEED: require and validate signed handoff
  -> if PAUSED: persist trajectory and wait for reviewer
  -> otherwise: do not call the framework tool
  -> execute only in the caller-owned tool boundary
```

Adapters must not duplicate policy logic, bypass signed handoffs, retry with altered arguments after a pause, or claim tool success when HonestAgent rejected or paused the action.

## Domain adaptability workstreams

Each domain pack follows the same implementation and evidence shape: taxonomy, policy schema, validators, synthetic fixtures, adversarial cases, example policy, dry-run report, and limitations. Domain packs are not production regulatory certification.

### D1 — Healthcare

Initial scope: clinical-support and healthcare operations, not autonomous diagnosis or treatment.

Representative actions:

- read patient record;
- summarize encounter;
- draft—not send—patient communication;
- schedule appointment;
- update administrative demographics;
- submit claim for review;
- access or export protected health information;
- recommend clinical action for qualified human review.

Controls and edge cases:

- minimum-necessary data and purpose-of-use checks;
- patient/tenant/role scope;
- emergency override as an explicitly logged, time-bounded exception;
- consent and proxy-access states;
- clinician approval for diagnosis, treatment, medication, or patient-facing advice;
- stale or conflicting records;
- protected-health-information redaction and egress blocks;
- duplicate appointment, claim, or message prevention.

Hard stop: no autonomous clinical order, prescription, diagnosis, or treatment execution in examples.

### D2 — Financial trading

Initial scope: pre-trade proposal controls, not a trading engine or investment adviser.

Representative actions:

- market-data lookup;
- portfolio/read-only exposure query;
- draft order;
- submit order for approval;
- cancel or amend order;
- rebalance proposal;
- transfer or settlement action.

Controls and edge cases:

- instrument, account, venue, side, quantity, notional, price-band, and time-in-force validation;
- pre-trade limits, credit and buying-power references;
- stale quote and market-closed checks;
- duplicate order and replay prevention;
- human approval for configured order classes and all transfers;
- kill switch, rate limit, loss/notional cap, and canary account scope;
- restricted list, market-abuse-sensitive workflow, and emergency cancel handling;
- explicit separation between recommendation, order preparation, and submission.

Hard stop: HonestAgent never submits a trade or represents market compliance; live execution evidence remains deployment-owned.

### D3 — Recruiting and HR

Initial scope: workflow assistance and administrative actions, not autonomous employment decisions.

Representative actions:

- search candidates;
- summarize a resume against a role;
- draft outreach;
- schedule an interview;
- update ATS stage;
- request references;
- draft offer or rejection communication.

Controls and edge cases:

- protected-attribute and proxy-feature minimization;
- consent and source-purpose checks;
- recruiter/hiring-manager approval boundaries;
- explainable rubric and evidence references;
- duplicate candidate and duplicate-contact prevention;
- candidate communication approval;
- retention/deletion requests and jurisdictional restrictions;
- no autonomous reject, rank, hire, fire, compensation, or promotion decision.

### D4 — Forecasting

Initial scope: planning and decision support, not automatic financial or capacity commitment.

Representative actions:

- retrieve historical series;
- generate forecast;
- publish forecast draft;
- update planning assumptions;
- create scenario;
- approve a forecast version;
- trigger downstream planning workflow.

Controls and edge cases:

- dataset version, timestamp, lineage, and freshness;
- missing, sparse, shifted, or contradictory data;
- forecast horizon and confidence interval requirements;
- scenario versus committed plan distinction;
- approval for publication and downstream commitment;
- leakage prevention between training and evaluation periods;
- reproducible model/prompt/configuration references;
- rollback to prior forecast version.

### D5 — Ecommerce

Initial scope: safe catalog, order, and customer-service operations with financial and inventory guardrails.

Representative actions:

- product/catalog lookup;
- inventory read;
- cart update;
- order draft;
- discount proposal;
- refund request;
- cancellation or address change;
- shipment or fulfillment update.

Controls and edge cases:

- customer authentication and order ownership;
- price, discount, inventory, and margin limits;
- refund threshold and payment-method restrictions;
- duplicate order/refund prevention;
- shipping address and fraud-risk changes;
- promotional abuse and coupon scope;
- customer-data redaction and vendor egress;
- approval for high-value refunds, irreversible cancellations, and account changes.

### D6 — Customer support

Initial scope: agent-assisted support, not unrestricted account or financial remediation.

Representative actions:

- retrieve account/ticket status;
- draft response;
- classify or route ticket;
- update non-sensitive ticket fields;
- issue approved knowledge-based guidance;
- refund/credit request;
- account recovery or entitlement change.

Controls and edge cases:

- authenticated customer and ticket scope;
- knowledge freshness and source citation;
- escalation for legal, safety, privacy, abuse, or vulnerable-customer signals;
- refund/credit thresholds;
- account recovery and identity-proofing boundaries;
- no secret collection in prompts or logs;
- duplicate response and duplicate remediation prevention;
- handoff to a human with preserved context and reason codes.

## Five framework examples

Each example should be a small runnable project or self-contained example with local deterministic stubs, no provider credentials, no real side effects, and a README containing setup, flow, failure cases, and a production-hardening checklist.

### E1 — LangChain tool wrapper

Show a `StructuredTool` or equivalent wrapper that normalizes tool name, arguments, context, and agent metadata, calls HonestAgent before the underlying Python function, raises a typed pause/rejection result, and validates the signed handoff before execution.

Test cases: safe lookup proceeds; write pauses; unknown tool rejects; altered arguments invalidate the handoff; provider failure does not execute.

### E2 — LangGraph state-machine node

Show a graph with explicit `propose -> guard -> human_review? -> execute` nodes. Persist `trajectory_id` in graph state, route `PAUSED` to an interrupt/checkpoint, and prevent an edge from reaching execution without a valid handoff.

Test cases: refresh/resume, duplicate resume, approval/rejection, expired handoff, and graph state tampering.

### E3 — CrewAI task/tool integration

Show a crew tool boundary where an agent may propose an action but only a guarded wrapper can call the actual tool. Demonstrate role/task metadata mapping and a human-review callback without giving the crew unrestricted executor access.

Test cases: delegated tool proposal, role mismatch, irreversible action, and no fallback execution after rejection.

### E4 — Microsoft AutoGen or AG2 function tool

Show a function-tool adapter that returns a normalized decision to the conversation, stops automatic continuation on `PAUSED` or `REJECTED`, and requires an explicit reviewer message plus handoff validation before calling the function.

Test cases: multi-agent proposal, conflicting proposals, bounded retries, cancellation, and malicious tool-result content.

### E5 — LlamaIndex agent tool / workflow

Show a workflow or tool callback integrating the guard before a retrieval-backed action. Separate untrusted retrieved text from authorization metadata and demonstrate evidence/freshness requirements for a high-impact action.

Test cases: prompt injection in retrieved content, stale evidence, sensitive retrieval egress, and human approval for downstream mutation.

If a framework has materially changed APIs at implementation time, pin a tested version and clearly label the example. Do not claim support for every version.

## Execution sequence

### Sprint EA-0 — Contract and threat model

Deliverables:

- stable normalization contract for domain packs and framework adapters;
- threat model covering authority confusion, prompt injection, data leakage, replay, duplicate execution, and fail-open paths;
- compatibility decision for domain-policy composition;
- ADR documenting why domain logic stays outside the generic kernel.

Acceptance:

- no proposed domain rule requires industry branching inside `HonestGuard`;
- every adapter has one pre-execution enforcement point;
- all consequential actions require a verifiable handoff or checkpoint resolution.

### Sprint EA-1 — Domain policy-pack foundation

Deliverables:

- validated policy-pack schema and loader;
- tenant/domain/version selection;
- deterministic validator interface;
- signed import, simulation, approval, activation, rollback, and audit integration;
- generic reason-code and evidence model.

Acceptance:

- malformed, unsigned, unauthorized, or ambiguous packs fail closed;
- old active policy remains available during failed activation;
- policy version is present in every decision and audit record;
- no secrets or raw prompts are exported by simulation.

### Sprint EA-2 — Healthcare and HR packs

Deliverables:

- healthcare and recruiting/HR packs;
- synthetic sanitized fixtures;
- adversarial tests and dry-run reports;
- explicit prohibited-action catalog;
- one integration example reused against both packs.

Acceptance:

- no autonomous clinical or employment decision path can reach execution;
- PHI and protected employment data are minimized/redacted in evidence;
- role, purpose, consent, and approval failures are deterministic.

### Sprint EA-3 — Trading and forecasting packs

Deliverables:

- pre-trade and forecast policy packs;
- market/data freshness and lineage validators;
- cap, replay, duplicate, kill-switch, and rollback tests;
- synthetic proposal fixtures only.

Acceptance:

- no test or example sends a live order or commits a plan;
- stale/contradictory data pauses or rejects;
- notional, quantity, horizon, and account scope limits are enforced before handoff.

### Sprint EA-4 — Ecommerce and customer-support packs

Deliverables:

- ecommerce and support policy packs;
- refund, account-change, identity, and escalation rules;
- sensitive-data and knowledge-freshness fixtures;
- dry-run reports and stop-condition drills.

Acceptance:

- duplicate refund/order/account changes are blocked;
- high-impact remediation requires approval;
- untrusted customer or retrieved text cannot change authority.

### Sprint EA-5 — Framework examples 1–3

Deliverables:

- LangChain, LangGraph, and CrewAI examples;
- pinned dependencies and local deterministic stubs;
- adapter contract test suite;
- README quickstarts and failure-mode demonstrations.

Acceptance:

- each example runs from a clean checkout without provider credentials;
- each example demonstrates proceed, pause, reject, provider failure, and altered-argument rejection;
- no framework tool executes when HonestAgent returns `PAUSED`, `REJECTED`, or `CAP_EXCEEDED`.

### Sprint EA-6 — Framework examples 4–5 and compatibility review

Deliverables:

- AutoGen/AG2 and LlamaIndex examples;
- version compatibility matrix;
- common adapter conformance tests;
- integration security review.

Acceptance:

- all five examples expose the same normalized decision semantics;
- framework-specific state persistence cannot bypass handoff validation;
- examples clearly separate local demonstration from production claims.

### Sprint EA-7 — Cross-domain assurance and release evidence

Deliverables:

- matrix of domains × action classes × controls × tests;
- full regression and adversarial suite;
- clean-checkout reproduction for all examples;
- SBOM and dependency scan for optional example dependencies;
- documentation, changelog, threat-model update, and release decision.

Acceptance:

- no unsupported production or regulatory-certification claims;
- every known limitation is recorded;
- all examples and packs are opt-in and disabled by default unless explicitly configured;
- conditional-pilot evidence distinguishes synthetic, local, and live deployment results.

## Configuration and packaging strategy

Start with one repository and one generic kernel. Package domain packs as versioned configuration modules or optional extras only after the shared schema stabilizes. Keep framework examples in separate directories with isolated dependency constraints so installing one integration does not destabilize the core runtime.

Recommended layout:

```text
honest_agent/
  core/                       # generic enforcement kernel
  domain/                     # validated domain-pack contracts and built-ins
  adapters/                   # framework-neutral adapter contract
examples/
  langchain/
  langgraph/
  crewai/
  autogen/
  llamaindex/
fixtures/
  domains/
  framework_examples/
```

The examples should depend on the published or local package interface, not import private internals. Each example must have a `requirements.txt` or equivalent pinned environment and a no-credential test command.

## Evidence and quality gates

| Gate | Evidence required |
|---|---|
| Genericity | Kernel tests pass without any domain pack installed; no industry conditionals in core orchestration |
| Adaptability | Six domain packs validate, simulate, and fail closed on prohibited/ambiguous cases |
| Safety | Negative tests prove no direct execution, no altered-argument replay, no duplicate transaction, and no fail-open provider path |
| Privacy | Sanitized fixtures, redacted trajectories, secret scans, and egress/data-classification tests |
| Reproducibility | Clean-checkout commands for core plus all five examples |
| Framework value | Each example demonstrates the same decision contract and framework-native pause/resume behavior |
| Enterprise readiness | Policy signing/quorum/rollback, reviewer identity, audit integrity, kill switch, limits, and deployment assumptions documented |
| Honesty | Synthetic/local/live evidence is labeled separately; no fabricated customer or regulatory validation |

## Out of scope for this phase

- Autonomous execution of healthcare, trading, hiring, financial, refund, account-recovery, or other consequential actions.
- Building connectors to production EHRs, brokerages, ATSs, ERP systems, commerce platforms, or support systems.
- Regulatory certification, legal advice, clinical validation, investment advice, employment-law determinations, or security guarantees beyond tested controls.
- A universal policy language that attempts to encode every customer’s business rules in the first release.
- Supporting every version of every framework.

## Decisions requested before implementation

1. Approve the six-domain scope and the explicit prohibited-action boundaries.
2. Choose whether the first implementation should prioritize healthcare + HR, trading + forecasting, or a balanced vertical slice.
3. Confirm the five framework targets. Recommended set: LangChain, LangGraph, CrewAI, AutoGen/AG2, and LlamaIndex.
4. Confirm whether domain packs should ship in the core package initially or as optional extras/configuration bundles.
5. Confirm that all examples remain synthetic and side-effect-free until separate deployment evidence and customer authorization exist.
6. Confirm the commercial boundary: examples may document integration, but licensed client deployments must follow the repository’s commercial licensing terms.

## Review checkpoint

This document is intentionally uncommitted. Implementation should begin only after the decisions above are resolved and the accepted scope is recorded in an ADR and sprint trace.
