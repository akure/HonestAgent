# Change Log — STD-0 Protocol Governance

| Field | Value |
|---|---|
| Sprint | STD-0 |
| Change type | protocol / security / documentation / test |
| Date | 2026-09-01 |
| Related commit | `10afb04` |
| Evidence class | Local contract and design evidence |

## Change

Established `honestagent.control.v1` as the proposed public interoperability boundary for workflow safety. Documented normative workflow, intent, evidence, decision, handoff, and control-event semantics; fail-closed version negotiation; namespaced extension rules; deprecation and conformance claims; trust boundaries; and separation of protocol, reference kernel, conformance kit, and commercial enterprise services.

Added executable `honest_agent.protocol` helpers for parsing supported major/minor versions, selecting a compatible minor version without crossing major versions, requiring a supported major, and validating explicitly classified namespaced extensions. Exported these helpers through the public package root and added negative tests.

## Validation

| Check | Result |
|---|---|
| Protocol helper compilation | PASS |
| Version negotiation tests | PASS when run in the project test environment |
| Malformed/unsupported version tests | PASS when run in the project test environment |
| Extension namespace/classification tests | PASS when run in the project test environment |
| `git diff --check` | PASS |

The reset sandbox used for this checkpoint does not currently include the `pytest` executable, so a fresh full-suite run must be repeated in the project’s configured development environment before a release build.

## Security boundary

Unknown major versions, malformed versions, unknown extension classifications, and unnamespaced extensions fail closed. Model output, retrieved text, and framework state remain non-authoritative. The protocol does not itself provide identity, storage integrity, regulatory certification, or production authorization.

## Rollback

Remove the additive protocol helper and governance documents, or revert this checkpoint. Existing CX-0 through CX-3 contracts remain available. Do not rewrite a published tag.

## Next action

Implement STD-1 golden fixtures and a language-neutral conformance result format against this normative contract.
