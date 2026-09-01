# ADR STD-0: Separate Protocol, Kernel, Conformance Kit, and Enterprise Services

## Status

Accepted for the STD-0 checkpoint.

## Context

HonestAgent must become useful across many agent frameworks and RAG architectures without forcing every user to adopt one implementation or vendor service. At the same time, the project needs to retain a defensible generic safety kernel and a commercial path for managed enterprise operations.

## Decision

Maintain four separable layers:

1. **Control protocol:** versioned schemas, canonicalization, status semantics, state transitions, trust rules, and compatibility governance.
2. **Reference kernel:** the generic fail-closed evaluator, policy, checkpoint, handoff, and executor boundary.
3. **Conformance kit:** language-neutral fixtures and tests that measure compatibility.
4. **Enterprise services:** managed identity, registry, durable storage, audit, quotas, monitoring, support, and deployment operations.

Framework integrations MUST translate into the control protocol and MUST NOT implement an alternate authorization path. Domain behavior MUST remain in declarative policy packs or explicitly reviewed deterministic validators rather than industry-specific branches inside the kernel.

## Alternatives rejected

| Alternative | Reason rejected |
|---|---|
| Make HonestAgent a full agent framework | Increases coupling and makes adoption dependent on replacing existing stacks. |
| Keep all semantics proprietary and undocumented | Prevents independent implementation and undermines interoperability claims. |
| Put domain logic directly in the kernel | Expands the trusted computing base and makes policy behavior harder to review. |
| Let framework adapters authorize independently | Creates bypass paths and inconsistent pause/reject/handoff semantics. |
| Treat RAG content as authorization | Confuses evidence with authority and creates injection and cross-tenant risks. |

## Consequences

The protocol must be stable, explicit, and independently readable. The reference implementation must pass its own conformance fixtures but cannot claim external conformance without an independent test run. Commercial offerings can add operational value without fragmenting the interoperability contract. The repository must clearly distinguish protocol rights from proprietary code, domain packs, hosted services, and commercial deployment rights.

## Reversal conditions

This decision may be revisited only through a new ADR if independent adoption demonstrates that a boundary is too restrictive, or if security evidence shows that a protocol layer creates an unmanageable bypass risk. Any revision must preserve fail-closed behavior and publish a migration path.
