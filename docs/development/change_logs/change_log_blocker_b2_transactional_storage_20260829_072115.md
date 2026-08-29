# Change Log — B-2 production transactional storage

| Field | Value |
|---|---|
| Change ID | `B-2` |
| Feature | `Transactional SQLite checkpoint backend with backup and restore` |
| Timestamp UTC | `2026-08-29 07:21:15` |
| Status | `complete for durable-volume/single-host production-like deployment` |

## Problem

The pilot file-backed store had cross-process locking and compare-and-set behavior, but unrestricted production still lacked a transactional database backend with a structured schema, WAL durability, backup, restore, and production-mode selection.

## Change

Added `SQLiteCheckpointStore` with transactional tables, WAL mode, indexed state/timestamp access, `BEGIN IMMEDIATE` resolution, atomic single-winner compare-and-set semantics, retention pruning, backup, and restore. Added validated configuration fields and wired `HonestGuard` to select SQLite when `checkpoint_backend=sqlite`; the file backend remains the explicit development/pilot default.

## Evidence

| Check | Result |
|---|---|
| SQLite restart durability | `PASS` |
| Cross-process single-winner resolution | `PASS` |
| Backup and restore | `PASS` |
| Full regression suite | `71 passed` |
| Formatting check | `PASS` |

## Decision

B-2 is **closed for production-like single-host durable-volume deployment**. A managed relational database, HA topology, and formal RTO/RPO drill remain required before unrestricted horizontally scaled production.

## Safety invariants

| Invariant | Result |
|---|---|
| Resolution remains deterministic and single-winner | `PASS` |
| Pending state is not retained after resolution | `PASS` |
| Backup/restore preserves checkpoint state | `PASS` |
| File-backed pilot compatibility remains explicit | `PASS` |
