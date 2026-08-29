# Change Log — production provider fault and latency testing

| Field | Value |
|---|---|
| Change ID | `LR-5` |
| Feature | `Production provider fault and latency testing` |
| Timestamp UTC | `2026-08-29 06:58:33` |
| Status | `complete for the provider boundary and offline fault harness` |

## Problem

The provider adapter had one generic exception path and no explicit operational distinction between timeout, transport failure, malformed output, disagreement, retry exhaustion, and cancellation. It also had no bounded latency/outcome instrumentation, making it difficult to prove fail-closed behavior or establish provider budgets.

## Change

Added explicit provider fault types for timeout, unavailability, contract violations, and verifier disagreement. The OpenAI-compatible adapter now maps transport and JSON failures into those types. Added `ResilientVerifierProvider` with bounded retries only for transient timeout/unavailability, no retries for malformed contracts or disagreement, and explicit cancellation propagation. Optional secondary-provider comparison fails closed when recommendation, risk, or confidence materially disagrees. Added `ObservedVerifierProvider` and `ProviderMetrics` to measure attempts, successes, failures, and latency percentiles without recording payloads or secrets.

## Live experiment log

| Stage | What was tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Generic provider exception handling | Existing adapter tests passed, but fault causes were not distinguishable and retry behavior was unspecified | Replaced; generic errors obscure operational control |
| Iteration 1 | Retry transient timeout/unavailability once | Timeout retry and retry-budget tests passed | Kept; retry is bounded and not applied to contract failures |
| Iteration 2 | Compare optional secondary provider | Disagreement test fails closed | Kept; independent disagreement is safer than silently choosing one result |
| Iteration 3 | Add latency/outcome observation | Metrics test records attempts, success/failure, and latency sample | Kept; no request payloads or secrets are recorded |

## Safety invariants

| Invariant | Result |
|---|---|
| Provider timeout exhaustion fails closed through existing guardrail handling | `PASS` |
| Malformed provider output is never treated as a valid recommendation | `PASS` |
| Provider disagreement fails closed | `PASS` |
| Cancellation is propagated and never converted into a successful decision | `PASS` |
| Retry count is bounded and limited to transient failures | `PASS` |
| Metrics do not contain provider payloads or credentials | `PASS` |

## Validation

- `pytest -q`: **55 passed**
- Timeout retry and exhaustion: **PASS**
- Malformed response mapping: **PASS**
- Provider disagreement: **PASS**
- Cancellation propagation: **PASS**
- Latency/outcome instrumentation: **PASS**
- `git diff --check`: **PASS**

## Known limitations

The fault matrix uses deterministic offline transports and provider doubles; no live customer provider endpoint was called, and no production latency SLO is claimed from these tests. A deployment should run the same harness against its approved provider in a controlled environment and record real p50/p95/p99 budgets before unrestricted production authorization.
