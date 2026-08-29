# Change Log — B-1 provider evidence runner

| Field | Value |
|---|---|
| Change ID | `B-1` |
| Feature | `Target-environment provider evidence runner` |
| Timestamp UTC | `2026-08-29 07:17:00` |
| Status | `implementation complete; blocker remains NOT MEASURED` |

## Problem

The final release review identified that the provider fault harness was deterministic and offline, but live approved-provider latency and fault evidence had not been collected. Without credentials and an approved endpoint, a live result must not be inferred or fabricated.

## Change

Added `scripts/run_provider_evidence.py`. The runner reads endpoint, API key, and model only from environment variables, never prints or stores the secret, runs approved synthetic requests through the existing observed/resilient provider boundary, records typed outcomes and latency metrics, and writes a JSON artifact. When required inputs are absent, it writes an explicit `NOT_MEASURED` result and exits without making a network call.

## Evidence

The executed run produced `test_reports/provider_live_evidence_20260829_071700.json` with status `NOT_MEASURED` because no approved live provider endpoint, API key, and model were available in the sandbox. The full suite passed with 68 tests after adding the runner.

## Decision

The runner is **KEPT**. B-1 is **not closed**. Live provider evidence remains a release blocker and requires approved deployment credentials and endpoint access supplied through the deployment environment.

## Safety invariants

| Invariant | Result |
|---|---|
| No live request without explicit endpoint and credentials | `PASS` |
| No secret printed or stored in evidence output | `PASS` |
| Synthetic evidence cannot be mislabeled as live evidence | `PASS` |
| Provider failures remain typed and fail closed | `PASS` |
| Existing regression behavior preserved | `PASS` |
