# Change Log — STD-10D Operational Dashboards, Alerting, and Kill-Switch Operations

| Field | Value |
|---|---|
| Sprint | STD-10D |
| Change type | operations / dashboard / alerting / kill switch |
| Date | 2026-09-03 |
| Related commit | `cbbd184` |
| Evidence class | Local synthetic / deployment-neutral |

## Change

Added durable actor-attributed control events and read-only operational snapshots to `IntentStore`. Added deterministic threshold alert evaluation and dashboard construction. Existing transactional tenant/workflow/tool/global kill-switch enforcement remains unchanged and fail-closed.

## Validation

| Check | Result |
|---|---|
| STD-10D operational tests | PASS — 4 tests |
| STD-6 execution regressions | PASS — 4 tests |
| Combined focused result | PASS — 8 tests |
| Full suite | PASS — 176 tests |

## Evidence boundary

The result is local synthetic reference evidence. It does not establish production telemetry, external paging, alert delivery, operator authentication, break-glass approval, immutable event forwarding, or multi-region operational readiness.

## Rollback

Revert the additive event table/API, operations helper, tests, and STD-10D evidence files. Existing execution control rows remain compatible.

## Next action

Stage STD-10E deployment packaging and commercial operational boundaries separately after review.
