# Sprint Trace — EA-5 through EA-7 Framework Examples and Assurance

| Field | Value |
|---|---|
| Milestone | EA-5 / EA-6 / EA-7 |
| Sprint | Framework examples, compatibility review, and cross-domain assurance |
| Objective | Provide five common adapter examples and local assurance without provider credentials, live side effects, or framework-wide compatibility claims. |
| Start UTC | 2026-08-30 14:12:00 |
| End UTC | 2026-08-30 14:18:00 |
| Status | complete |

## Scope

Implemented dependency-free, framework-shaped examples for LangChain, LangGraph, CrewAI, AutoGen/AG2, and LlamaIndex over one shared guarded-tool contract. Added local deterministic demos, conformance tests, compatibility/security documentation, a six-domain assurance matrix, and an EA-7 threat-model update. Deferred are actual optional framework installs/version pins, live provider tests, production deployment evidence, and real external side effects.

## Execution trace

| Order | Task | Action | Result | Evidence |
|---:|---|---|---|---|
| 1 | EA-5 | implemented | Added shared `GuardedFrameworkTool` with one pre-execution gate, handoff validation, and provider-failure handling. | `honest_agent/adapters/contract.py` |
| 2 | EA-5/6 | implemented | Added LangChain, LangGraph, CrewAI, AutoGen/AG2, and LlamaIndex wrappers with clean-checkout demos and local manifests. | `examples/{langchain,langgraph,crewai,autogen,llamaindex}` |
| 3 | EA-5/6 | tested | Ran shared proceed/pause/reject/provider-failure/altered-handoff conformance cases across all five adapters. | `tests/test_framework_adapters.py` |
| 4 | EA-7 | tested | Ran all-six-domain hard-stop and wrong-tenant assurance cases. | `tests/test_ea7_cross_domain_assurance.py` |
| 5 | EA-7 | documented | Added compatibility matrix, security review, assurance matrix, and threat-model update. | `docs/development/framework-adapter-compatibility-ea6_20260830.md` |

## Failures discovered

No runtime failures remained after implementation. The conformance suite intentionally confirms that underlying tools are not called for paused, rejected, or provider-failure paths and that altered arguments cannot reuse a handoff.

## Decisions and trade-offs

The examples are framework-shaped rather than claiming support for installed framework APIs, because those optional dependencies are not present in the core environment and version compatibility changes rapidly. This preserves a reproducible, credential-free clean-checkout path. Actual integrations must pin a tested framework version and retain the same shared enforcement boundary.

## Validation

| Gate | Command or artifact | Result |
|---|---|---|
| Adapter conformance | `pytest -q tests/test_framework_adapters.py` | PASS — 15 tests |
| Cross-domain assurance | `pytest -q tests/test_ea7_cross_domain_assurance.py` | PASS — 2 tests |
| Full regression | `pytest -q` | PASS — 120 tests |
| Clean-checkout demos | `for framework in langchain langgraph crewai autogen llamaindex; do python examples/$framework/demo.py; done` | PASS — five synthetic `PROCEED` demos |
| JSON/hygiene | `python -m json.tool` and `git diff --check` | PASS |

## Git publication

| Commit | Message | Remote status |
|---|---|---|
| Pending | `feat(examples): add framework adapters and cross-domain assurance` | Pending commit and push |

## Milestone decision

EA-5 through EA-7 are complete for dependency-free local examples and assurance evidence. The project remains NO-GO for unrestricted consequential production use. Production framework support requires pinned-version integration tests, managed identity/secrets, live deployment evidence, and customer-authorized side-effect testing.
