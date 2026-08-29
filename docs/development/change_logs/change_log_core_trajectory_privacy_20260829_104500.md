# Change Log — core trajectory free-text privacy hardening

| Field | Value |
|---|---|
| Change ID | `CORE-001` |
| Date | `2026-08-29` |
| Scope | `honest_agent.core.logger.TrajectoryLogger` |
| Status | Fixed and verified |

## Finding

Trajectory logging already redacted sensitive keys inside tool inputs, but it persisted raw `system_instruction` and `thought` text. Those free-text fields can contain customer content, credentials, prompt-injection text, or other sensitive material.

## Fix

The logger now preserves schema compatibility while writing `[OMITTED]` for non-empty system instructions and thoughts. Tool names and structured tool inputs remain available for audit, with sensitive input keys recursively redacted by the existing security helper.

## Regression evidence

The security regression test now supplies sensitive instruction and thought values and verifies that neither value appears in the persisted trajectory. It also verifies that the existing authorization redaction remains intact. The full repository suite passes after the fix.

## Limitations

This is an application-level privacy boundary. Operators must still minimize context, tool inputs, identifiers, and event values; protect trajectory storage; define retention; and use an access-controlled or immutable production sink. The verifier may still receive request context before logging, so provider transport controls and provider-side data handling remain separate deployment concerns.
