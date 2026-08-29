# Change Log — launch-readiness audit

| Field | Value |
|---|---|
| Date | `2026-08-29` |
| Role | Staff Engineer + QA + Security Reviewer |
| Finding | `/v1/guard` did not enforce `max_payload_bytes` |
| Root cause | Size checks existed on `/v1/execute` and `/v1/chat/completions`, but not on the guard endpoint |
| Fix | Added bounded Content-Length middleware returning HTTP 413 for oversized requests |
| Regression | `tests/test_core.py::test_guard_rejects_oversized_payload` |
| Status | Fixed and verified |

## Evidence

The full upgraded-dependency suite passes with 81 tests. Intentional smoke checks produce clear 422 responses for empty and malformed JSON, 413 for a valid oversized guard request, and successful completion for 16 concurrent requests. Targeted auth, executor, provider, storage, security, and durability tests pass. Repository secret scans found no candidate credentials, environment files, or sensitive logger calls.

The audit did not add product features. Refresh-mid-action is not applicable because this repository exposes HTTP, MCP stdio, and Python SDK surfaces rather than a browser UI; equivalent interrupted-request and durable-checkpoint behavior is covered by storage and executor tests.
