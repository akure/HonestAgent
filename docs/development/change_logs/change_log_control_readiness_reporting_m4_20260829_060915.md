# Change Log — control-readiness reporting and pilot tooling

| Field | Value |
|---|---|
| Change ID | `HA-M4-001` |
| Change type | `feature` and pilot tooling |
| Milestone / sprint | `M4 / Sprint 5` |
| Timestamp UTC | `2026-08-29 06:09:15` |
| Related tasks | `HA-013`, `HA-016`, `HA-017` |
| Related commit | `{filled after commit}` |

## Problem

A customer pilot needs more than raw JSON trajectories. Operators need a repeatable control-readiness artifact showing the evaluation scope, interception rate, safe-action availability, review routing, latency, limitations, and recommendation without exporting secrets or requiring a builder to interpret results.

## Change

Added `honest_agent.ops.control_report.build_control_readiness_report()` and a reproducible CLI under `scripts/generate_control_report.py`. The report normalizes benchmark metrics, preserves the fixture scope, states limitations, provides a staging-pilot recommendation, and omits unrecognized sensitive fields. The M4 test also verifies the report boundary.

## Files changed

| File | Role | Behavior impact |
|---|---|---|
| `honest_agent/ops/control_report.py` | Pilot tooling | Generates sanitized, customer-readable evidence. |
| `scripts/generate_control_report.py` | CLI | Reproduces report generation from JSON artifacts. |
| `tests/test_m4_reporting.py` | Tests | Covers metrics, omissions, and limitations. |
| `docs/integrations/examples/` | Examples | Reserved for clean-checkout pilot examples. |

## Validation

| Command or test | Result | Evidence |
|---|---|---|
| `python3 -m pytest -q` | `PASS` | 29 tests passed. |
| Report fixture | `PASS` | Metrics preserved and unknown secret fields omitted. |

## Failure found during implementation

The first report test assumed every input field would be copied into the export. That would have enlarged the data-leak surface. The implementation intentionally exports a fixed schema, and the test was corrected to assert that unrecognized secret fields are omitted.

## Risk and limitations

The report is a deterministic evidence artifact, not a compliance certification. It does not prove production safety, and it does not yet include customer-specific policy simulation, retention controls, or live provider measurements.

## Rollback or mitigation

Do not treat the report as an authorization artifact. Keep raw trajectories access-controlled and publish only sanitized reports to customer-facing channels.

## Next action

Proceed to M5: add policy dry-run simulation, stable PMF event definitions, and a pilot validation workflow.
