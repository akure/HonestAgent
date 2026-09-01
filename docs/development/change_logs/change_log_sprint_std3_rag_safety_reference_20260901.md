# Change Log — STD-3 RAG Safety Reference Workflow

| Field | Value |
|---|---|
| Sprint | STD-3 |
| Change type | RAG / workflow / safety / test |
| Date | 2026-09-01 |
| Related commit | Pending |
| Evidence class | Local synthetic and deterministic test evidence |

## Change

Added `RAGSafetyWorkflow`, a framework-neutral reference composition over the existing CX-3 `RAGEvidenceBoundary` and STD-2 `HonestAgent` facade. The workflow performs retrieval inspection, high-impact citation coverage, policy evaluation, approval resume, request-bound handoff validation, and stub execution. It returns typed workflow results and never treats retrieved content as authorization.

Added an offline synthetic customer-support example and end-to-end tests covering allowed cited evidence, cross-tenant rejection, prompt-injection isolation, and approved high-impact resume.

## Correction

Approval resume captures the pending request before the existing guard resolves and removes it from the in-memory pending map. This preserves the current checkpoint lifecycle while allowing the reference workflow to validate the newly issued handoff against the original request.

## Validation

| Check | Result |
|---|---|
| STD-3 workflow tests | PASS — 3 tests |
| CX-3 RAG tests | PASS — 4 tests |
| Full regression suite | PASS — 135 tests |
| Synthetic example | PASS — offline, credential-free |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security and limitations

Cross-tenant, stale, disallowed-egress, untrusted high-impact, citation-incomplete, and injection-signaled retrieval cannot reach the tool. The workflow does not provide production vector-store isolation, external identity, durable state-machine guarantees, regulatory certification, or live side-effect safety.

## Rollback

Revert the additive workflow, example, tests, and documentation. Existing CX-3 boundary and STD-2 SDK remain available.

## Next action

Implement STD-4 durable workflow state and human oversight.
