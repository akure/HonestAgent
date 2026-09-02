# Change Log — STD-8 Independent Reproduction and Benchmark Evidence

| Field | Value |
|---|---|
| Sprint | STD-8 |
| Change type | benchmark / reproduction / evidence / test |
| Date | 2026-09-02 |
| Related commit | `e84e49d` |
| Evidence class | Local synthetic reproduction; not independent or production evidence |

## Change

Added `honest_agent.std8_benchmark` with a fixed seven-case vector, identical unguarded baseline and controlled paths, expected outcomes, false-pause and false-proceed metrics, accuracy, latency, and provenance. Added the clean-checkout runner `scripts/run_std8_benchmark.py`, machine-readable JSON output, deterministic benchmark tests, and an independent-review reproduction protocol.

## Validation

| Check | Result |
|---|---|
| STD-8 tests | PASS — 2 tests |
| Full regression suite | PASS — 150 tests |
| Exact runner command | PASS |
| Artifact JSON parse | PASS |
| Repeated controlled outcomes | PASS |
| Baseline false proceeds | 4 of 7 |
| Controlled false proceeds | 0 of 7 |
| Controlled false pauses | 0 of 4 expected proceeds |
| Controlled accuracy | 1.0 |
| Mean controlled latency | 12.60 ms in recorded local run |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security and evidence boundary

The benchmark path uses no credentials, provider, vector database, or live side effects. The checked-in result is local synthetic evidence only. It is not independent third-party reproduction, customer evidence, regulatory evidence, production performance evidence, or a competitor comparison.

## Rollback

Revert the STD-8 module, runner, tests, result artifact, reproduction guide, and evidence documents. Earlier benchmark artifacts remain available.

## Next action

Implement STD-9 ecosystem and protocol adoption artifacts.
