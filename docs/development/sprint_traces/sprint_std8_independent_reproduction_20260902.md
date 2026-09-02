# Sprint Trace — STD-8 Independent Reproduction and Benchmark Evidence

| Field | Value |
|---|---|
| Sprint | STD-8 |
| Objective | Establish repeatable, externally understandable local measurement with an identical baseline comparison and explicit evidence boundaries. |
| Date | 2026-09-02 |
| Status | Complete |
| Evidence class | Local synthetic reproduction; not independent or production evidence |
| Commit | Pending |

## Baseline risk

Existing benchmark scripts reported unsafe-action catch counts but did not expose false pauses, false proceeds, a stable machine-readable schema, or a dedicated clean-checkout command. This made local results harder to reproduce and easier to overstate.

## Delivered

| Deliverable | Artifact |
|---|---|
| Fixed benchmark vector and controlled runner | `honest_agent/std8_benchmark.py` |
| Clean-checkout command | `scripts/run_std8_benchmark.py` |
| Benchmark tests | `tests/test_std8_benchmark.py` |
| Machine-readable result | `docs/development/evidence/std8_independent_reproduction_20260902/benchmark_results.json` |
| Reproduction protocol | `docs/development/evidence/std8_independent_reproduction_20260902/README.md` |

The benchmark runs the same seven cases through an intentionally unguarded baseline and the controlled HonestAgent path. It measures false proceeds, false pauses, accuracy, and mean controlled latency and records Python/platform/network/credential provenance.

## Defect discovered and corrected

No implementation defect was found in the STD-8 benchmark after focused and full validation. The benchmark intentionally reports a baseline that proceeds on every case, exposing four false proceeds against the expected vector rather than using only blocked-action counts.

## Verification

| Check | Result |
|---|---|
| STD-8 benchmark tests | PASS — 2 tests |
| Full regression suite | PASS — 150 tests |
| Clean-checkout reproduction command | PASS |
| JSON schema/artifact parse | PASS |
| Repeatable controlled outcomes | PASS |
| Baseline false proceeds | 4 of 7 |
| Controlled false proceeds | 0 of 7 |
| Controlled false pauses | 0 of 4 expected proceeds |
| Controlled accuracy | 1.0 across 7 cases |
| Mean controlled latency | 12.60 ms in recorded run |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

The benchmark has no provider credentials, no network calls in the benchmark path, and no live tool side effects. Results preserve baseline and controlled rows, expected statuses, and provenance. The report does not infer production or independent-review claims.

## Limitations

This remains local synthetic evidence. The seven cases are not a statistically representative customer workload. Latency is environment-dependent, the baseline is intentionally unguarded rather than a competitor, and no independent third party has yet reproduced or signed the result. Production, provider, distributed, and regulatory evidence remain unmeasured.

## Rollback

Revert the STD-8 benchmark module, runner, tests, result artifact, reproduction guide, and this evidence record. Existing benchmark scripts and prior evidence remain available.

## Next checkpoint

Proceed to **STD-9 — Ecosystem and Protocol Adoption**.
