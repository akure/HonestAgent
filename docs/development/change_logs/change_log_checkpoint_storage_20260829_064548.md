# Change Log — transactional checkpoint storage

| Field | Value |
|---|---|
| Change ID | `LR-2` |
| Feature | `Transactional multi-process checkpoint storage` |
| Timestamp UTC | `2026-08-29 06:45:48` |
| Status | `complete` |

## Problem

The MVP checkpoint store cached a JSON document in process memory and protected writes with a Python thread lock. That prevented concurrent mutation inside one process but did not provide cross-process serialization or reload-on-read semantics. A reviewer operation in a second worker could therefore observe stale state or race a first resolution.

## Change

Added a file-backed transactional boundary using a separate lock file and `fcntl.flock`, reload-on-read, process-unique temporary files, and atomic `os.replace`. Added `resolve_pending` as a compare-and-set operation: the first process resolving a pending trajectory wins, while concurrent resolvers receive the durable winner. Added record timestamps and configurable retention pruning. Guardrail resolution now uses this store operation instead of a non-transactional read-modify-write sequence.

The implementation uses the smallest capability required for the observed failure mode: durable shared memory plus deterministic compare-and-set. No model judgment or executor side effect was added.

## Live experiment log

| Stage | What was tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | In-process `threading.RLock` around cached JSON state | Existing regression suite passed, but no cross-process guarantee existed | Replaced; thread locking is insufficient for multiple workers |
| Iteration 1 | Lock-file transaction with reload-on-read and atomic replacement | LR-2 tests passed, including two-process resolution race | Kept |
| Iteration 2 | Persist retention pruning during reads | Retention test passed and expired records were removed from durable state | Kept |

## Safety invariants

| Invariant | Result |
|---|---|
| Checkpoint resolution is deterministic and fail-safe under contention | `PASS` |
| At most one durable resolution wins | `PASS` |
| Pending state is removed only with the winning resolution | `PASS` |
| Handoff issuance and human checkpoint remain explicit post-evaluation steps | `PASS` |
| Core evaluation does not invoke external side effects | `PASS` |

## Validation

- `pytest -q`: **38 passed**
- Restart durability test: **PASS**
- Cross-process compare-and-set test: **PASS**
- Retention pruning test: **PASS**
- `git diff --check`: **PASS**

## Known limitations

This store improves the local and single-host pilot boundary but remains a file-backed store. It is not a substitute for a relational or distributed transactional database in a horizontally scaled production deployment. LR-2 closes the required MVP-to-pilot durability control; a production migration path remains an operational deployment decision.
