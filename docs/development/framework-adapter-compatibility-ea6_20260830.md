# Framework Adapter Compatibility — EA-6

## Status and support boundary

The examples in this repository are **framework-shaped, dependency-free contract demonstrations**. They are not claims of support for every release of the named frameworks. Each adapter delegates to the same public `honest_agent.adapters.GuardedFrameworkTool` boundary and uses local deterministic stubs.

| Example | Framework target | Tested mode | External dependency | Production claim |
|---|---|---|---|---|
| `examples/langchain` | LangChain `StructuredTool` shape | Local wrapper | None | None; pin the application’s LangChain version separately. |
| `examples/langgraph` | LangGraph state-node shape | Local state transition wrapper | None | None; persist trajectory state in the application checkpoint system. |
| `examples/crewai` | CrewAI task/tool shape | Local guarded tool boundary | None | None; do not expose the underlying callable to unrestricted agents. |
| `examples/autogen` | AutoGen/AG2 function-tool shape | Local function boundary | None | None; stop automatic continuation on `PAUSED` or `REJECTED`. |
| `examples/llamaindex` | LlamaIndex tool/workflow shape | Local callback wrapper | None | None; retrieved text is untrusted and cannot authorize execution. |

## Common semantics

Every adapter produces the same result vocabulary: `PROCEED`, `PAUSED`, `REJECTED`, `CAP_EXCEEDED`, or `PROVIDER_FAILURE`. The underlying callable is invoked only after the guard returns `PROCEED` and the request-bound, expiring handoff validates. A provider or tool exception is reported as failure; it is never converted into an unverified success.

## Security review

The adapter contract has one pre-execution enforcement point. It copies caller-supplied evidence into request metadata, but does not interpret prompt text or retrieved content as authority. Altering tool arguments after a decision invalidates the handoff. The adapters do not retry rejected actions with modified arguments, do not perform network calls, and do not store credentials. Framework state may resume a proposal, but it cannot bypass `validate_handoff`.

## Clean-checkout command

```bash
for framework in langchain langgraph crewai autogen llamaindex; do
  python "examples/$framework/demo.py"
done
pytest -q tests/test_framework_adapters.py
```

These commands use only repository code and synthetic data. Actual framework integration must add a pinned optional dependency, repeat the conformance suite, and document the tested version before being advertised.
