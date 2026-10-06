# HonestAgent framework mini use cases

These samples show one reusable safety pattern across popular agent frameworks:

```text
framework/model proposal
  -> canonical EvaluationRequest
  -> HonestGuard policy and evidence evaluation
  -> signed request-bound handoff validation
  -> caller-owned tool
  -> redacted audit/observability record
```

The framework remains responsible for planning, routing, state-machine transitions, and user experience. HonestAgent remains responsible for the pre-execution safety boundary. Model messages, retrieved documents, framework state, and tool arguments are untrusted proposals.

## Mini-use-case matrix

| Framework or service | Mini use case | Safe action | Blocked action | Sample |
|---|---|---|---|---|
| LangGraph | Support-ticket state graph | Lookup synthetic customer record | Issue refund without reviewer approval | `examples/langgraph/demo.py` |
| CrewAI | Research crew with a tool boundary | Read synthetic account context | Send an external message without approval | `examples/crewai/demo.py` |
| AutoGen/AG2 | Function-tool assistant | Retrieve synthetic order status | Change account state without an approved handoff | `examples/autogen/demo.py` |
| LangSmith | Observability for the guarded graph | Trace an allow decision | Trace a pause decision without turning it into authority | `examples/langsmith/demo.py` |
| LangChain | Tool wrapper | Read-only lookup | Irreversible tool call without approval | `examples/langchain/demo.py` |
| LlamaIndex | Retrieval workflow | Use cited synthetic evidence | Treat retrieved text as authorization | `examples/llamaindex/demo.py` |

## Run the samples

The local examples intentionally use deterministic stubs and do not require framework packages, model API keys, network calls, or live side effects.

```bash
python examples/langgraph/demo.py
python examples/crewai/demo.py
python examples/autogen/demo.py
python examples/langsmith/demo.py
python examples/langchain/demo.py
python examples/llamaindex/demo.py
```

Run the shared adapter regression tests:

```bash
pytest -q tests/test_framework_adapters.py
```

## Safe workflow recipe

### 1. Treat the model as a proposer

Convert the model or framework tool proposal into an `EvaluationRequest`. Do not allow the model to choose its own tenant, reviewer, policy version, approval state, or evidence authority.

```python
request = EvaluationRequest(
    agent_id="support-agent",
    context="synthetic support ticket",
    tool_name="lookup_customer",
    tool_input={"customer_id": "synthetic-001"},
    irreversible=False,
    metadata={"tenant": "tenant-a", "workflow_run": "run-001"},
)
```

### 2. Use one pre-execution boundary

Each framework adapter delegates to the shared `GuardedFrameworkTool` boundary. Do not copy policy decisions into separate LangGraph nodes, CrewAI tools, AutoGen functions, or LangChain callbacks.

```python
result = await adapter.call(request, caller_owned_tool)
if result.executed:
    return result.result
return {"status": result.status, "reason": result.decision.reasoning}
```

A `PROCEED` result is still executed only after the adapter validates the request-bound handoff. `PAUSED`, `REJECTED`, malformed input, provider failure, expired approval, cap exhaustion, and invalid handoff results must not call the underlying tool.

### 3. Make irreversible work explicit

Mark financial, identity, communications, deletion, access-control, and other consequential operations as irreversible. Require an authenticated, scoped human approval before execution.

```python
refund = EvaluationRequest(
    tool_name="issue_refund",
    context="refund requested; approval not yet recorded",
    tool_input={"customer_id": "synthetic-001", "amount": 25},
    irreversible=True,
)
```

The expected safe behavior is pause or reject, not an invented success claim.

### 4. Keep retrieval and telemetry untrusted

Retrieved content can provide evidence for a proposal, but cannot grant authority. Observability systems such as LangSmith can record the decision and trajectory, but cannot modify the decision or authorize a tool call. Redact secrets and protected payloads before telemetry export.

### 5. Test the negative path

Every integration should test at least:

- Empty and malformed tool input.
- Prompt-injection text in retrieved content.
- Wrong tenant and altered tool arguments.
- Missing, expired, or revoked approval.
- Duplicate or replayed handoff.
- Provider timeout or malformed provider output.
- Tool failure after an allowed decision.
- Concurrent duplicate requests.
- A claimed success when the tool was never executed.

## Framework-specific integration notes

### LangGraph

Put HonestAgent at the edge of the node that would cause a side effect. The graph may route `PROCEED`, `PAUSED`, `REJECTED`, and `PROVIDER_FAILURE` to different state transitions. Do not let a graph edge turn a pause into execution.

### CrewAI

Wrap the actual CrewAI tool function, not only the task description or agent prompt. CrewAI planning can propose the call; the guarded wrapper decides whether the caller-owned function runs.

### AutoGen/AG2

Apply the boundary to the registered function tool or executor callback. A conversation message that contains a function call is still a proposal until the request-bound handoff is validated.

### LangSmith

Use tracing for visibility, evaluation, and incident investigation. Never use trace metadata as an authorization source. Export only redacted decision metadata and authenticated context.

### LangChain and LlamaIndex

Wrap the tool or retrieval-to-action boundary. Citations and retrieved nodes can be passed as evidence, but the guard must independently enforce tenant, policy, approval, destination, and expiry constraints.

## What these samples do not prove

These examples are local, synthetic demonstrations. They do not prove compatibility with every framework release, model-provider reliability, hosted LangSmith controls, production identity integration, registry signing, deployment safety, regulatory compliance, or production readiness. Pin framework versions and run the conformance and deployment evidence required by the target environment.
