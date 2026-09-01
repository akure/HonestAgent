# Sprint Trace — STD-3 RAG Safety Reference Workflow

| Field | Value |
|---|---|
| Sprint | STD-3 |
| Objective | Provide an offline end-to-end RAG safety workflow that separates retrieved content from authority and gates execution through HonestGuard. |
| Date | 2026-09-01 |
| Status | Complete |
| Evidence class | Local synthetic and deterministic test evidence |

## Delivered

| Deliverable | Artifact |
|---|---|
| Composable RAG workflow | `honest_agent/rag_workflow.py` |
| Public workflow exports | `honest_agent/__init__.py` |
| End-to-end tests | `tests/test_std3_rag_workflow.py` |
| Synthetic support example | `examples/rag_support/demo.py` |
| Example guide | `examples/rag_support/README.md` |

The workflow executes `retrieve → boundary inspect → citation check → guard → handoff validation → tool stub`. Retrieval must pass the existing CX-3 tenant, source, egress, freshness, trust, and injection gates. High-impact requests require citation coverage. The tool is never called unless the existing guard returns `PROCEED` and the request-bound handoff validates.

## Verification

| Case | Result |
|---|---|
| Fresh trusted cited evidence executes | PASS |
| Cross-tenant content cannot reach tool | PASS |
| Prompt-injection content cannot reach tool | PASS |
| Approved high-impact action resumes and executes | PASS |
| CX-3 boundary regressions | PASS — 4 tests |
| STD-3 workflow tests | PASS — 3 tests |
| Full regression suite | PASS — 135 tests |
| Synthetic example | PASS — offline and credential-free |

## Limitations

This is an offline reference workflow, not a production vector-store connector or regulatory control. Identity, durable workflow state, source ACL enforcement, citation quality, model behavior, and external side-effect semantics remain deployment concerns. The current approval resume path is intentionally built on the existing in-memory/file checkpoint behavior and is not yet a full durable state machine.

## Next checkpoint

Proceed to **STD-4 — Durable workflow state and human oversight**.
