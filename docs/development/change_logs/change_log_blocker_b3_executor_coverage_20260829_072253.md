# Change Log — B-3 third-party executor coverage

| Field | Value |
|---|---|
| Change ID | `B-3` |
| Feature | `CallableExecutor` handoff enforcement adapter |
| Timestamp UTC | `2026-08-29 07:22:53` |
| Status | `complete for supported callable executor boundary` |

## Problem

LR-3 enforced handoffs at the application gateway, but third-party tool integrations could still implement their own invocation path unless they used a shared enforcement contract. The remaining blocker was to provide and test an executor adapter that validates immediately before invoking synchronous or asynchronous callables.

## Change

Added `CallableExecutor`, a reusable adapter that requires a request-bound valid handoff before invoking a tool function. It validates missing, malformed, altered-payload, and altered-trajectory handoffs through the existing guardrail signer. Invalid requests raise `ExecutionBlocked` before the callable is reached; valid synchronous and asynchronous callables are supported.

## Evidence

| Check | Result |
|---|---|
| Valid synchronous callable invoked once | `PASS` |
| Missing handoff invokes zero times | `PASS` |
| Invalid handoff invokes zero times | `PASS` |
| Altered payload/replay invokes zero times | `PASS` |
| Async callable support | `PASS` |
| Full regression suite | `75 passed` |
| Formatting check | `PASS` |

## Decision

B-3 is **closed for integrations using the supported adapter contract**. Each real third-party executor must be inventoried and migrated to this adapter or demonstrate equivalent enforcement in a deployment-specific integration test. The release remains conservative until that inventory is complete.

## Safety invariants

| Invariant | Result |
|---|---|
| Validation occurs before callable invocation | `PASS` |
| Invalid handoffs produce zero side effects | `PASS` |
| Handoff remains bound to trajectory and payload | `PASS` |
| Core authorization remains deterministic | `PASS` |
