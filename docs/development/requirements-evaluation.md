# Initial Requirements Evaluation Rubric

This rubric evaluates the current implementation against the initial build requirements. A requirement is marked **Pass**, **Partial**, or **Gap** based on executable evidence rather than code presence alone.

| Requirement | Evidence to collect | Pass condition |
|---|---|---|
| TS-01 token telemetry | Evaluator unit tests plus structured-context fixtures. | Deterministic count is repeatable and ratio threshold triggers escalation. |
| TS-02 hallucination intercept | Ambiguous, unsupported, contradictory, and missing-context fixtures. | Unsafe action is not `PROCEED` before execution. |
| TS-03 HITL workflow | Pending, approval, rejection, replay, and concurrent approval tests. | Action pauses, reviewer resolution is explicit, idempotent, and durable. |
| TS-04 benchmark delta | Same cases through baseline and guard; confusion matrix. | Baseline and solution use identical fixtures and report false positives and false negatives. |
| TS-05 latency overhead | p50/p95 timing with and without local audit persistence. | Fast-path result is measured honestly and compared against the 25 ms target. |
| Proxy integration | FastAPI health, normalized guard, OpenAI-shaped route, approval endpoint. | Contract returns structured decisions and never executes a real side effect. |
| MCP integration | Stdio tool calls and normalized result fields. | Both declared tools are callable and share the core contract. |
| Python decorator | Safe call and paused call fixtures. | Safe function executes; paused function is not invoked. |
| IDE skill | Static review of root `SKILL.md`. | Instructions require structured proposal, guard call, and stop-on-pause behavior. |
| Audit-ready trajectory | JSON schema validation for proceed, pause, reject, approve, and provider failure. | Every evaluation has traceable action, confidence, tier, context ratio, and checkpoint state. |
| Verifier routing | Fast, high-context, and irreversible fixtures. | Risk routes to escalated tier; low-risk actions remain fast. |
| Fail-closed safety | Provider timeout/error injection. | Provider failure cannot return `PROCEED`. |

## Known interpretation boundary

The current implementation uses a deterministic offline verifier. The initial requirements name Groq, Gemini Flash, or Ollama as production-ready provider choices, but do not require live credentials for the reproducible benchmark. Live provider adapter coverage is therefore evaluated separately as a gap or future enhancement, not silently treated as complete.
