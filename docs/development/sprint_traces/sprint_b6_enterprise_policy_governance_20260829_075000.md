# Sprint Trace — B-6 enterprise policy governance

| Field | Value |
|---|---|
| Sprint | `B-6` |
| Status | `partial — single-host governance boundary complete; enterprise deployment evidence NOT MEASURED` |
| Timestamp UTC | `2026-08-29 07:50:00` |
| Commit | `{filled after commit}` |

## Implementation

Policy records now carry an HMAC signature over version and rules, and signatures are verified before loading or activation. Registries support configurable approval quorum and an optional mandatory simulation gate. Simulation runs persist a timestamp and row count as activation evidence. Existing explicit rollback remains routed through the same approval and signature checks.

## Verification

The full regression suite passes with 76 tests. New cases cover two-person quorum, mandatory simulation before activation, and rejection of a modified persisted policy record.

## Gate decision

B-6 remains `PARTIAL` for unrestricted production. The code proves the governance controls in a single-host file-backed registry; customer IAM integration, enterprise approval authority, signed key lifecycle, production-like rollback drill, and audit review still require deployment evidence.
