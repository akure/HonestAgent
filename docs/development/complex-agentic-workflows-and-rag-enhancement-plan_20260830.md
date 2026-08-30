# HonestAgent Core Enhancement Analysis and Plan

## Executive summary

HonestAgent currently provides a credible safety boundary for a guarded tool call: it normalizes an evaluation request, evaluates context and action risk, applies optional domain policy, pauses for human review when required, issues a request-bound handoff, and validates that handoff before execution. The domain-pack and framework-example work has extended that foundation without adding industry-specific branches to the kernel.

For builders creating complex agentic workflows and retrieval-augmented generation (RAG) systems, the next limitation is not the absence of more action rules. The limitation is that the current safety decision is still primarily **single-request oriented**, while real systems are multi-step, stateful, partially observed, asynchronous, retried, resumed, delegated, and exposed to untrusted retrieved content. The recommended direction is therefore to evolve HonestAgent into a **workflow control plane** while preserving a small generic fail-closed kernel.

The first implementation should establish a durable, request-bound execution context and an evidence model. Subsequent workflow, RAG, policy, and adapter features should compose with those contracts rather than create parallel authorization paths.

## Current baseline and boundary

The existing implementation has several valuable properties. `HonestGuard` applies domain evaluation before verifier execution, fails closed when verification fails, records pending and resolved checkpoints, issues signed handoffs, and validates the handoff against the original request. `EvaluationRequest` already carries agent, context, tool, policy, and metadata fields. The domain evaluator provides tenant scope, deterministic constraints, evidence requirements, idempotency, review, and prohibited-action controls. The current framework examples reuse a single pre-execution adapter boundary.

The existing contract is documented in the approved [Domain Policy Pack schema][1] and the enterprise sprint plan [2]. This report does not propose weakening those controls. It proposes adding lifecycle and evidence structure around them.

## Capability-gap analysis

| Area | Current capability | Realistic complex-agent requirement | Risk if unchanged | Priority |
|---|---|---|---|---|
| Workflow identity | A trajectory ID is generated per decision; requests are largely standalone. | Durable workflow/run ID, parent-child step IDs, attempt IDs, actor identity, tenant, and correlation across asynchronous steps. | A resumed or delegated step can be confused with a new action; audit reconstruction is incomplete. | P0 |
| Intent and tool input | `tool_input` is a dictionary and constraints inspect selected fields. | Typed tool-intent envelope with schema/version, normalized arguments, declared side-effect class, destination, resource scope, and idempotency key. | Ambiguous or malformed tool calls reach policy evaluation; altered semantics can hide inside unmodeled fields. | P0 |
| Evidence | Evidence is a caller-supplied mapping, with basic presence, age, and contradiction markers. | Signed or attributable evidence envelopes containing source, provenance, timestamp, lineage, trust class, freshness, classification, and transformation history. | Retrieved text or stale context can be mistaken for authorization or current truth. | P0 |
| RAG safety | Generic context evaluation and redaction exist; no first-class retrieval/chunk/source model. | Retrieval boundary that separates untrusted content from authorization metadata, detects injection patterns, enforces source/tenant/egress rules, and binds citations to the final action. | Prompt injection, cross-tenant retrieval, stale citations, and sensitive-data egress are under-modeled. | P0 |
| Multi-step policy | Domain evaluator decides one action at a time. | Workflow-level invariants: allowed transitions, cumulative spend/quantity, step budgets, deadlines, fan-out limits, and approval scope. | A sequence of individually acceptable actions can create an unacceptable aggregate outcome. | P1 |
| Checkpoints | Pending/resolved checkpoint stores exist; approval returns a handoff. | Typed pause reasons, reviewer authorization, approval scope, expiry, re-evaluation on resume, cancellation, and duplicate-resume semantics. | Approval may be replayed against changed state or used outside its intended scope. | P1 |
| Execution reliability | Handoff validation protects the executor; idempotency is policy-dependent. | Transactional outbox/inbox, exactly-once intent recording where possible, explicit at-most-once/at-least-once semantics, compensation and recovery states. | Retries, refreshes, timeouts, and worker crashes can duplicate or orphan side effects. | P1 |
| Delegation | Agent metadata is present but delegation lineage is not a first-class contract. | Delegation chain, capability attenuation, child-agent budget, allowed tools, and non-escalation invariant. | A subagent can acquire broader authority than its parent or obscure responsibility. | P1 |
| Model/provider interaction | Provider failures fail closed; deterministic mock verifier exists. | Provider call envelope, timeout/deadline, bounded retry policy, structured output validation, model/tool-call provenance, and streaming checkpoints. | Long workflows can loop, exhaust budgets, or treat malformed model output as intent. | P1 |
| Policy composition | Generic policy and domain packs are additive, but selection/composition is narrow. | Layered policy resolution: platform, tenant, domain, workflow, tool, and step, with conflict explanation and immutable policy snapshot. | A later layer can accidentally override a stricter earlier layer or audit cannot reproduce the decision. | P1 |
| Observability | Trajectory logging and audit artifacts exist. | Append-only event stream with decision, evidence, policy snapshot, checkpoint, handoff, execution, and recovery events. | Operators cannot reliably answer what was proposed, approved, executed, or retried. | P1 |
| Adapter realism | Five examples demonstrate a common wrapper contract but are dependency-free shapes. | Framework-native state persistence, interrupt/resume, streaming, cancellation, and version-pinned integration tests. | Examples look safe locally but may not protect actual framework execution paths. | P2 |
| Operations | Deployment evidence covers many controls, but runtime control plane is not comprehensive. | Kill switch by tenant/workflow/tool, rate and concurrency quotas, circuit breakers, health state, and operator views. | A runaway workflow can continue until external infrastructure stops it. | P2 |

## Design principles

### Preserve a small generic kernel

The kernel should enforce generic invariants: identity, authorization scope, evidence validity, risk classification, limits, checkpoint resolution, handoff integrity, and execution gating. Industry rules remain policy-pack data or reviewed deterministic plugins. A healthcare, trading, or support-specific branch inside `HonestGuard` would make the system harder to audit and easier to bypass through an unhandled path.

### Treat model output and retrieved content as untrusted proposals

A model may propose a tool call, but it does not grant itself authority. Retrieved documents, web pages, tool results, and user-provided text are evidence candidates or untrusted content; they are not reviewer identity, tenant identity, policy, approval, or execution authorization. The data model should make this distinction structurally difficult to ignore.

### Bind every consequential decision to state

A handoff must bind not only tool name and payload hash, but also workflow run, step, tenant, policy snapshot, evidence snapshot, authorization scope, and expiry. A resume operation should revalidate state and evidence rather than blindly replaying an old approval.

### Prefer explicit uncertainty over optimistic automation

Unknown, stale, contradictory, incomplete, or unavailable evidence should produce a typed pause or rejection. The system should expose why a workflow stopped and what evidence or reviewer action is required, without exporting raw prompts or sensitive retrieved content.

## Target architecture

```text
framework / agent / RAG application
                |
        normalized proposal
                v
      Workflow Control Context
   run · step · actor · tenant · budgets
                |
      Evidence and Retrieval Boundary
 source · provenance · freshness · trust · egress
                |
      Layered Policy Resolution
 platform + tenant + domain + workflow + tool
                |
        Generic HonestGuard kernel
 context · risk · limits · checkpoint · handoff
                |
    durable decision / event / outbox record
                |
      executor or framework continuation
       only after request-bound validation
```

The control plane should expose one normalized API regardless of whether the caller is a graph node, a crew task, a function tool, a RAG workflow, or a custom orchestrator. Framework adapters should translate into the control plane; they should not implement authorization independently.

## Proposed core contracts

### `WorkflowRunContext`

A durable context should contain `run_id`, `tenant_id`, `root_agent_id`, `parent_step_id`, `step_id`, `attempt`, `delegation_chain`, `workflow_version`, `deadline`, `budgets`, `kill_switch_epoch`, and a policy snapshot identifier. It should be immutable for a step once the proposal is evaluated. Child contexts may attenuate capabilities but may not add tools, raise limits, extend deadlines, or change tenant scope.

### `ToolIntent`

`ToolIntent` should replace an unstructured combination of request fields for execution decisions. It should contain the normalized tool identifier, versioned argument schema, canonical arguments, declared action class, resource scope, destination/egress class, idempotency key, expected side-effect mode, and provenance indicating whether the intent came from a model, human, rule, or delegated agent. Canonicalization must be deterministic before hashing and signing.

### `EvidenceEnvelope`

An evidence envelope should contain a stable evidence ID, source ID, source type, tenant scope, content hash, provenance chain, observed-at and expires-at timestamps, trust class, data classification, lineage references, retrieval query ID, citation spans, and a boolean indicating whether the content is authorization-bearing. Authorization-bearing evidence should require a trusted producer or verifier; model-generated summaries should never silently inherit source authority.

### `DecisionRecord` and `ControlEvent`

Every decision should be reproducible from an immutable policy snapshot, normalized intent, workflow context, and evidence references. The record should include decision status, reason codes, risk, limits consumed, checkpoint scope, handoff ID, and redacted references rather than raw prompts. Append-only control events should cover proposal, evaluation, pause, approval, rejection, handoff issue, execution start, execution result, timeout, cancellation, retry, compensation, and kill-switch activation.

## Phased implementation plan

### Phase CX-0 — Contract and threat-model extension

Document and approve the four contracts above, their canonicalization rules, trust boundaries, compatibility strategy, and state-transition diagram. Add adversarial cases for prompt injection, cross-tenant evidence, stale citations, delegation escalation, altered arguments, duplicate resume, and deadline expiry. No framework-specific feature should begin before these contracts are stable.

**Acceptance criteria:** contracts are versioned; sensitive fields are redacted by construction; every consequential action has a run/step/attempt identity; child delegation cannot increase authority; unknown trust or malformed envelopes fail closed.

### Phase CX-1 — Durable workflow context and budgets

Add a generic workflow context and budget manager. Support per-run and per-step limits for verifier calls, tool calls, retries, tokens, wall-clock deadline, fan-out, concurrency, and cumulative domain amounts. Persist context transitions transactionally and make cancellation and kill-switch state visible to every pre-execution check.

**Acceptance criteria:** a workflow cannot exceed any configured budget; refresh/resume does not reset counters; concurrent workers cannot consume the same single-use intent twice; budget exhaustion produces typed `CAP_EXCEEDED` evidence.

### Phase CX-2 — Intent canonicalization and handoff v2

Introduce `ToolIntent` and canonical hashing. Extend the handoff to bind run ID, step ID, attempt, tenant, policy snapshot, evidence snapshot, destination, and expiry. Preserve backward compatibility for the current handoff only where explicitly configured; new consequential actions should use the stronger envelope.

**Acceptance criteria:** semantically altered arguments, destination, tenant, policy, evidence, or workflow step invalidate the handoff; canonicalization is deterministic across processes; old handoffs cannot authorize new attempts.

### Phase CX-3 — First-class RAG evidence boundary

Add retrieval and evidence models without storing raw sensitive content in audit records. Enforce tenant/source scope, classification and egress rules, freshness, lineage, citation coverage, and separation between retrieved text and authorization metadata. Add a deterministic prompt-injection detector as a signal, not as the sole authorization mechanism; suspicious or conflicting content pauses or rejects according to policy.

**Acceptance criteria:** cross-tenant chunks are rejected; stale or contradictory evidence pauses/rejects; retrieved instructions cannot alter reviewer, tenant, policy, or tool authority; high-impact actions require cited, fresh, attributable evidence; redaction tests prove raw protected content does not enter trajectories.

### Phase CX-4 — Workflow state machine and human checkpoints

Provide explicit proposal, guard, pause, approve/reject, resume, execute, compensate, cancel, and expire states. Approval should be scoped to an intent/evidence/policy snapshot and should require reviewer authentication and role checks. Resume should re-evaluate changed evidence and policy, with deterministic duplicate-resume behavior.

**Acceptance criteria:** no edge reaches execution without a valid current handoff; approval of a changed proposal is invalid; cancellation is terminal for that attempt; expired or already-resolved checkpoints cannot execute.

### Phase CX-5 — Policy composition and delegation

Implement layered, explainable policy resolution and capability attenuation for subagents. Add workflow-level invariants and aggregate controls for fan-out, cumulative amount, repeated retrieval, and downstream mutations. Keep domain-specific behavior declarative.

**Acceptance criteria:** effective policy and conflict reason are recorded; stricter rules always win; child agents cannot broaden parent authority; aggregate limits hold under concurrency and retries; simulation exports only redacted references.

### Phase CX-6 — Reliability and execution semantics

Add durable intent inbox/outbox records, explicit execution semantics, timeout/cancellation handling, compensation hooks, circuit breakers, and recovery drills. Document where exactly-once is impossible and select at-most-once or idempotent at-least-once behavior per tool class.

**Acceptance criteria:** crash/retry/timeout tests produce no duplicate protected mutation; provider failure does not create a false success; recovery resumes from a durable state; compensation is never mistaken for rollback success without evidence.

### Phase CX-7 — Realistic framework and RAG integrations

Upgrade the current examples selectively, beginning with one graph framework and one retrieval workflow. Add optional, pinned dependency environments, framework-native interrupt/resume, streaming/cancellation, state persistence, and version-specific tests. Keep dependency-free contract tests as the baseline.

**Acceptance criteria:** each supported version has a reproducible environment; framework state cannot bypass the control plane; provider/tool failures, prompt injection, stale evidence, cancellation, and altered handoffs are covered; unsupported versions are explicitly labeled.

### Phase CX-8 — Operational assurance and release gate

Build domain × workflow × action × evidence × failure matrices; run concurrency, chaos, replay, redaction, secret scan, dependency, SBOM, and clean-checkout validation. Add tenant/workflow/tool kill-switch drills, monitoring and alerting evidence, and a release decision distinguishing synthetic, local, pilot, and production evidence.

**Acceptance criteria:** every known limitation is recorded; all opt-in features are disabled by default; no unsupported production or regulatory claims are made; deployment-dependent controls are marked open until evidenced.

## Recommended first vertical slice

The highest-leverage first slice is **CX-0 through CX-3 for one RAG-backed, multi-step workflow** rather than implementing all features across every framework. A representative synthetic workflow is:

```text
retrieve -> cite/validate evidence -> propose tool action -> guard -> pause if required -> approve -> resume -> execute stub
```

Use a synthetic customer-support or ecommerce workflow because it exercises retrieval freshness, tenant scope, sensitive-data redaction, human review, idempotency, and a reversible mutation without requiring clinical, employment, trading, or financial production claims. The same contracts can then be reused for the remaining domains.

## Prioritized backlog

| Priority | Item | Why now | Expected artifact |
|---|---|---|---|
| P0 | WorkflowRunContext, ToolIntent, EvidenceEnvelope schemas | Establishes the stable language for every later feature. | Versioned Pydantic models and ADR |
| P0 | Handoff v2 binding and canonicalization | Prevents replay and cross-step authority confusion. | Signer/verifier implementation and adversarial tests |
| P0 | RAG evidence boundary | Directly addresses prompt injection, stale retrieval, leakage, and cross-tenant risk. | Retrieval/evidence adapter and redaction tests |
| P1 | Durable budgets and workflow state machine | Makes long-running agent behavior bounded and resumable. | State transitions, counters, concurrency tests |
| P1 | Scoped checkpoints and approval re-evaluation | Makes human oversight meaningful after refresh or changed evidence. | Approval scope model and recovery tests |
| P1 | Policy composition and delegation attenuation | Controls multi-agent and multi-domain complexity. | Effective-policy record and child-context tests |
| P1 | Inbox/outbox and execution semantics | Prevents duplicate or orphaned side effects. | Transactional intent store and crash/retry tests |
| P2 | One real pinned framework integration | Validates the adapter contract against actual framework behavior. | Optional environment and compatibility tests |
| P2 | Operational control plane | Required before realistic enterprise pilot claims. | Kill-switch, metrics, alerts, and drill evidence |

## Explicit non-goals

The plan does not propose autonomous clinical decisions, hiring decisions, live trading, payment capture, account recovery, unrestricted browsing, a universal policy expression language, automatic trust in retrieved text, or a guarantee of exactly-once execution across arbitrary external systems. It also does not make framework-shaped examples equivalent to production-certified integrations.

## Release posture

The current HonestAgent release remains suitable for guarded single-action evaluation, domain-pack experiments, and credential-free adapter demonstrations. It is not yet a complete control plane for arbitrary long-running agentic workflows or complex RAG deployments. The next release should be called a **workflow-safety foundation** only after CX-0 through CX-3 pass their adversarial acceptance criteria; production or conditional-pilot expansion should wait for CX-6 through CX-8 deployment evidence.

## References

[1]: https://github.com/akure/HonestAgent/blob/main/docs/architecture/domain-policy-pack-schema-ea1_20260830.md "HonestAgent Domain Policy Pack Schema"

[2]: https://github.com/akure/HonestAgent/blob/main/docs/development/enterprise-adaptability-and-framework-examples-sprint-plan_20260830.md "HonestAgent Enterprise Adaptability and Framework Examples Sprint Plan"
