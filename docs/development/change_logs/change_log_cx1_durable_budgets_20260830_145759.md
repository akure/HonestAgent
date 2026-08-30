# Change Log — CX-1 durable workflow context and budgets

| Field | Value |
|---|---|
| Phase | `CX1` |
| Feature | `Durable workflow context and budget accounting` |
| Timestamp UTC | `2026-08-30 14:57:59` |
| Status | `complete` |

## Problem

CX0 defined workflow identity and budget fields, but counters were not durably persisted or atomically consumed. Refresh/resume could reset usage, concurrent workers could oversubscribe a cap, and cancellation or expired deadlines were not represented as typed pre-execution outcomes.

## Change

Added `DurableWorkflowStore` backed by SQLite WAL. It persists workflow context, usage counters, cancellation state, and update timestamps. Reservations use `BEGIN IMMEDIATE` and validate every requested dimension against the immutable context budget before mutating counters. Added typed `BudgetExceeded` with dimension, limit, current, and requested values, plus `WorkflowCancelled`. Added wall-clock budget support to CX0 budgets and retained inherited context identity across resume.

## Verification

| Check | Result |
|---|---|
| Counters survive store restart | `PASS` |
| Concurrent reservations cannot exceed cap | `PASS` |
| Failed reservation leaves usage unchanged | `PASS` |
| Cancellation blocks reservations | `PASS` |
| Expired deadline returns typed cap error | `PASS` |
| Full regression suite | `85 passed` |
| Formatting check | `PASS` |

## Decision

CX-1 is **complete** for the durable single-host workflow context boundary. CX-2 can bind these context and budget identities into the stronger handoff envelope.

## Safety invariants

| Invariant | Result |
|---|---|
| Budget failure is fail-closed before side effects | `PASS` |
| Concurrent workers cannot consume the same remaining cap | `PASS` |
| Resume does not reset counters | `PASS` |
| Cancellation is terminal for reservation | `PASS` |
| Context authority remains attenuated | `PASS` |
