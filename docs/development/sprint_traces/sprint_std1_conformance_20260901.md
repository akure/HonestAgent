# Sprint Trace — STD-1 Golden Fixtures and Conformance Kit

| Field | Value |
|---|---|
| Sprint | STD-1 |
| Objective | Turn the STD-0 protocol rules into versioned, deterministic, language-neutral conformance fixtures and a machine-readable runner. |
| Date | 2026-09-01 |
| Status | Complete |
| Evidence class | Local deterministic conformance evidence |

## Delivered

| Deliverable | Artifact |
|---|---|
| Versioned fixture manifest | `fixtures/conformance/v1/manifest.json` |
| Fixture usage guide | `fixtures/conformance/v1/README.md` |
| Conformance runner | `honest_agent/conformance/runner.py` |
| Runner package boundary | `honest_agent/conformance/__init__.py` |
| Conformance tests | `tests/test_std1_conformance.py` |

## Fixture coverage

The core profile contains eight cases covering compatible minor negotiation, major-version mismatch, malformed versions, valid namespaced extensions, unknown extension classification, unnamespaced extensions, deterministic ToolIntent hashing, and semantic hash mutation.

## Failure discovered and corrected

The first runner execution revealed that the runner eagerly converted an unknown extension classification to raw `ValueError` before the protocol validator could normalize it. The runner was corrected to pass the classification through the protocol boundary, producing the required `ProtocolError` fail-closed result. The conformance package was also changed to lazy-load the runner so `python -m honest_agent.conformance.runner` executes without an import-order warning.

## Validation

| Check | Result |
|---|---|
| Golden manifest runner | PASS — `8 passed`, `0 failed`, `conformant=true` |
| Determinism test | PASS |
| Fixture mismatch reporting | PASS — mismatch is reported as non-conformant |
| Targeted STD-0/STD-1 tests | PASS — 6 tests |
| Full regression suite | PASS — 129 tests |
| `git diff --check` | PASS |

## Limitations

STD-1 is a local reference conformance kit. It does not constitute independent certification, a public conformance badge, or an external implementation result. The initial fixture profile covers core version, extension, and intent-hash behavior; RAG, human-review, execution, and future profiles require additional fixtures.

## Next checkpoint

Proceed to **STD-2 — Python developer experience and CLI**, using this runner and fixture format as the compatibility baseline.
