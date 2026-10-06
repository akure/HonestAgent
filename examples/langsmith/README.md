# LangSmith observability boundary

This mini use case shows how to use LangSmith-style tracing with HonestAgent without allowing tracing, model output, or retrieved content to authorize execution.

## Scenario

A support agent proposes two actions:

1. `lookup_customer`: read-only and permitted by the local synthetic policy.
2. `issue_refund`: irreversible and paused because reviewer approval is absent.

Both decisions are recorded in a local JSONL trace. The trace contains decision metadata and a trajectory identifier, not secrets, raw prompts, or unrestricted retrieved content.

## Run locally

From the repository root:

```bash
python examples/langsmith/demo.py
```

No LangSmith account, API key, network access, or framework installation is required for this deterministic demonstration.

## Production integration

In a real LangSmith deployment, use a LangSmith callback, `RunTree`, or `@traceable` wrapper around the framework node. Keep the order unchanged:

```text
framework/model proposal
  -> EvaluationRequest
  -> HonestAgent / HonestGuard
  -> request-bound handoff validation
  -> caller-owned tool
  -> redacted LangSmith trace
```

The LangSmith run is observability only. It must not set tenant, reviewer, policy, approval, or execution fields. Populate trace metadata from the authenticated request and the returned HonestAgent decision. Redact credentials, protected payloads, and unnecessary retrieved documents before sending telemetry.

## Evidence boundary

The local result proves only that the sample records allow and pause decisions. It does not prove LangSmith connectivity, hosted retention, enterprise access controls, or production observability readiness.
