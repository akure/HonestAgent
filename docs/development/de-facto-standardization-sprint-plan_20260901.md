# HonestAgent De Facto Standardization Sprint Plan

## Purpose

This plan turns HonestAgent from a strong safety implementation into a broadly reusable **agent workflow control protocol and reference control plane**. The objective is not to replace LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex, or custom orchestrators. The objective is to make HonestAgent the neutral layer that normalizes intent, evidence, policy, approval, handoff, and execution safety across them.

The plan is deliberately sequential. Each sprint produces one reviewable checkpoint with tests, documentation, and an explicit release decision before the next sprint begins.

## Strategic position

HonestAgent should be treated as four related products:

| Layer | Role | Adoption strategy |
|---|---|---|
| Control protocol | Versioned schemas and semantics for workflow context, tool intent, evidence, decisions, handoffs, and events | Stable interoperability contract; easy to implement independently |
| Reference kernel | Generic fail-closed evaluation, policy, checkpoint, handoff, and executor boundary | High-quality reference implementation with strong tests |
| Conformance kit | Golden fixtures and adversarial tests that prove compatible implementations | Public ecosystem trust and compatibility badge |
| Enterprise control plane | Durable storage, identity, approvals, audit, quotas, operations, managed policy, and support | Commercial differentiation and deployment value |

The protocol and conformance surface must be sufficiently open and documented for independent implementations. Enterprise operational services, advanced domain assurance, managed hosting, and support may remain commercially controlled under the repository’s licensing strategy.

## Current state at planning time

The synchronized remote branch already contains the first workflow-safety foundation:

| Capability | Current state | Evidence |
|---|---|---|
| Workflow contracts | Implemented | `honest_agent/schemas/workflow.py`, CX-0 trace |
| Durable workflow budgets | Implemented | `honest_agent/core/budgets.py`, CX-1 trace |
| Workflow-bound handoff v2 | Implemented | `honest_agent/core/handoff.py`, CX-2 trace |
| First-class RAG evidence boundary | Implemented in-memory foundation | `honest_agent/core/rag.py`, CX-3 trace |
| Six domain policy packs | Implemented as synthetic opt-in artifacts | `examples/domain_packs/` |
| Five framework-shaped adapters | Implemented as dependency-free examples | `examples/{langchain,langgraph,crewai,autogen,llamaindex}/` |
| Protocol governance and public conformance kit | Not yet complete | This plan |
| Production workflow persistence and operational control plane | Not yet complete | This plan |

The current evidence is local and synthetic. It does not establish production authorization, regulatory certification, customer validation, or safe autonomous execution of consequential actions.

## Non-negotiable principles

1. **The protocol must be framework-neutral.** Framework adapters translate into the protocol; they do not create alternate authorization paths.
2. **Model output and retrieved content remain untrusted.** Neither can grant tenant identity, reviewer identity, policy authority, or execution permission.
3. **Stricter policy wins.** Platform, tenant, domain, workflow, tool, and step restrictions must compose monotonically.
4. **Every consequential action is state-bound.** Run, step, attempt, tenant, policy snapshot, evidence snapshot, destination, and expiry must be part of the authorization boundary.
5. **Safe adoption must be easier than custom safety code.** The first demo should run locally with no credentials, and the first integration should require only one guarded boundary.
6. **Evidence categories remain separate.** Synthetic, local, independent reproduction, pilot, and production evidence must never be combined into one misleading score.
7. **No standard claim without external adoption.** Until independent users or implementations exist, describe the project as a proposed protocol and reference implementation.

## Sprint sequence

### STD-0 — Protocol governance and public contract boundary

**Objective:** Convert the existing CX contracts into a clearly versioned public protocol surface.

**Deliverables:**

- `honestagent.control.v1` protocol overview;
- normative field and state-transition definitions for `WorkflowRunContext`, `ToolIntent`, `EvidenceEnvelope`, `DecisionRecord`, `ExecutionHandoffV2`, and `ControlEvent`;
- canonicalization and compatibility rules;
- trust-boundary and threat-model document;
- deprecation, version negotiation, and extension policy;
- decision record separating protocol, reference kernel, conformance kit, and enterprise services.

**Acceptance criteria:** An independent implementer can understand the minimum valid request/decision/handoff exchange without reading private source code. Unknown major versions, ambiguous extensions, malformed envelopes, and missing trust metadata fail closed. No protocol field allows model or retrieved text to become authority.

### STD-1 — Golden fixtures and conformance kit

**Objective:** Make compatibility measurable rather than aspirational.

**Deliverables:**

- versioned JSON golden fixtures;
- canonical hash and signature vectors;
- expected `PROCEED`, `PAUSED`, `REJECTED`, `CAP_EXCEEDED`, and provider-failure cases;
- altered-argument, altered-tenant, stale-evidence, cross-tenant, replay, duplicate-resume, and delegation-escalation fixtures;
- a language-neutral test manifest and result format;
- `honestagent-conformance` command or equivalent test entry point.

**Acceptance criteria:** The reference implementation passes every fixture; fixture results are deterministic across runs; a deliberately weakened implementation fails the negative cases; no fixture contains credentials, raw protected content, or live side effects.

### STD-2 — Python developer experience and CLI

**Objective:** Make safe adoption simple for Python builders.

**Deliverables:**

- stable `honest_agent` public imports;
- `check(intent)`, guarded-tool, and workflow-context helpers;
- CLI initializer and local demo commands;
- typed exception/result semantics;
- migration guide from direct tool calls;
- examples for a custom Python agent and a RAG workflow.

**Acceptance criteria:** A clean checkout can install the package and run a safe read, paused mutation, rejected action, stale-evidence case, and altered-handoff case with no credentials or network. Public imports are tested, documented, and covered by compatibility tests.

### STD-3 — RAG safety reference workflow

**Objective:** Make complex RAG safety the flagship demonstration and reference architecture.

**Deliverables:**

- retrieval source and tenant boundary;
- evidence snapshot and citation binding;
- freshness, lineage, classification, and egress controls;
- prompt-injection signal handling;
- separation of retrieved content from authorization-bearing evidence;
- redacted audit output;
- synthetic support/ecommerce workflow: retrieve → cite → propose → guard → approve → resume → execute stub.

**Acceptance criteria:** Cross-tenant chunks, stale evidence, disallowed egress, missing high-impact citations, and injection-bearing content cannot authorize execution. A retrieved instruction cannot change tenant, reviewer, policy, or tool authority. The complete workflow is reproducible offline.

### STD-4 — Durable workflow state and human oversight

**Objective:** Make long-running workflows resumable without resetting safety state.

**Deliverables:**

- explicit state machine for proposal, guard, pause, approval, rejection, expiry, resume, execution, cancellation, compensation, and completion;
- durable state transitions;
- approval scoped to intent, evidence, policy, run, step, and attempt;
- reviewer authentication and role checks;
- cancellation and duplicate-resume behavior;
- re-evaluation when policy, evidence, or state changes.

**Acceptance criteria:** No state transition reaches execution without a current valid handoff. Approval cannot be reused for changed arguments or evidence. Refresh, worker restart, duplicate resume, timeout, cancellation, and expiry tests are deterministic.

### STD-5 — Policy composition and delegation attenuation

**Objective:** Control multi-agent and multi-policy workflows without industry branching in the kernel.

**Deliverables:**

- effective-policy resolver for platform, tenant, domain, workflow, tool, and step layers;
- conflict explanations and immutable policy snapshots;
- child-agent capability attenuation;
- workflow-level cumulative amount, fan-out, retrieval, concurrency, and deadline limits;
- simulation output containing redacted references only.

**Acceptance criteria:** A child cannot add tools, extend a deadline, broaden tenant scope, increase limits, or weaken a parent restriction. Aggregate limits hold under concurrency and retries. Effective policy and conflict reason are present in decisions and audit events.

### STD-6 — Reliable execution semantics and operational controls

**Objective:** Make the control plane usable around real workers and external systems without claiming impossible guarantees.

**Deliverables:**

- transactional intent inbox/outbox;
- explicit at-most-once or idempotent at-least-once semantics by tool class;
- retry, timeout, cancellation, circuit-breaker, and compensation states;
- tenant/workflow/tool kill switch;
- health and quota state;
- crash, recovery, and duplicate-side-effect drills.

**Acceptance criteria:** Provider failure never creates false success. Crash/retry tests do not duplicate protected mutations where idempotency is available. Where exactly-once cannot be guaranteed, the limitation and selected execution semantics are explicit.

### STD-7 — Version-pinned framework integrations

**Objective:** Prove that the protocol protects actual framework execution paths, not only framework-shaped examples.

**Deliverables:**

- one pinned integration for a graph framework;
- one pinned integration for a RAG workflow;
- additional LangChain, CrewAI, AutoGen/AG2, and LlamaIndex integrations as capacity permits;
- framework-native pause/resume, streaming, cancellation, and state-persistence tests;
- compatibility matrix and unsupported-version policy.

**Acceptance criteria:** Actual framework state cannot bypass the control plane. Every supported version demonstrates proceed, pause, reject, provider failure, stale evidence, prompt injection, cancellation, and altered-handoff rejection. Unsupported versions are clearly labeled.

### STD-8 — Independent reproduction and benchmark evidence

**Objective:** Establish credibility through repeatable, externally understandable measurement.

**Deliverables:**

- safety, integrity, reliability, RAG, latency, precision, and developer-experience benchmark definitions;
- clean-checkout reproduction guide;
- independent implementer or reviewer reproduction protocol;
- benchmark result schema separating synthetic, local, pilot, and production evidence;
- baseline comparison against unguarded tool execution on identical cases.

**Acceptance criteria:** An independent party can reproduce the reported results from a clean checkout. Metrics include false pauses and false proceeds, not only blocked-action counts. No fabricated customer, regulatory, or production claims appear in the report.

### STD-9 — Ecosystem and protocol adoption

**Objective:** Create ecosystem gravity without overstating standard status.

**Deliverables:**

- protocol website or repository landing section;
- implementation guide for non-Python clients;
- TypeScript/HTTP reference client;
- conformance badge rules;
- adapter template;
- issue and proposal process for protocol changes;
- public compatibility and adoption page.

**Acceptance criteria:** At least one independent implementation or adapter passes the conformance kit. Version negotiation and deprecation rules are exercised. The project claims “conformant implementation” only for measured results and does not claim de facto standard status prematurely.

### STD-10 — Enterprise control plane and commercial packaging

**Objective:** Monetize operational assurance while preserving interoperability.

**Deliverables:**

- managed policy registry;
- enterprise identity and reviewer governance;
- immutable audit and evidence retention;
- dashboards, alerting, and kill-switch operations;
- domain assurance packs;
- hosted/private-deployment/OEM packaging;
- commercial deployment evidence and support model.

**Acceptance criteria:** Enterprise services are separable from the protocol and reference kernel. Tenant isolation, identity revocation, audit retrieval, recovery, egress, secrets, monitoring, and rollback are evidenced in a target-like environment. Pricing and license boundaries do not imply safety certification.

## Definition of done for every sprint

A sprint is not complete when code merely exists. It is complete only when the checkpoint has:

| Requirement | Evidence |
|---|---|
| Implementation | Small focused diff with public boundary identified |
| Safety | Positive and adversarial regression tests |
| Reproducibility | Exact clean-checkout command |
| Documentation | README/API/design note and limitation statement |
| Security | Threat, mitigation, residual-risk review |
| Operations | Rollback or disable path |
| Measurement | Test result and evidence class |
| Governance | Change log, sprint trace, reviewer decision, and immutable commit |

## Release gates

| Gate | Minimum condition |
|---|---|
| Protocol preview | STD-0 and STD-1 complete; reference implementation passes conformance fixtures |
| Developer preview | STD-2 and STD-3 complete; offline demos and public imports stable |
| Workflow-safety foundation | STD-4 through STD-6 complete; recovery and duplicate-execution evidence available |
| Integration preview | STD-7 complete for explicitly pinned versions |
| Independent-conformance release | STD-8 and at least one external reproduction complete |
| Ecosystem standard candidate | STD-9 complete with independent implementation and version governance |
| Enterprise pilot | STD-10 deployment evidence complete; accountable owner accepts residual risk |

## Immediate next sprint

The next implementation sprint should be **STD-0**, but it should be executed after the already completed CX-0 through CX-3 foundation is reviewed and treated as its implementation input. It should not add another safety mechanism in parallel. Its job is to publish the stable protocol boundary, compatibility rules, and conformance-oriented terminology that the later SDK, RAG workflow, framework integrations, and enterprise control plane will all share.

## Strategic outcome

HonestAgent becomes valuable as a de facto standard only when developers can adopt it without changing their preferred framework, independent implementers can verify compatibility, and enterprise operators can purchase stronger governance without fragmenting the protocol. The sequence above therefore prioritizes **interoperability, evidence, and developer value before commercialization**.

## Current release posture

The repository remains a tested workflow-safety foundation, not unrestricted production authorization. Synthetic and local evidence demonstrate implementation behavior but do not establish regulatory compliance, customer validation, or safe autonomous execution of consequential actions.
