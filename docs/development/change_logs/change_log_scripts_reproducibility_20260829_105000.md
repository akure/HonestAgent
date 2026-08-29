# Change Log — script reproducibility hardening

| Field | Value |
|---|---|
| Change ID | `SCRIPTS-001` |
| Date | `2026-08-29` |
| Scope | `scripts/` CLI utilities |
| Status | Fixed and verified |

## Findings

The policy-simulation and control-report CLIs wrote directly to their output paths without creating parent directories. A clean checkout therefore failed when users followed the documented commands with a new `reports/` directory. The documented policy-simulation command also referenced `fixtures/customer_sanitized_requests.json`, but that fixture was absent from the repository.

## Fixes

- Both CLIs now create the output parent directory before serialization.
- Added a committed, sanitized three-request fixture covering a read-only action, an explicitly irreversible action, and an unknown action that must fail closed.
- The provider-evidence runner already created its output parent and already emitted `NOT_MEASURED` without credentials; no change was needed there.

## Verification

- Policy simulation generated output in a previously absent nested directory.
- Control-readiness report generated output in a previously absent nested directory.
- Provider evidence ran with zero iterations and no credentials, produced `NOT_MEASURED`, and made no network call.
- Fixture output confirmed read-only `would_execute=true`, irreversible `would_execute=false`, and unknown `would_execute=false`.
- Script compilation and `git diff --check` passed.

## Limitations

These CLIs still report malformed input through Python/Pydantic exceptions rather than a custom structured error format. That is suitable for a developer-facing CLI but should be wrapped by an operational job runner if customer-facing automation requires stable exit-code taxonomy and redacted error logs.
