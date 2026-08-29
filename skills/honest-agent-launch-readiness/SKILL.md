---
name: honest-agent-launch-readiness
description: Sequential launch-readiness engineering for safety-critical AI agent gateways. Use when taking an agent runtime from MVP or pilot readiness through authenticated review, durable state, executor enforcement, managed secrets, provider testing, customer policy governance, security hardening, and a conservative go/no-go release review.
---

# Honest Agent Launch Readiness

Use this skill to move a safety gateway through controlled production gates without conflating tested application behavior with deployment evidence. Work **one sprint at a time**. Never begin the next sprint until the current sprint has passed its tests, published its trace and changelog, and been committed and pushed.

## Operating cycle

1. Read the repository roadmap, trace workflow, current tests, and project instructions.
2. Confirm the current gate and define one narrow sprint outcome.
3. Implement the smallest deterministic control that closes the gate. Keep model judgment outside consequential authorization and execution.
4. Add focused regression tests before claiming completion. Preserve fail-closed behavior and no-side-effect core boundaries.
5. Run the full test suite and formatting/static checks. Record only measured results.
6. Write `docs/development/change_logs/change_log_{feature}_{YYYYMMDD_HHMMSS}.md` and `docs/development/sprint_traces/sprint_{gate}_{YYYYMMDD_HHMMSS}.md`.
7. Commit with a focused message and push to `main`. Verify the remote head and clean working tree.
8. Report the commit, evidence, limitations, and next staged gate. Do not start the next sprint without explicit user direction unless the user has already authorized the complete sequence.

## Gate sequence

| Gate | Required control | Minimum evidence |
|---|---|---|
| LR-1 | Authenticated reviewer identity, role authorization, expiry, and audit attribution | 401/403, expiry, spoofing, and attribution tests |
| LR-2 | Durable multi-process state and compare-and-set resolution | Restart, contention, single-winner, and retention tests |
| LR-3 | Executor-enforced request-bound handoff | Invalid, expired, mismatched, and missing handoff tests with zero side effects |
| LR-4 | Managed secret injection and rotation | Missing/weak secret rejection, current/previous-key overlap, and redaction tests |
| LR-5 | Provider fault matrix and latency instrumentation | Timeout, malformed output, disagreement, retry, cancellation, and measured metrics |
| LR-6 | Customer policy import, simulation, approval, activation, and rollback | Validation, no-activation simulation, approval gate, restart, and rollback tests |
| LR-7 | SSRF, payload redaction, request limits, and deployment hardening | Private-target, credential-URL, log-redaction, payload-limit, and configuration tests |
| Final | Integrated validation and conservative launch decision | Full suite, evidence inventory, deployment checklist, and explicit blockers |

## Mandatory design rules

- Make policy classification, checkpoint resolution, handoff validation, authorization, and executor blocking deterministic.
- Require a human approval checkpoint before consequential or irreversible execution.
- Fail closed on missing context, invalid provider output, provider disagreement, missing credentials, invalid handoffs, and unsafe deployment configuration.
- Keep the core decision engine free of external side effects. Put network calls and execution behind explicit boundaries.
- Redact secrets and sensitive fields before logs, reports, traces, or error responses. Never commit credentials or private data.
- Treat file-backed controls as pilot/single-host evidence unless concurrency and deployment requirements prove otherwise.
- Distinguish `PASS`, `PARTIAL`, `BLOCKED`, and `NOT MEASURED`; do not infer production readiness from unit tests alone.

## Evidence discipline

Every changelog entry must contain the failure mode, what was tried, measured evidence from the same test method, the decision, safety invariants, known limitations, and the next action. Include removed or revised experiments rather than silently deleting them. Use exact test counts from command output.

Every sprint trace must contain the objective, baseline risk, implementation, verification matrix, gate decision, commit placeholder before commit, and next sprint. Replace the placeholder after the commit if the trace is edited.

## Final go/no-go checklist

Use `references/release-checklist.md` and mark each item with evidence, owner, and status. The final decision is **NO-GO** if any mandatory control is missing, deployment evidence is absent, credentials are not managed, the executor can be bypassed, or a security review has unresolved blockers. A pilot approval must explicitly limit scope, side effects, customer data, and environment.

## Reusable artifact paths

- Changelog pattern: `docs/development/change_logs/change_log_{feature}_{timestamp}.md`
- Sprint trace pattern: `docs/development/sprint_traces/sprint_{gate}_{timestamp}.md`
- Final release report: `docs/release/launch-readiness-release-report_{timestamp}.md`
- Deployment checklist: `docs/release/production-deployment-verification-checklist_{timestamp}.md`
- Optional structured evidence: `test_reports/launch_readiness_validation_{timestamp}.json`
