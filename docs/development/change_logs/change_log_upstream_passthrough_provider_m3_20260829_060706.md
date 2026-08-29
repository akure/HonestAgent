# Change Log — upstream passthrough and provider boundary

| Field | Value |
|---|---|
| Change ID | `HA-M3-001` |
| Change type | `feature` and integration boundary |
| Milestone / sprint | `M3 / Sprint 4` |
| Timestamp UTC | `2026-08-29 06:07:06` |
| Related tasks | `HA-008`, `HA-010` |
| Related commit | `{filled after commit}` |

## Problem

The proxy returned a simulated completion even when a customer needed a real upstream path. Provider integration was also implicit, so malformed or unavailable provider responses had no dedicated contract test.

## Change

Added an optional `OpenAICompatibleVerifierProvider` with structured response validation and an injectable HTTP client, plus an `UpstreamClient` that forwards only after the guard returns `PROCEED`. Local simulation remains the default when no upstream URL is configured. Paused actions never call the upstream client, and upstream failures return a structured error without changing the guard decision.

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `python3 -m pytest -q` | `PASS` | 28 tests passed. |
| Provider contract | `PASS` | Mocked structured response parsed; malformed response raises `ProviderContractError`. |
| Upstream forwarding | `PASS` | Mock transport observed exactly one safe request. |
| Pause gate | `PASS` | Paused proxy request observed zero upstream calls. |

## Risk and limitations

The provider adapter is OpenAI-compatible and optional; no live provider credentials are used in CI. Streaming, provider-specific authentication, retries, and cost accounting remain limited. The upstream client must be configured with a trusted base URL; production deployments still need SSRF controls, request authentication, and timeout budgets.

## Rollback or mitigation

Unset `HONEST_AGENT_UPSTREAM_URL` to return to local simulation. Keep the paused-action gate in place and do not bypass the guard when upstream calls fail.

## Next action

Proceed to M4: add pilot tooling, reproducible integration examples, control-readiness evidence export, and production-readiness documentation.
