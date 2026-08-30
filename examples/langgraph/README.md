# LangGraph adapter example

This is a **credential-free local adapter example** for LangGraph. It demonstrates the framework boundary without installing or claiming compatibility with every framework release. The wrapper delegates to `honest_agent.adapters.GuardedFrameworkTool`; it does not duplicate policy logic.

## Flow

`framework proposal -> EvaluationRequest -> HonestGuard -> signed handoff validation -> caller-owned tool`

A `PROCEED` result is executed only after request-bound handoff validation. `PAUSED`, `REJECTED`, `CAP_EXCEEDED`, malformed/failed provider, or invalid handoff results never call the underlying tool. Retrieved text and model messages remain untrusted; only trusted caller metadata supplies tenant and evidence fields.

## Local use

From the repository root, use the shared conformance tests:

```bash
pytest -q tests/test_framework_adapters.py
```

The example has no API keys, network calls, live side effects, or production framework-version claim. For deployment, pin the actual framework version in the application environment and preserve this single pre-execution boundary.

Run the deterministic demo from the repository root:

```bash
python examples/langgraph/demo.py
```
