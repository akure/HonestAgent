# Change Log — CX-2 intent canonicalization and handoff v2

| Field | Value |
|---|---|
| Phase | `CX2` |
| Feature | `ToolIntent` canonicalization and workflow-bound handoff v2 |
| Timestamp UTC | `2026-08-30 15:22:46` |
| Status | `complete` |

## Problem

CX0 defined workflow and intent contracts, but the existing handoff bound only the legacy request tool/payload, trajectory, policy version, and expiry. A stronger envelope was required so a handoff could not be replayed across tenants, workflow steps, attempts, evidence snapshots, destinations, or semantically altered arguments.

## Change

Added `ExecutionHandoffV2` and `HandoffSigner.issue_v2()` / `validate_v2()`. The signed claims bind contract version, run ID, step ID, attempt, tenant ID, policy snapshot, evidence snapshot, canonical intent hash, destination, and bounded expiry. `ToolIntent.canonical_hash()` uses deterministic sorted JSON and SHA-256. Added `CallableExecutor.execute_v2()` so supported tool integrations can enforce the stronger envelope immediately before invocation. Existing v1 handoffs remain available only through the existing explicit compatibility path.

## Verification

| Check | Result |
|---|---|
| Equivalent argument key ordering produces same intent hash | `PASS` |
| Altered argument produces different intent hash | `PASS` |
| Tenant mutation rejected | `PASS` |
| Step mutation rejected | `PASS` |
| Attempt mutation rejected | `PASS` |
| Evidence snapshot mutation rejected | `PASS` |
| Destination mutation rejected | `PASS` |
| Expired v2 handoff rejected | `PASS` |
| Invalid v2 handoff produces zero side effects | `PASS` |
| Async v2 executor path | `PASS` |
| Full regression suite | `89 passed` |
| Formatting check | `PASS` |

## Decision

CX-2 is **complete**. New workflow-aware consequential integrations can use handoff v2. The existing legacy handoff remains a compatibility path and must not be treated as equivalent to v2 for new consequential workflows.

## Safety invariants

| Invariant | Result |
|---|---|
| Handoff is bound to current workflow identity and attempt | `PASS` |
| Handoff is bound to intent and destination | `PASS` |
| Handoff is bound to policy and evidence snapshot | `PASS` |
| Expiry is enforced | `PASS` |
| Invalid handoff reaches zero side effects | `PASS` |
