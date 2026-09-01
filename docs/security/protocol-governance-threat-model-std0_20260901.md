# STD-0 Protocol Governance Threat Model

## Decision summary

The protocol boundary is a **policy and execution safety contract**, not an identity provider, retrieval engine, model evaluator, or external transaction coordinator. The reference kernel remains generic. Frameworks and enterprise services must translate into the protocol and cannot create parallel authorization paths.

## Trust boundaries

| Boundary | Untrusted input | Required control |
|---|---|---|
| Model/framework → protocol | Generated tool name, arguments, thoughts, retrieved text, framework state | Typed validation, provenance, policy evaluation, and no authorization from content |
| Retrieval system → evidence | Chunks, metadata, source claims, timestamps, summaries | Tenant/source scope, freshness, lineage, classification, egress, citation, and injection signal |
| Caller → identity context | Tenant, agent, reviewer, delegation claims | Trusted identity integration; caller metadata alone is not proof of authorization |
| Policy registry → kernel | Pack bytes, version, status, signature, activation request | Signature verification, registry-derived lifecycle, immutable policy snapshot, fail-closed conflict handling |
| Kernel → executor | Decision and handoff | Request/state-bound signature, expiry, idempotency, and executor revalidation |
| Store → resume | Pending state and approval records | Integrity, scoped approval, re-evaluation, duplicate-resume protection, and expiry |
| Kernel → audit | Prompts, tool payloads, evidence, outcomes | Redaction, hashes/references, actor/run/step correlation, and append-only integrity |

## Principal threats and mitigations

| Threat | Mitigation in STD-0 | Residual risk |
|---|---|---|
| Prompt injection | Content is explicitly non-authoritative; suspicious content pauses or rejects according to profile | Detectors can have false positives/negatives; source and application isolation remain necessary |
| Cross-tenant retrieval | Evidence carries tenant scope and retrieval boundary must check it | Production vector-store isolation and access controls need deployment evidence |
| Stale or contradictory evidence | Freshness, provenance, contradiction, and citation semantics are normative | Clock, source quality, and business freshness policy are deployment concerns |
| Handoff replay | Handoff binds run, step, attempt, tenant, policy, evidence, intent, destination, and expiry | Distributed single-use consumption still requires durable execution storage |
| Delegation escalation | Child contexts attenuate capabilities and cannot broaden parent authority | Identity and worker enforcement must preserve the context fields |
| Fail-open extension | Unknown security-relevant extensions and unsupported major versions reject | Implementations must not incorrectly classify extensions as informational |
| Malformed or ambiguous envelope | Required fields, enum values, canonicalization, and duplicate/unknown-field rules fail closed | Parser differentials between languages require conformance vectors |
| Audit leakage | Raw protected content is not part of the decision record; references and hashes are used | Operators can still leak data through application-level logs outside the protocol |
| False production claim | Evidence class and conformance-claim requirements are explicit | Organizations may still market beyond measured evidence; governance must review claims |

## Security invariants

1. A model, retrieved document, tool result, or framework state cannot grant authority.
2. A `PAUSED`, `REJECTED`, `CAP_EXCEEDED`, or provider-failure result cannot reach execution.
3. A handoff for one intent cannot authorize another intent, step, attempt, tenant, destination, policy, or evidence snapshot.
4. A child workflow cannot increase parent capability, budget, deadline, or tenant scope.
5. Unknown security-relevant protocol behavior fails closed.
6. Audit and simulation paths do not export raw prompts, protected content, secrets, or credentials.

## Decision record

STD-0 adopts a versioned protocol and profile model, namespaced extensions, explicit compatibility negotiation, immutable policy snapshots, and separate protocol/reference-kernel/conformance/enterprise layers. It rejects an unrestricted expression language, implicit trust in retrieved content, silent downgrade between protocol versions, and a claim that the reference implementation alone proves external conformance.

## Evidence boundary

This is a design and local reference-implementation evidence record. It does not claim independent review, production penetration testing, customer validation, regulatory certification, or complete protection against application-specific vulnerabilities.
