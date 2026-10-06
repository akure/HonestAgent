# Change Log — Framework Mini Use Cases — 2026-10-06

## Scope

Add small, credential-free examples showing how framework proposals pass through HonestAgent before tool execution, with LangSmith represented as observability rather than authority.

## Changes

- Added `examples/README.md` as the integration guide.
- Expanded LangGraph, CrewAI, AutoGen, and LangChain demos with safe and blocked proposals.
- Added `examples/langsmith/adapter.py`, `demo.py`, `README.md`, and optional dependency notes.
- Added sprint trace evidence.

## Measured evidence

The following commands ran successfully for the demos:

```bash
python examples/langgraph/demo.py
python examples/crewai/demo.py
python examples/autogen/demo.py
python examples/langsmith/demo.py
python examples/langchain/demo.py
python -m compileall -q examples honest_agent tests
```

Observed behavior included proceeding read-only actions and pausing irreversible actions without executing the caller-owned tool. The adapter pytest suite was not run because `pytest` is unavailable in the restored execution environment.

## Evidence boundary

This is local synthetic evidence. No framework package, model provider, LangSmith service, API key, network call, or live side effect was used. The examples do not establish production compatibility or hosted observability readiness.

## Commit

Implementation commit: `PENDING`
