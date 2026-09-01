# STD-2 Python Developer Experience and CLI

## Quickstart

Install the package with its development extras in a clean environment:

```bash
python -m pip install -e '.[dev]'
honest-agent demo
```

The demo uses synthetic data, local temporary storage, no provider credentials, no network calls, and a stub tool. It prints a machine-readable result and exercises the same `HonestGuard` pre-execution boundary used by framework adapters.

Create a starter file without overwriting an existing file:

```bash
honest-agent init my_agent.py
```

Use `--force` only when intentionally replacing the file.

## Python API

```python
from honest_agent import HonestAgent, make_request

agent = HonestAgent()
request = make_request(
    "lookup_customer",
    {"customer_id": "synthetic-001"},
    context="Find the synthetic customer record",
)
result = await agent.invoke(request, lookup_customer)
if result.executed:
    print(result.result)
else:
    print(result.status, result.decision.reasoning)
```

For a decorator-style boundary:

```python
from honest_agent import HonestAgent

agent = HonestAgent()

@agent.protect("lookup_customer")
async def lookup_customer(customer_id: str):
    return {"customer_id": customer_id}

value = await lookup_customer(customer_id="synthetic-001")
```

The decorated callable is always asynchronous because authorization precedes tool execution. A `GuardBlocked` exception is raised when the decision is paused, rejected, or capped. The exception exposes the complete typed decision for caller-controlled handling. A guarded tool is never called when the guard does not return `PROCEED` and the existing handoff validation fails.

## Migration from direct tool calls

Replace:

```python
result = tool(**arguments)
```

with:

```python
request = make_request(tool_name, arguments, context=task_context)
result = await agent.invoke(request, tool)
if result.status != "PROCEED":
    return result.decision
return result.result
```

Do not authorize based on model text, retrieved content, or a caller-supplied `approved` boolean. Put retrieval evidence in the evidence boundary and use a trusted reviewer flow for consequential actions.

## CLI contract

| Command | Behavior |
|---|---|
| `honest-agent demo` | Runs one offline synthetic guarded read and emits JSON |
| `honest-agent init PATH` | Creates a starter file only when `PATH` does not exist |
| `honest-agent init PATH --force` | Explicitly replaces the starter file |

The CLI does not collect, print, or require credentials. It does not invoke a live model, external service, or irreversible tool.

## STD-2 evidence boundary

This is a local developer-experience checkpoint. It proves a usable Python facade over the existing guard and handoff boundary, not framework-version compatibility, production identity, external service safety, or independent conformance. Those claims require later STD-7 through STD-10 evidence.
