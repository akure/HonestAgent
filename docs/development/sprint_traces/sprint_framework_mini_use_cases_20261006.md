# Sprint Trace — Framework Mini Use Cases

| Field | Value |
|---|---|
| Sprint | Framework mini use cases |
| Objective | Demonstrate safe HonestAgent integration with LangGraph, CrewAI, AutoGen, LangSmith-style observability, LangChain, and LlamaIndex boundaries |
| Date | 2026-10-06 |
| Status | Complete |
| Evidence class | Local synthetic |
| Commit | `PENDING` |

## Baseline risk

The existing framework samples showed a generic adapter call but did not provide a consolidated use-case guide or an observability-specific example. Users could copy a framework wrapper without seeing the distinction between model proposals, guard decisions, tool execution, and telemetry.

## Delivered

- Added a unified `examples/README.md` with a framework matrix, safe workflow recipe, negative-test checklist, and production limitations.
- Upgraded LangGraph, CrewAI, AutoGen, and LangChain demos with one read-only proposal that proceeds and one irreversible proposal that pauses.
- Added a credential-free LangSmith-style observability boundary and JSONL trace demo.
- Added optional LangSmith dependency guidance without making the local sample depend on network access or API keys.

## Defect discovered and corrected

The prior demos exercised only a proceeding lookup. They did not visibly demonstrate the safety behavior for irreversible actions. Each demo now prints both `PROCEED/executed=True` and `PAUSED/executed=False` cases.

## Verification

| Check | Result |
|---|---|
| LangGraph demo | `PROCEED/True` lookup; `PAUSED/False` refund |
| CrewAI demo | `PROCEED/True` read; `PAUSED/False` outbound message |
| AutoGen demo | `PROCEED/True` order status; `PAUSED/False` address change |
| LangSmith demo | Redacted local trace records for proceed and pause |
| LangChain demo | `PROCEED/True` retrieval; `PAUSED/False` deletion |
| Python compilation | Passed for `examples`, `honest_agent`, and `tests` |
| `git diff --check` | Passed |
| Pytest adapter suite | Not run: `pytest` is unavailable in the restored execution environment |

## Security invariants

- Framework and model output remain untrusted proposals.
- LangSmith-style telemetry records decisions but cannot authorize execution.
- Irreversible actions require an explicit guard decision and are paused without approval.
- Tool invocation occurs only through the shared request-bound handoff boundary.
- Samples contain synthetic data, no credentials, no network calls, and no live side effects.

## Limitations

The examples are dependency-free local demonstrations. They do not prove compatibility with every released version of LangGraph, CrewAI, AutoGen/AG2, LangSmith, LangChain, or LlamaIndex. Hosted LangSmith retention, production identity, registry signing, deployment, and regulatory controls remain unmeasured.

## Rollback

Revert the example and documentation files from this checkpoint. No runtime protocol or policy behavior was changed.

## Next checkpoint

Install the project development dependencies and run the complete adapter regression suite, then validate one pinned version of each framework in an isolated integration environment.
