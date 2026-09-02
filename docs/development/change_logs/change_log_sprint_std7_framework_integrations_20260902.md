# Change Log — STD-7 Version-Pinned Framework Integrations

| Field | Value |
|---|---|
| Sprint | STD-7 |
| Change type | framework integration / lifecycle / compatibility / test |
| Date | 2026-09-02 |
| Related commit | `5937df7` |
| Evidence class | Local synthetic adapter-boundary evidence |

## Change

Added a version-pinned compatibility boundary for a LangGraph graph integration (`0.2.53`) and the STD-3 RAG reference (`std3`). Unsupported versions fail closed. Added native adapter operations for cancellation and approval resume while retaining the existing guard and signed handoff boundary.

Added tests for supported/unsupported versions, proceed, pause, reject/failure via existing conformance, cancellation, resume, and handoff enforcement.

## Defect discovered and corrected

The initial resume path approved an irreversible request and then sent it through normal evaluation again, causing a second pause. The corrected path directly validates and executes the newly approved request-bound handoff, with no second authorization and no bypass.

## Validation

| Check | Result |
|---|---|
| STD-7 focused tests | PASS — 3 tests |
| Existing framework adapter tests | PASS — 15 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |
| Unsupported-version rejection | PASS |
| Cancellation isolation | PASS |
| Native pause/resume | PASS |
| Altered-handoff protection | PASS |

## Security and limitations

The adapter cannot prove compatibility with uninstalled framework packages or all framework versions. Provider/network behavior, true streaming, distributed persistence, and framework-native serialization remain unmeasured. Local tests use synthetic state and no credentials or live side effects.

## Rollback

Revert the compatibility module, adapter exports, tests, compatibility matrix, and evidence documents. Existing generic wrappers remain available.

## Next action

Implement STD-8 independent reproduction and benchmark evidence.
