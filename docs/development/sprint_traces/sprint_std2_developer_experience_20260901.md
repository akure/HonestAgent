# Sprint Trace — STD-2 Python Developer Experience and CLI

| Field | Value |
|---|---|
| Sprint | STD-2 |
| Objective | Make the existing fail-closed guard easy to adopt from Python without creating a second authorization path. |
| Date | 2026-09-01 |
| Status | Complete |
| Evidence class | Local source, offline CLI, and regression tests |

## Delivered

| Deliverable | Artifact |
|---|---|
| Python SDK facade | `honest_agent/sdk.py` |
| Public helper exports | `honest_agent/__init__.py` |
| CLI | `honest_agent/cli.py` and `honest-agent` project script |
| Quickstart and migration guide | `docs/development/python-sdk-and-cli-std2_20260901.md` |
| SDK/CLI tests | `tests/test_std2_developer_experience.py` |

The SDK exposes `HonestAgent.check`, `HonestAgent.invoke`, `HonestAgent.protect`, `make_request`, and typed `GuardBlocked`. Invocation delegates to the existing `GuardedFrameworkTool` and `HonestGuard`; it does not authorize independently. The CLI provides a non-destructive `init` command and an offline synthetic `demo` command.

## Defect discovered and corrected

The first adoption fixtures omitted grounding context. The existing verifier correctly paused those calls because empty context is unsafe. The SDK test and CLI demo were corrected to provide explicit synthetic context; no fail-open kernel change was made.

## Validation

| Check | Result |
|---|---|
| STD-2 targeted tests | PASS — 3 tests |
| Offline CLI demo | PASS — `PROCEED`, executed true, credential-free |
| Full regression suite | PASS — 132 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Limitations

STD-2 is a local Python adoption layer. It does not prove framework-version compatibility, production identity, external side-effect safety, independent conformance, or regulatory readiness. The decorated callable is always asynchronous, and blocked decisions require caller handling or explicit review flows.

## Next checkpoint

Proceed to **STD-3 — RAG safety reference workflow**, using the SDK and STD-1 runner as the adoption baseline.
