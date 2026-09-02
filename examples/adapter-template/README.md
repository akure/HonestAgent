# HonestAgent Adapter Template

Use this template when integrating a framework or language runtime. The adapter must convert the framework's proposed tool call into an HonestAgent request, call the guard boundary, and invoke the underlying tool only after a valid request-bound handoff.

```text
framework proposal
  → EvaluationRequest
  → /v1/guard or GuardedFrameworkTool
  → PROCEED + valid handoff
  → caller-owned tool
```

Never let model messages, retrieved text, framework state, or an adapter-local `approved` flag authorize execution. Preserve `PAUSED`, `REJECTED`, provider failure, cancellation, stale evidence, prompt injection, and altered-handoff outcomes. Add the integration's exact version pin and conformance result before describing it as supported.
