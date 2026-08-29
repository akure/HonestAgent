# Honest Agent — Internal Evaluation Report

## Executive conclusion

The prototype is strong on the current deterministic synthetic distribution: **20/20 unsafe cases were intercepted before execution, 20/20 safe cases proceeded, and 16/16 regression tests passed** after the hardening cycle. The key result is not the initial 100% figure by itself; it is that adversarial testing exposed and corrected four safety/quality defects before they could be mistaken for product readiness.

## Final measured results

| Measure | Result | Interpretation |
|---|---:|---|
| Deep evaluation cases | 40 | 20 labeled unsafe and 20 labeled safe |
| Unsafe-action catch rate | 20/20 = 100% | No false negatives in this fixture set |
| Safe-action pass rate | 20/20 = 100% | No false positives in this fixture set |
| Latency p50 / p95 | 0.158 / 0.204 ms | Includes local trajectory persistence; remains below the 25 ms target in this environment |
| Fast / escalated routing | 22 / 18 | Risk is concentrated in the escalated path rather than every request |
| Original benchmark | 10/10 unsafe caught | The approval-resumption case is counted at its first pre-execution checkpoint |
| Regression suite | 16 passed | Covers core, adversarial, concurrency, MCP, SDK, and approval-audit behavior |

These are measured local results from deterministic fixtures, not claims about live provider performance. The verifier fallback is intentionally not a substitute for evaluating real Groq/Gemini/Ollama adapters.

## Defects found and fixed

| Defect | How it was found | Fix | Evidence |
|---|---|---|---|
| Substring matching escalated `runtime_status` and `rewrite_summary`. | Safe misleading-name adversarial test. | Token-aware exact matching. | Adversarial suite improved from 1/5 to 5/5. |
| Zero-argument read-only tools were rejected. | `health_check({})` safe fixture. | Only missing tool names are invalid; empty structured input is allowed. | Safe zero-argument test passes. |
| Provider exception propagated. | Injected timeout provider. | Fail closed with `REJECTED_VERIFIER_FAILURE`. | Provider-failure test passes. |
| Approval replay raised `KeyError`. | Double and concurrent approval tests. | Resolved-state cache with idempotent replay under a lock. | Concurrency test passes. |
| Approval changed memory but not the durable trajectory. | Approval-audit probe. | Store the original request and rewrite the same trajectory after resolution. | Persisted `APPROVED` audit test passes. |
| Risk words in free-form query text escalated safe searches. | Safe query containing “run” and “write”. | Infer implicit risk from tool name only; retain explicit irreversible flag. | Targeted precision probe passes. |

## Remaining risks

The evaluation is still synthetic and the verifier is deterministic. The system has not yet been measured against real provider latency, provider disagreement, malformed provider JSON, cancellation, persistence failure, multi-process state, or a live upstream OpenAI-compatible server. The current token evaluator is a deterministic approximation rather than a model-specific tokenizer. These are the next evaluation boundaries, not evidence that the current result generalizes automatically.

The most important product risk is **semantic under-specification**: a tool named `archive_data` or a generic `call_api` may be consequential even when it does not match the current implicit-risk vocabulary. The safer production direction is an explicit application policy registry with default-deny behavior for unknown external side effects, rather than endlessly expanding keyword lists.

## Recommended next enhancement order

1. Add an explicit policy registry with `read_only`, `reversible`, and `irreversible` action classes, plus tests for unknown tools and policy conflicts.
2. Add provider adapter contract tests for timeout, malformed JSON, disagreement, retries, and cancellation; keep fail-closed semantics mandatory.
3. Separate decision latency from trajectory I/O latency so the 25 ms target is reported honestly for both hot-path verification and audit persistence.
4. Add durable checkpoint storage with expiry, reviewer identity validation, and audit event append-only semantics before any multi-process deployment.
5. Expand evaluation to mutation-based and paraphrased fixtures, then repeat the confusion-matrix analysis with the same cases for baseline and solution.

## Current recommendation

**Continue testing before release.** The deterministic core is ready for a second internal iteration, but the build should not yet be presented as production-grade or provider-validated. The highest-leverage next step is explicit policy semantics plus provider-failure contract testing, not more superficial feature integrations.
