# HonestAgent Control Protocol v1 — STD-0 Governance and Public Contract

## Status

| Field | Value |
|---|---|
| Protocol name | `honestagent.control.v1` |
| Document status | STD-0 implementation checkpoint |
| Compatibility posture | Proposed stable public contract; changes require the process in this document |
| Reference implementation | HonestAgent Python package |
| Evidence class | Local repository implementation and tests |
| Production posture | **Not production authorization** |

This document defines the public interoperability boundary for HonestAgent workflow safety. It is intentionally separate from any framework, model provider, vector store, identity provider, or enterprise hosting product.

## Scope and product separation

HonestAgent has four separable layers:

| Layer | Included in this protocol | Not implied by protocol conformance |
|---|---|---|
| Control protocol | Versioned envelopes, semantics, state transitions, canonicalization, and failure behavior | A particular deployment, framework, model, database, or regulatory certification |
| Reference kernel | Generic evaluation, policy composition, checkpoints, signed handoffs, and executor gating | Universal protection against every application defect |
| Conformance kit | Golden fixtures, negative cases, signature vectors, and result format | Independent certification unless a named test run is published |
| Enterprise services | Identity, managed registry, durable operations, audit, quotas, support, and deployment controls | Open-ended permission to use the repository or enterprise product |

A compatible implementation must preserve the protocol’s safety semantics. It may implement the protocol in another language or runtime, but it must not silently reinterpret a pause, rejection, missing trust signal, expired handoff, or malformed envelope as authorization to execute.

## Normative vocabulary

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative. A protocol implementation is conformant only when it follows the mandatory requirements in this document and passes the versioned conformance fixtures.

## Trust model

The protocol treats the following as untrusted unless separately authenticated and attributable:

- model output, chain-of-thought-like text, and generated tool arguments;
- user-provided content;
- retrieved documents, web pages, vector-search chunks, and tool results;
- model-generated summaries of evidence;
- framework state restored from an untrusted store;
- caller-provided claims about reviewer, tenant, policy, or authorization.

Untrusted content **MUST NOT** establish tenant identity, reviewer identity, policy authority, approval, or permission to execute. A trusted control-plane identity or explicitly trusted evidence producer must supply those claims.

## Normative envelope set

### WorkflowRunContext

A workflow context identifies the authority and limits of a workflow step. It MUST include:

| Field | Rule |
|---|---|
| `contract_version` | Major-compatible protocol version |
| `run_id` | Stable workflow execution identifier |
| `tenant_id` | Trusted tenant scope; never derived from retrieved text |
| `root_agent_id` | Root accountable agent or application identity |
| `parent_step_id` | Parent step for delegated work, when present |
| `step_id` | Stable current step identifier |
| `attempt` | Positive attempt number; retries do not reset it |
| `delegation_chain` | Ordered parent lineage, bounded in length |
| `workflow_version` | Application workflow version |
| `deadline` | Absolute expiration boundary |
| `budgets` | Non-negative verifier/tool/retry/token/fan-out/concurrency/amount limits |
| `kill_switch_epoch` | Monotonic operational stop-control version |
| `policy_snapshot_id` | Immutable effective-policy reference |
| `allowed_tools` | Explicit capability set; empty means no delegated tool capability |

A child context MUST attenuate tools, budgets, and deadline. It MUST NOT add capabilities, extend a deadline, change tenant scope, or increase a parent limit.

### ToolIntent

A tool intent is a normalized proposal, not an authorization. It MUST include a non-empty tool name, argument schema version, canonical JSON arguments, declared action class, resource scope, destination, idempotency key, expected side-effect mode, and provenance.

Canonical arguments MUST be serialized with sorted keys, deterministic separators, UTF-8 encoding, and non-finite numbers rejected. The intent hash MUST be computed over the canonical serialized intent, not over a framework-specific object representation.

`provenance` identifies whether the intent originated from a model, human, deterministic rule, or delegated agent. Provenance is descriptive and MUST NOT bypass policy or handoff validation.

### EvidenceEnvelope

An evidence envelope identifies evidence without exporting raw protected content. It MUST include evidence ID, source ID/type, tenant scope, content hash, observation time, trust class, data classification, and a redacted reference. It MAY include expiry, provenance chain, lineage references, retrieval query ID, and citation spans.

Authorization-bearing evidence MUST be produced by an explicitly trusted and attributable producer. Retrieved text and model summaries MUST NOT become authorization-bearing merely because they contain instructions or claims. Unknown, stale, contradictory, cross-tenant, disallowed-egress, or malformed evidence MUST produce a pause or rejection according to policy; it MUST NOT produce an allow decision.

### DecisionRecord

A decision record MUST be reproducible from the policy snapshot, workflow context, intent hash, and evidence IDs. It MUST include decision ID, run/step/attempt, status, reason codes, policy snapshot, and redacted references. It MUST NOT include raw prompts, raw protected retrieval content, secrets, or credentials.

The minimum status vocabulary is:

| Status | Meaning | Execution consequence |
|---|---|---|
| `PROCEED` | All configured gates passed | Handoff MAY be issued; executor still MUST validate it |
| `PAUSED` | Human review, missing/stale evidence, or recoverable uncertainty | MUST NOT execute; checkpoint or evidence resolution required |
| `REJECTED` | Explicit deny, malformed/unauthorized input, or fail-closed error | MUST NOT execute; no automatic fallback |
| `CAP_EXCEEDED` | A configured workflow, tool, token, retry, or amount limit was reached | MUST NOT execute; operator or workflow policy decides next step |
| `PROVIDER_FAILURE` | Provider/tool dependency failed before a valid result | MUST NOT be reported as successful execution |

### ExecutionHandoffV2

A handoff is a short-lived, signed authorization for one exact intent. It MUST bind run ID, step ID, attempt, tenant ID, policy snapshot ID, evidence snapshot ID, intent hash, destination, and expiry. It MUST be rejected when any bound value changes, when the token expires, when the signature is invalid, or when the decision is not `PROCEED`.

A handoff MUST NOT be treated as a reusable bearer permission for another step, attempt, tenant, destination, policy, evidence snapshot, or argument set.

### ControlEvent

Control events are append-only operational records. Implementations SHOULD emit events for proposal, evaluation, pause, approval, rejection, handoff issue, execution start/result, timeout, cancellation, retry, compensation, recovery, and kill-switch activation. Event payloads MUST be redacted and MUST preserve actor, run, step, and timestamp fields.

## State transitions

The minimum safe state graph is:

```text
PROPOSED → EVALUATING →
  PROCEED → HANDOFF_ISSUED → EXECUTION_STARTED → COMPLETED
  PAUSED → APPROVED → HANDOFF_ISSUED → EXECUTION_STARTED
  PAUSED → REJECTED / EXPIRED / CANCELLED
  REJECTED / CAP_EXCEEDED / PROVIDER_FAILURE → TERMINAL
```

An implementation MAY add states, but it MUST NOT add an edge from `PAUSED`, `REJECTED`, `CAP_EXCEEDED`, or `PROVIDER_FAILURE` directly to execution. Approval MUST be scoped to the original intent, evidence, policy snapshot, run, step, and attempt. Changed state requires re-evaluation.

## Failure and compatibility rules

### Versioning

Protocol versions use `major.minor` semantics. A compatible minor revision MAY add optional fields or reason codes when the default behavior remains safe. A major revision MAY change required fields, canonicalization, status semantics, or security boundaries.

- Unknown major versions MUST be rejected.
- Unknown minor versions MUST be accepted only when the implementation has declared compatibility and can preserve fail-closed behavior.
- Missing required fields, ambiguous duplicate fields, invalid enum values, and unsupported security-relevant extensions MUST be rejected.
- Implementations MUST expose their supported protocol versions.
- A negotiation failure MUST NOT downgrade silently to a weaker security contract.

### Extensions

Extensions use namespaced keys such as `x-example.org-field` or a registered protocol namespace. Extensions MUST be explicitly declared, schema-bounded, and classified as informational, restrictive, or security-relevant. Security-relevant extensions require conformance fixtures before release.

Unknown extensions MAY be ignored only when they are explicitly marked non-authoritative and cannot affect authorization, routing, identity, policy, evidence, limits, or execution. Otherwise they MUST cause rejection.

### Deprecation

A field or status is deprecated only after a documented replacement exists, a migration path is published, and the conformance kit covers both the transition and final removal. Security-critical behavior MUST NOT be deprecated without an equivalent or stronger replacement.

## Conformance claims

A project MAY claim `honestagent.control.v1 compatible` only after passing the versioned conformance suite for the declared profile. A claim MUST name:

- implementation and version;
- protocol version and profile;
- test-suite version and commit;
- date and environment;
- known unsupported features.

The reference implementation itself is not automatically evidence that an independent implementation conforms. The project MUST NOT claim de facto standard status solely from publishing this protocol.

## Protocol profiles

The initial profiles are:

| Profile | Scope | Requirement |
|---|---|---|
| `core` | Workflow context, intent, decision, and handoff | Required baseline |
| `rag` | Evidence envelopes, retrieval boundaries, freshness, lineage, and citation coverage | Required for RAG claims |
| `human-review` | Scoped checkpoints, reviewer identity, approval, expiry, and resume | Required for reviewed consequential actions |
| `execution` | Handoff validation, idempotency, execution events, and failure semantics | Required for executor integration |

An implementation MUST NOT claim a profile it has not tested. Profiles compose additively; a caller cannot use a partial profile to weaken a required control.

## Governance process

Protocol changes follow this sequence:

1. Open a proposal describing the problem, threat model, compatibility impact, and alternative designs.
2. Add or update normative text and machine-readable schema fixtures.
3. Add positive and negative conformance cases, including a fail-closed case.
4. Obtain implementation and security/reliability review.
5. Publish a decision record and migration guidance.
6. Release the protocol revision and reference implementation together when semantics change.

Emergency security corrections MAY be released as patch or minor revisions, but the change MUST document the affected threat, mitigation, compatibility impact, and rollback path.

## Repository and licensing boundary

The protocol document and interoperability semantics are intended to be readable and implementable independently. This does not grant rights to copy proprietary implementation code, domain packs, commercial services, branding, or licensed customer materials. Protocol adoption, source-code use, hosted deployment, resale, and commercial rights remain governed by the repository’s applicable license and commercial agreements.

## STD-0 acceptance record

| Criterion | Result | Evidence |
|---|---|---|
| Independent implementer can understand minimum exchange | PASS for documented contract | This document and CX schemas |
| Unknown major/malformed/ambiguous input fails closed | PASS in reference contract tests | `tests/test_cx0_contracts.py` |
| Model/retrieved text cannot become authority | PASS in contract and RAG boundary tests | `tests/test_cx3_rag_boundary.py` |
| Versioning and extensions are governed | PASS as normative process | Versioning and extensions sections |
| Protocol/kernel/conformance/commercial separation | PASS | Product separation section |

## Next checkpoint

Proceed to **STD-1 — Golden fixtures and conformance kit**. STD-0 does not claim external conformance or production readiness; it establishes the contract that STD-1 will make executable.
