# Change Log — STD-1 Golden Fixtures and Conformance Kit

| Field | Value |
|---|---|
| Sprint | STD-1 |
| Change type | protocol / conformance / test |
| Date | 2026-09-01 |
| Related commit | `23879ec` |
| Evidence class | Local deterministic conformance evidence |

## Change

Added the first language-neutral `honestagent.control.v1` core-profile manifest under `fixtures/conformance/v1/`. The eight synthetic cases cover minor-version negotiation, unsupported major versions, malformed versions, namespaced extension classification, unsafe extension handling, deterministic intent hashing, and semantic mutation detection.

Added `honest_agent.conformance.runner`, which emits machine-readable per-case results and an overall `conformant` flag with a non-zero exit code on mismatch. Added a fixture README describing independent implementation requirements and the boundary between local runner evidence and independent certification.

## Defect correction

The initial runner converted an unknown extension classification before it reached the protocol helper, producing a raw `ValueError` instead of the normative `ProtocolError`. The boundary was corrected and regression-tested. Package lazy loading removed the module-entry warning.

## Validation

| Check | Result |
|---|---|
| Golden manifest | PASS — 8/8 conformant |
| Targeted STD-0/STD-1 tests | PASS — 6 tests |
| Full regression suite | PASS — 129 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security and limitations

Fixtures are synthetic and credential-free. A mismatch remains a conformance failure and cannot be treated as authorization. STD-1 does not provide external certification, a conformance badge, or complete RAG/human-review/execution profile coverage. Those profiles require later fixture additions and independent reproduction.

## Rollback

Remove the additive conformance package and fixture directory, or revert this checkpoint. The STD-0 protocol helpers and existing CX tests remain independently available.

## Next action

Implement STD-2 developer experience and CLI features using the STD-1 fixture runner as the compatibility baseline.
