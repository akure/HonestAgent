# Sprint Trace — STD-7 Version-Pinned Framework Integrations

| Field | Value |
|---|---|
| Sprint | STD-7 |
| Objective | Prevent framework state from bypassing the control plane through explicit version boundaries and native lifecycle-safe graph/RAG adapters. |
| Date | 2026-09-02 |
| Status | Complete |
| Evidence class | Local synthetic adapter-boundary evidence |
| Commit | `5937df7` |

## Baseline risk

The repository had five generic framework-shaped wrappers, but no explicit supported-version registry or native lifecycle contract. Framework-shaped examples could be mistaken for proof of compatibility with actual framework releases.

## Delivered

| Deliverable | Artifact |
|---|---|
| Version boundary and lifecycle adapter | `honest_agent/adapters/compatibility.py` |
| Adapter exports | `honest_agent/adapters/__init__.py` |
| STD-7 tests | `tests/test_std7_framework_integrations.py` |
| Compatibility matrix | `docs/development/framework-compatibility-std7_20260902.md` |

The checkpoint explicitly pins the local LangGraph boundary at `0.2.53` and the RAG reference at `std3`. Unsupported versions are rejected. The adapter covers proceed, pause, reject, provider failure, cancellation, resume, state, and request-bound handoff validation. Existing LangChain, CrewAI, AutoGen/AG2, and LlamaIndex wrappers remain generic and are marked unmeasured for actual package compatibility.

## Defect discovered and corrected

The first native resume path approved a paused irreversible request and then re-submitted it through normal evaluation, producing a second `PAUSED` result. Resume now executes only after approval and direct request-bound handoff validation, avoiding duplicate authorization while preserving the guard boundary.

## Verification

| Check | Result |
|---|---|
| STD-7 focused tests | PASS — 3 tests |
| Existing framework adapter tests | PASS — 15 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |
| Unsupported version rejection | PASS |
| Native pause/resume | PASS |
| Cancellation before tool call | PASS |
| Handoff boundary | PASS |

## Security invariants

Unsupported versions fail closed. Framework cancellation prevents tool invocation. Resume requires an existing approved trajectory and validates the signed handoff against the original request and trajectory. Framework state and model messages cannot authorize execution.

## Limitations

This is local adapter-boundary evidence, not proof of actual installed framework compatibility. Provider behavior, streaming, distributed persistence, external cancellation delivery, and framework-specific state serialization remain unmeasured. Full real-framework integration should be performed only in a separately pinned environment with reproducible dependency locks.

## Rollback

Revert the compatibility adapter, exports, tests, compatibility documentation, and this evidence record. Existing generic wrappers remain available.

## Next checkpoint

Proceed to **STD-8 — Independent Reproduction and Benchmark Evidence**.
