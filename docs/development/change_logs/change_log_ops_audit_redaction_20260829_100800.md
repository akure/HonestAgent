# Change Log — ops event-log redaction hardening

| Field | Value |
|---|---|
| Change ID | `OPS-001` |
| Date | `2026-08-29` |
| Scope | `honest_agent.ops.pmf.PMFEventLog` |
| Status | Fixed and verified |

## Finding

`PMFEventLog.append()` persisted the caller-supplied `PMFEvent.value` without applying the redaction helper used by control-readiness reports. That contradicted the documented privacy boundary: pilot instrumentation must not export credentials or raw sensitive fields by default.

## Root cause

The PMF event model accepted an arbitrary JSON object and the append path serialized it directly. The existing tests covered round-trip behavior but did not include sensitive nested values.

## Fix

`PMFEventLog.append()` now creates a sanitized copy of the event before JSONL serialization. The existing recursive sanitizer redacts recognized sensitive keys in nested dictionaries and lists while preserving non-sensitive event metrics.

## Regression evidence

- Added `test_pmf_event_log_redacts_sensitive_values_before_persisting`.
- Verified nested `authorization` and `api_key` values are replaced with `[REDACTED]` in the persisted JSONL output.
- Full regression suite passes after the fix.

## Limitations

This is application-level field redaction, not a guarantee that arbitrary sensitive data cannot be encoded under an unrecognized key or embedded in free text. Operators must minimize event values, restrict file permissions, define retention, and use an immutable or access-controlled production sink before a real pilot.
