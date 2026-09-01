# Change Log — STD-2 Python Developer Experience and CLI

| Field | Value |
|---|---|
| Sprint | STD-2 |
| Change type | SDK / CLI / test / documentation |
| Date | 2026-09-01 |
| Related commit | `e4f3741` |
| Evidence class | Local source and offline execution evidence |

## Change

Added a stable Python facade over the existing `HonestGuard` and `GuardedFrameworkTool` boundary. `HonestAgent.invoke` returns a typed adapter result, `HonestAgent.check` exposes a direct decision call, `make_request` builds the current request model, and `protect` supplies an async decorator that raises `GuardBlocked` for any non-proceed result.

Added the `honest-agent` CLI with a non-destructive `init` command and a temporary-storage, credential-free `demo` command. Registered the CLI in `pyproject.toml`. Added migration and quickstart documentation.

## Defect correction

The first tests used empty grounding context and correctly received `PAUSED` from the existing verifier. The synthetic SDK and CLI fixtures were corrected to include explicit local context. The safety kernel was not weakened.

## Validation

| Check | Result |
|---|---|
| STD-2 targeted tests | PASS — 3 tests |
| Offline CLI demo | PASS — synthetic, credential-free, executed true |
| Full regression suite | PASS — 132 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security and limitations

The SDK delegates authorization to the existing guard and handoff validation. It never executes the tool for a paused, rejected, capped, or invalid-handoff decision. The CLI does not contact providers or perform irreversible actions. Production identity, durable workflow state, and framework-native integrations remain later sprint work.

## Rollback

Revert the SDK, CLI, metadata, tests, and documentation changes. Existing core and adapter APIs remain available.

## Next action

Implement STD-3 RAG safety reference workflow on top of the stable SDK and conformance boundaries.
