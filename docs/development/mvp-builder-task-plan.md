# Honest Agent — MVP Builder Task Plan

## Purpose

This document converts the MVP Launch and Product-Market-Fit Roadmap into executable builder tasks. The sequence is intentionally risk-first: close the real execution boundary before adding dashboards, more integrations, or commercial polish.

The launch target is **one controlled consequential workflow for one customer**, supported by a trustworthy policy decision, authenticated human checkpoint, durable audit evidence, and a real integration path. The MVP is not a general observability platform or a multi-tenant control plane.

## Milestones

| Milestone | Outcome | Exit evidence |
|---|---|---|
| M0 — Contract freeze | Public schemas, policy semantics, and threat model are agreed. | ADR, data model, security invariants, contract tests. |
| M1 — Safe execution boundary | No supported consequential action can bypass policy or approval. | Integration tests with a simulated executor, fail-closed fault tests, approval replay tests. |
| M2 — Pilot-ready core | One workflow can run with durable review and audit evidence. | Docker deployment, authenticated reviewer flow, exportable trajectory, operator runbook. |
| M3 — Integration-ready | Customer can adopt through one production-grade path. | True HTTP passthrough or SDK integration, upstream failure tests, deployment example. |
| M4 — Design-partner pilot | Two pilot workflows produce comparable before/after evidence. | Control-readiness reports, review-burden metrics, customer feedback, pricing signal. |
| M5 — PMF iteration | Repeated usage identifies the next product investment. | Retention and expansion evidence, prioritized PMF backlog, revised roadmap. |

## Workstream A — Contract and policy foundation

### HA-001: Freeze the normalized action contract

**Priority:** P0. **Depends on:** none. **Owner:** core platform builder.

Define versioned request, decision, policy, checkpoint, verifier, and trajectory schemas. Add `policy_version`, `request_id`, `action_class`, `execution_status`, and `trace_event_id` fields without leaking framework-specific concepts into the core contract.

**Acceptance criteria:** Pydantic validation rejects malformed requests; schema examples cover read-only, reversible, irreversible, unknown, paused, approved, rejected, expired, and verifier-failure states; backward-compatibility rules are documented; contract tests run in CI.

### HA-002: Implement the explicit action-policy registry

**Priority:** P0. **Depends on:** HA-001. **Owner:** policy builder.

Replace implicit keyword assumptions with application-declared policy classes: `read_only`, `reversible`, `irreversible`, and `unknown`. Support exact tool identifiers, default behavior for unknown tools, policy versioning, and deterministic conflict resolution.

**Acceptance criteria:** an unknown external action cannot silently proceed; explicit policy overrides are auditable; policy simulation produces the would-proceed, would-pause, and would-reject result without executing a tool; 20 policy edge cases are covered.

### HA-003: Write the safety invariants and threat model

**Priority:** P0. **Depends on:** HA-001, HA-002. **Owner:** security-minded reviewer.

Document invariants such as “verifier failure never returns `PROCEED`,” “human approval is attributable,” “approval is bound to the original request,” and “the core never executes a customer side effect.” Enumerate threats including replay, confused deputy, prompt injection, policy bypass, stale approval, secret leakage, and audit tampering.

**Acceptance criteria:** each invariant has a test or enforcement location; security review signs off before pilot deployment; unresolved threats are recorded with mitigations or explicit exclusions.

## Workstream B — Durable checkpoint and audit system

### HA-004: Add durable checkpoint storage

**Priority:** P0. **Depends on:** HA-001, HA-003. **Owner:** backend builder.

Introduce a storage interface with a development file implementation and a production relational implementation. Store the original request, decision, policy version, reviewer events, expiry, and final disposition. Use optimistic concurrency or transactional compare-and-set for resolution.

**Acceptance criteria:** state survives process restart; duplicate approvals are idempotent; conflicting approvals resolve deterministically; expired checkpoints cannot proceed; all state transitions are testable without external services.

### HA-005: Split and secure the webhook adapter

**Priority:** P0. **Depends on:** HA-004. **Owner:** API builder.

Create `interfaces/webhooks.py` for review queue operations: list, inspect, approve, reject, expire, and audit history. Add caller authentication, reviewer identity, authorization checks, request IDs, and rate limiting hooks.

**Acceptance criteria:** unauthenticated or unauthorized resolution fails; reviewer identity is persisted; approval cannot be reused for a different payload; endpoint contract tests cover 401, 403, 404, 409, and successful transitions.

### HA-006: Implement append-only audit events and export

**Priority:** P0. **Depends on:** HA-004, HA-005. **Owner:** audit builder.

Write immutable events for proposal, policy decision, verifier result, pause, reviewer action, expiry, and execution handoff. Add a sanitized JSON export for customer security reviews.

**Acceptance criteria:** final export reconstructs the complete lifecycle; updates do not erase prior events; sensitive fields can be redacted by policy; export fixtures validate against the public trajectory schema.

## Workstream C — Verification and execution boundary

### HA-007: Define the verifier provider interface

**Priority:** P0. **Depends on:** HA-001, HA-003. **Owner:** verifier builder.

Formalize an asynchronous provider protocol with timeout, cancellation, structured response validation, provider metadata, and failure classification. Keep the deterministic verifier as the default offline provider.

**Acceptance criteria:** timeout, malformed JSON, provider disagreement, cancellation, and rate-limit cases all fail closed; no provider exception reaches the executor as an implicit proceed; contract tests run against a fake provider.

### HA-008: Add one supported live provider adapter

**Priority:** P1. **Depends on:** HA-007. **Owner:** integrations builder.

Implement one production-quality adapter first, selected after customer requirements and provider terms are reviewed. Add credential injection through environment or secret manager only; never store credentials in trajectories.

**Acceptance criteria:** adapter supports bounded timeouts, retries only where safe, structured output validation, cost/latency metadata, and a provider health check; live integration is optional in CI and never required for deterministic tests.

### HA-009: Build a true guarded executor handoff

**Priority:** P0. **Depends on:** HA-002, HA-004, HA-005, HA-007. **Owner:** execution-boundary builder.

Separate evaluation from execution with a signed or request-bound handoff token. The executor accepts a request only when the policy, checkpoint, and payload hash match the approved decision.

**Acceptance criteria:** changing tool arguments after approval invalidates the handoff; rejected, expired, or unknown tokens cannot execute; the demo executor is simulated; integration tests prove zero bypass paths.

### HA-010: Implement real OpenAI-compatible passthrough

**Priority:** P1. **Depends on:** HA-009. **Owner:** proxy builder.

Forward requests to an upstream provider only after the guard decision. Support upstream errors, timeouts, streaming behavior, request IDs, and a clear paused response. Keep the simulated mode for local reproduction.

**Acceptance criteria:** safe request reaches a fake upstream exactly once; paused request reaches it zero times; upstream failure is reported without changing the guard decision; streaming and non-streaming contract tests pass.

## Workstream D — Integration and developer experience

### HA-011: Production Python SDK

**Priority:** P1. **Depends on:** HA-009. **Owner:** SDK builder.

Expose a stable `guard()` decorator and explicit `evaluate()` API with dependency injection for policy, storage, verifier, and logger. Preserve function signatures and make paused decisions easy to catch.

**Acceptance criteria:** sync and async functions are supported; blocked functions are never called; caller can inspect the decision and trajectory ID; SDK contract is documented with a production example.

### HA-012: Official MCP integration

**Priority:** P2. **Depends on:** HA-005, HA-011. **Owner:** MCP builder.

Replace the lightweight line-delimited adapter with official MCP transport and tool discovery. Expose context verification and checkpoint resolution through standard schemas.

**Acceptance criteria:** an official MCP client can discover both tools, invoke them, receive normalized errors, and preserve the same audit lifecycle as HTTP and SDK calls.

### HA-013: Framework adoption examples

**Priority:** P2. **Depends on:** HA-011. **Owner:** developer-experience builder.

Add minimal examples for one agent framework and one IDE workflow. Examples must show proposal, guard call, pause, approval, and executor handoff without hiding the safety boundary in helper code.

**Acceptance criteria:** each example runs from a clean checkout with synthetic data; setup takes under one hour for an experienced Python developer; examples contain no credentials or real side effects.

## Workstream E — Evaluation and pilot readiness

### HA-014: Expand the evaluation harness

**Priority:** P0. **Depends on:** HA-001, HA-002, HA-007. **Owner:** evaluation builder.

Extend the current 40-case suite with provider failures, policy conflicts, unknown tools, replay mutations, malformed requests, concurrency, Unicode/code contexts, and paraphrased actions. Keep a transparent pass-through baseline and identical cases for both systems.

**Acceptance criteria:** at least 75 fixed cases; confusion matrix reports false negatives, false positives, safe pass rate, review rate, and p50/p95/p99 latency; every failure is retained as a regression fixture.

### HA-015: Separate latency budgets

**Priority:** P1. **Depends on:** HA-014. **Owner:** performance builder.

Measure policy, verifier, storage, queue, and end-to-end latency separately. Report local deterministic, fake-provider, and live-provider results independently.

**Acceptance criteria:** fast-path budget is defined before measurement; p95 target is reported with environment and provider details; persistence latency is not hidden inside verifier latency.

### HA-016: Build the customer control-readiness report

**Priority:** P1. **Depends on:** HA-014, HA-015. **Owner:** pilot tooling builder.

Generate a report containing action taxonomy, baseline behavior, guarded behavior, unsafe interception, safe-action block rate, review burden, latency, unresolved cases, known limitations, and recommended rollout controls.

**Acceptance criteria:** report is generated from machine-readable results; all percentages link to raw artifacts; customer data can be sanitized; a non-builder can understand the recommendation.

## Workstream F — Pilot operations and commercial learning

### HA-017: Create the two-week pilot playbook

**Priority:** P0. **Depends on:** HA-003, HA-016. **Owner:** founder or solutions lead.

Define discovery, workflow selection, data sanitization, policy workshop, staging integration, review training, benchmark, go-live recommendation, and handoff steps.

**Acceptance criteria:** playbook names customer responsibilities, required access, deliverables, timeline, pricing, and stop conditions; no pilot depends on production credentials before security review.

### HA-018: Add policy simulation and dry-run mode

**Priority:** P1. **Depends on:** HA-002, HA-014. **Owner:** product builder.

Allow customers to observe what would have paused or required approval without changing execution. This is essential for tuning policy before enforcement.

**Acceptance criteria:** dry-run never performs a side effect; output includes reason and policy version; customer can compare review burden before and after policy changes.

### HA-019: Instrument PMF metrics

**Priority:** P1. **Depends on:** HA-006, HA-016. **Owner:** product analytics builder.

Track protected consequential actions, critical releases, safe-action block rate, review turnaround, time to first protected action, unresolved checkpoints, pilot conversion, and 90-day workflow retention.

**Acceptance criteria:** metrics are defined in a data dictionary; sensitive payloads are excluded or redacted; dashboards are deferred until event semantics are stable; weekly pilot review is possible from exports.

### HA-020: Run design-partner pilots and pricing tests

**Priority:** P0 after M2. **Depends on:** HA-017, HA-018, HA-019. **Owner:** founder or sales lead.

Recruit 5 qualified prospects, conduct 12 problem interviews, run at least 2 pilots, and test a fixed-fee control-readiness offer before investing in broad SaaS infrastructure.

**Acceptance criteria:** interview notes identify repeated pain or invalidate the wedge; at least 3 of the first 5 qualified prospects accept a paid pilot or provide a documented procurement path; pilot results inform the next backlog revision.

## Delivery sequence

| Sequence | Tasks | Timebox | Release decision |
|---|---|---:|---|
| Sprint 1 | HA-001, HA-002, HA-003, HA-014 design update | 1 week | Do not build production integrations until contracts and invariants are frozen. |
| Sprint 2 | HA-004, HA-005, HA-006 | 1–2 weeks | M1 only if durable and authenticated checkpoint tests pass. |
| Sprint 3 | HA-007, HA-009, HA-011 | 1–2 weeks | M1/M2 only if no bypass path is found under fault injection. |
| Sprint 4 | HA-008, HA-010, HA-015 | 1–2 weeks | M3 only if true passthrough and provider-failure behavior are verified. |
| Sprint 5 | HA-012, HA-013, HA-016, HA-017 | 1–2 weeks | Pilot readiness review. |
| Sprint 6 | HA-018, HA-019, HA-020 | 2–4 weeks | PMF decision based on paid demand, retention, and review burden. |

## Definition of ready for each builder task

A task is ready when its contract, owner, dependency, test cases, data-safety boundary, and acceptance criteria are explicit. A task is not ready merely because it has a plausible implementation idea. If a task changes consequential-action authorization, it also requires a threat-model update and an adversarial regression fixture.

## Definition of done for MVP launch

The MVP is ready for a controlled paid pilot when one customer workflow can use a supported integration to propose and execute safe actions, pause risky actions, authenticate a reviewer, persist every state transition, survive restart, export sanitized evidence, and reproduce a baseline-versus-guard comparison. The system must fail closed on verifier and storage failure, and the customer must understand the remaining limitations.

## Definition of done for PMF investment

Invest in broader PMF features only after customer evidence shows repeated use and willingness to pay. The minimum signal is two active design-partner workflows, three paid or procurement-qualified pilots among the first five qualified opportunities, continued guard usage after 30 days, and a customer request for expansion such as another workflow, policy administration, or evidence retention.
