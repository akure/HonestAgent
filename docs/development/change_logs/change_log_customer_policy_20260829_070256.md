# Change Log — customer policy onboarding and rollback

| Field | Value |
|---|---|
| Change ID | `LR-6` |
| Feature | `Customer policy onboarding, version activation, and rollback` |
| Timestamp UTC | `2026-08-29 07:02:56` |
| Status | `complete` |

## Problem

The MVP had a deterministic built-in policy registry and a simulation helper, but no durable customer lifecycle for importing a policy, previewing its effect, requiring an approval, activating a version, or rolling back to a previously approved version. A customer could not safely govern policy changes as auditable releases.

## Change

Added `PolicyRegistry`, a durable file-backed lifecycle boundary for customer policy versions. Imported policies require a safe version identifier, an importer identity, and at least one validated `PolicyRule`. Each version can be simulated before activation. Activation is blocked until an explicit approval identity is recorded, and activation records the prior active version and actor. Rollback is an explicit activation of a different approved version. `HonestGuard` now accepts a registry and exposes explicit activation and rollback methods that replace the deterministic runtime policy only after the registry gate succeeds.

The model remains outside authorization: simulation is deterministic, and no customer policy becomes active without validation and approval.

## Live experiment log

| Stage | What was tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Built-in in-memory `ActionPolicy` plus offline simulation | Existing policy tests passed, but customer changes had no durable approval lifecycle | Replaced for customer-managed operation |
| Iteration 1 | Durable version registry with safe identifiers and validated rules | Import validation and restart tests passed | Kept |
| Iteration 2 | Simulation before activation | Simulation showed policy outcome and version without changing active policy | Kept |
| Iteration 3 | Approval-gated activation with actor attribution | Activation without approval failed; approved activation succeeded | Kept |
| Iteration 4 | Explicit rollback through the same activation gate | Runtime policy returned to prior approved version | Kept; rollback is a controlled release, not an ad hoc mutation |

## Safety invariants

| Invariant | Result |
|---|---|
| Invalid policy documents cannot enter the registry | `PASS` |
| Simulation cannot activate or execute a policy | `PASS` |
| Unapproved policies cannot become active | `PASS` |
| Activation and rollback require an actor identity | `PASS` |
| Runtime classification remains deterministic | `PASS` |
| Policy version is carried into resulting decisions | `PASS` |

## Validation

- `pytest -q`: **61 passed**
- Import validation: **PASS**
- Approval-gated activation: **PASS**
- Simulation without activation: **PASS**
- Restart persistence: **PASS**
- Runtime activation and rollback: **PASS**
- `git diff --check`: **PASS**

## Known limitations

The registry is file-backed for the current single-host pilot and should use the transactional database boundary planned for production-scale policy management. Multi-party approval quorum, customer identity-provider integration, and signed policy bundles remain future hardening work.
