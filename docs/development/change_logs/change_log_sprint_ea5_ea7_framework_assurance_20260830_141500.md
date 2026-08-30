# Change Log — EA-5 through EA-7 Framework Examples and Assurance

| Field | Value |
|---|---|
| Change ID | EA-5–EA-7 |
| Change type | feature / test / security / documentation |
| Milestone / sprint | EA-5 / EA-6 / EA-7 |
| Timestamp UTC | 2026-08-30 14:18:00 |
| Author | HonestAgent development agent |
| Related task | 7YvScDgTHokKogC36QYAFt |
| Related commit | `bccb2f1` |

## Problem

HonestAgent had domain packs but no practical mainstream-framework integration surface or cross-domain assurance record. Framework users need one safe pre-execution contract, while enterprise reviewers need evidence that paused, rejected, failed, or altered requests cannot reach caller-owned tools.

## Change

Added a framework-neutral `GuardedFrameworkTool` contract and five thin examples for LangChain, LangGraph, CrewAI, AutoGen/AG2, and LlamaIndex. Every example has an adapter, README, no-credential requirements manifest, and runnable deterministic demo. Added shared conformance tests covering proceed, pause, reject, provider failure, and altered-argument handoff rejection. Added six-domain hard-stop and tenant-isolation tests, compatibility/security documentation, a cross-domain assurance matrix, and a threat-model update.

## Files changed

| File or directory | Role | Behavior impact |
|---|---|---|
| `honest_agent/adapters/contract.py` and `honest_agent/adapters/__init__.py` | implementation/API | Shared guarded adapter boundary and result type. |
| `examples/langchain`, `examples/langgraph`, `examples/crewai`, `examples/autogen`, `examples/llamaindex` | examples | Credential-free framework-shaped wrappers, demos, and local manifests. |
| `tests/test_framework_adapters.py` | regression | Five-adapter conformance tests. |
| `tests/test_ea7_cross_domain_assurance.py` | assurance | All-six-domain hard-stop and tenant-isolation checks. |
| `docs/development/framework-adapter-compatibility-ea6_20260830.md` | compatibility | Version/support boundary and security review. |
| `docs/release/ea7-cross-domain-assurance-matrix_20260830.md` | evidence | Domain/control/test matrix and reproduction commands. |
| `docs/security/enterprise-adaptability-threat-model-ea7_20260830.md` | security | EA-7 threat-model update. |
| `docs/development/sprint_traces/sprint_ea5_ea7_framework_assurance_20260830.md` | evidence | Combined milestone trace. |

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `pytest -q tests/test_framework_adapters.py` | PASS | 15 tests passed. |
| `pytest -q tests/test_ea7_cross_domain_assurance.py` | PASS | 2 tests passed. |
| `pytest -q` | PASS | 120 tests passed. |
| Five demo commands | PASS | All five returned synthetic `PROCEED` without credentials or network. |
| JSON validation and `git diff --check` | PASS | Artifacts parse and diff is clean. |

## Risk and limitations

These are framework-shaped examples, not claims of support for every framework version. Optional framework packages are intentionally not installed in the core environment. No live provider, payment, trading, clinical, employment, support, or planning action is executed. Production key custody, identity, egress, audit, monitoring, kill-switch, distributed replay, and target-deployment evidence remain open.

## Rollback or mitigation

Remove or ignore the optional examples and retain the core package; the generic kernel and domain packs remain independently usable. The adapter contract is additive and can be disabled by not wiring an adapter into a caller. Revert the example directories if a framework-specific compatibility issue is found.

## Next action

Review the combined EA-5–EA-7 evidence. Before any production or commercial claim, add pinned framework-version integration tests and deployment-specific evidence. Do not claim that local synthetic examples establish regulatory, security, or customer validation.
