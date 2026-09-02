# STD-7 Framework Compatibility and Native Lifecycle Boundary

## Scope

STD-7 adds a version-bound compatibility registry and a framework-neutral lifecycle adapter. The adapter is the only path from framework state to the existing `GuardedFrameworkTool`; framework wrappers must not call tools directly. Local tests use synthetic framework-shaped state and no provider credentials.

## Compatibility matrix

| Integration | Pin | Kind | Local status | Production claim |
|---|---:|---|---|---|
| LangGraph | `0.2.53` | graph | Tested against adapter boundary | None; dependency is not installed by the repository test suite |
| RAG reference | `std3` | RAG | Tested against STD-3 workflow boundary | None; this is the repository reference workflow, not a vector-store release |
| LangChain | unsupported by STD-7 pin | tool wrapper | Existing generic adapter tests only | Not measured |
| CrewAI | unsupported by STD-7 pin | tool wrapper | Existing generic adapter tests only | Not measured |
| AutoGen/AG2 | unsupported by STD-7 pin | function wrapper | Existing generic adapter tests only | Not measured |
| LlamaIndex | unsupported by STD-7 pin | workflow wrapper | Existing generic adapter tests only | Not measured |

Unsupported versions must be rejected rather than silently treated as compatible. Actual framework package installation, provider behavior, streaming semantics, and framework-native persistence require a separate environment-specific validation run.

## Native lifecycle controls

`VersionPinnedFrameworkAdapter` supports proceed, pause, reject, provider failure, cancellation, resume, and request-bound handoff validation. Cancellation is checked before the underlying tool is called. Resume approves the existing trajectory and executes the newly approved handoff directly; it does not re-submit an irreversible request through the normal evaluation path and therefore cannot create a second pause or bypass approval.

The underlying adapter still validates the signed handoff against the request and trajectory. Altered arguments invalidate the handoff. The framework's state, messages, retrieved content, and callback results remain untrusted proposals.

## Evidence boundary

The STD-7 tests demonstrate the control-plane boundary locally. They do not prove compatibility with every framework release, production streaming, distributed persistence, external cancellation delivery, or provider/network behavior. Those claims remain `NOT MEASURED` until version-pinned environment tests are independently reproduced.
