# Sprint Trace — STD-10D Operational Dashboards, Alerting, and Kill-Switch Operations

| Field | Value |
|---|---|
| Sprint | STD-10D |
| Objective | Add safe read-only operational snapshots, deterministic threshold alerts, and actor-attributed kill-switch operations around the existing durable executor controls. |
| Date | 2026-09-03 |
| Status | Complete |
| Evidence class | Local synthetic / deployment-neutral |
| Commit | `cbbd184` |

## Baseline risk

The durable execution store already enforced tenant, workflow, tool, and global kill switches and quotas before claiming an intent. It did not provide a structured operational snapshot, threshold alert evaluation, or actor attribution for control changes. Operators could enforce a stop but could not consume a consistent local dashboard payload or audit who changed a control.

## Delivered

`IntentStore` now records control-change events with scope, action, actor, quota/enabled state, and timestamp. It provides a read-only `operational_snapshot()` containing intent counts, configured controls, and recent control events. The new deterministic operations helpers evaluate threshold alerts for failed, retryable, or crash-unknown states and build a sanitized dashboard payload. Existing kill-switch enforcement remains in the transactional claim path, so blocked intents cannot reach tools.

## Defect discovered and corrected

The operational gap was observability and attribution rather than missing enforcement. The fix adds durable control events and a read-only snapshot without weakening the claim boundary. Tests cover tenant kill-switch blocking, actor attribution, alert thresholds, malformed snapshots/rules, and missing control actors.

## Verification

| Check | Result |
|---|---|
| STD-10D operational tests | PASS — 4 tests |
| Existing STD-6 execution tests | PASS — 4 tests |
| Combined focused result | PASS — 8 tests |
| Full Python regression suite | PASS — 176 tests |
| Python compilation | PASS |
| `git diff --check` | PASS |

## Security invariants

Kill switches continue to be checked transactionally before an intent claim. Control updates require a non-empty actor and persist the change. Dashboard output is read-only and contains no payloads or secrets. Malformed snapshots and invalid alert rules fail closed. Alert generation does not authorize execution or automatically alter controls.

## Limitations

This is a local synthetic reference dashboard and alert evaluator. It does not page an external incident system, provide production metrics transport, prove alert delivery, integrate with an IdP, implement approval for emergency controls, or evidence multi-process/region operations. Production deployments require authenticated operator endpoints, immutable control-event forwarding, monitored alert delivery, and a tested break-glass procedure.

## Rollback

Revert the execution-store schema/API additions, operations helper, tests, and evidence artifacts. Existing control rows remain compatible because the new event table is additive.

## Next checkpoint

STD-10E should address deployment packaging and commercial operational boundaries separately; no billing or hosted-service behavior is introduced here.
