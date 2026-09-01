# Sprint Trace — STD-0 Protocol Governance and Public Contract Boundary

| Field | Value |
|---|---|
| Sprint | STD-0 |
| Objective | Establish a versioned, framework-neutral public control protocol and governance boundary. |
| Date | 2026-09-01 |
| Status | Complete |
| Evidence class | Local source, contract tests, and design review |
| Commit | `10afb04` |

## Baseline

The remote branch already contains CX-0 through CX-3: workflow context and budgets, workflow-bound handoff v2, and the first-class in-memory RAG evidence boundary. STD-0 formalizes those contracts for independent implementation rather than adding a parallel authorization system.

## Delivered

| Deliverable | Artifact |
|---|---|
| Normative protocol contract | `docs/architecture/honestagent-control-protocol-v1-std0_20260901.md` |
| Trust-boundary threat model | `docs/security/protocol-governance-threat-model-std0_20260901.md` |
| Architecture decision record | `docs/architecture/adr-std0-protocol-kernel-conformance-boundary_20260901.md` |
| Executable version/extension rules | `honest_agent/protocol.py` |
| Public exports | `honest_agent/__init__.py` |
| Governance tests | `tests/test_std0_protocol_governance.py` |

## Decisions

The protocol is versioned as `honestagent.control.v1` with major/minor compatibility. Unknown major versions, ambiguous or malformed envelopes, and unknown security-relevant extensions fail closed. Namespaced extensions are allowed only with an explicit classification. The protocol, reference kernel, conformance kit, and enterprise services are separate layers. Model output and retrieved content cannot grant authority.

## Acceptance evidence

| Criterion | Result |
|---|---|
| Independent implementer can understand minimum exchange | PASS — normative protocol document defines envelopes, statuses, state transitions, and handoff binding |
| Unknown major versions fail closed | PASS — `require_known_major` and negative tests |
| Version negotiation does not silently cross major versions | PASS — `negotiate_version` and negative tests |
| Unknown extension classifications fail closed | PASS — `validate_extension` and negative tests |
| Protocol/kernel/conformance/commercial separation | PASS — ADR and protocol product-separation section |
| Model/retrieved content cannot become authority | PASS — threat model and protocol trust rules |

## Limitations

STD-0 does not yet provide the STD-1 golden-fixture runner, independent implementation, public conformance badge, actual framework-version compatibility, or production deployment evidence. The protocol helpers are additive and do not replace the existing handoff, RAG, policy, or executor tests.

## Next sprint

Proceed to **STD-1 — Golden fixtures and conformance kit**. That sprint should turn the normative rules into language-neutral fixtures and a reproducible result format.
