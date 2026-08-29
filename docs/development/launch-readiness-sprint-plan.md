# Honest Agent — Launch-Readiness Sprint Program

## Objective

Move Honest Agent from a controlled pilot-capable MVP to a system that can be evaluated for real consequential execution. The program addresses every open gate in the MVP release review. Each sprint is independently testable, documented, committed, pushed to `main`, and reviewed before the next sprint begins.

This program does **not** authorize production side effects by itself. The final go/no-go review must confirm that the executor, storage, identity, secrets, provider, policy, and deployment controls operate together.

## Operating sequence

For every sprint, follow this sequence:

1. Publish or update the sprint plan and acceptance criteria.
2. Build only the current sprint scope.
3. Record every failure before applying its fix.
4. Run focused tests and the complete regression suite.
5. Create `change_log_{feature_or_fix}_{YYYYMMDD_HHMMSS}.md`.
6. Create `sprint_{milestone}_{sprint}_{YYYYMMDD_HHMMSS}.md`.
7. Create a focused conventional commit.
8. Push the implementation and trace artifacts to `main`.
9. Verify the remote hash and clean working tree.
10. Review the sprint outcome before starting the next one.

## Sprint map

| Sprint | Launch gate | Primary outcome | Depends on | Exit evidence |
|---|---|---|---|---|
| LR-1 | Authenticated reviewer identity | Authenticated reviewer sessions, roles, and attributed decisions | MVP M1/M2 | 401/403/expiry/replay tests and reviewer audit records |
| LR-2 | Multi-process durable storage | Transactional storage interface with compare-and-set, retention, and restart safety | LR-1 | Concurrent resolution tests, restart tests, retention tests |
| LR-3 | Executor enforcement | Executor or gateway validates the handoff before side effects | LR-2 | Payload mutation, token replay, rejection, and simulated side-effect tests |
| LR-4 | Secret management | No development secrets in launch configuration; managed injection and rotation | LR-3 | Startup/config tests, rotation test, secret scan |
| LR-5 | Production provider testing | Provider matrix for timeout, malformed output, disagreement, retry, cancellation, and latency | LR-4 | Provider contract report and latency budget evidence |
| LR-6 | Customer policy onboarding | Import, simulate, review, approve, version, and roll back customer policy | LR-2, LR-3 | Policy lifecycle tests and dry-run diff report |
| LR-7 | Security and deployment hardening | SSRF controls, redaction, deployment profiles, threat-model review | LR-1 through LR-6 | Security test report, hardened container, reviewer sign-off |

## LR-1 — Authenticated reviewer identity

Implement an authentication boundary for webhook and review operations. Support reviewer identity, role authorization, token expiry, and audit attribution. Development mode may use an explicit test adapter, but production configuration must fail closed when authentication is absent.

**Acceptance criteria:** unauthenticated requests return 401; authenticated non-reviewers return 403; expired credentials cannot resolve a checkpoint; every approval or rejection persists reviewer identity and authentication method; tests cover replay and duplicate resolution.

## LR-2 — Transactional multi-process storage

Add a relational or transactional storage adapter behind `CheckpointStore`. Use compare-and-set resolution, unique trajectory IDs, explicit retention, and restart-safe reads. The file store remains a local development adapter and must not be described as multi-process safe.

**Acceptance criteria:** two workers cannot both resolve the same pending checkpoint; state survives process restart; expired records are not executable; retention removes or archives records according to policy; storage failures fail closed.

## LR-3 — Executor-enforced handoff

Create a guarded executor adapter that accepts a tool proposal and handoff token, validates signature, payload hash, trajectory, policy version, expiry, and final decision, then invokes a simulated side effect only after validation. Keep the executor separate from the guard decision engine.

**Acceptance criteria:** valid handoff invokes the simulated executor exactly once; changed payload, changed tool, rejected decision, expired token, and replayed token invoke it zero times; all invalid cases produce structured errors and audit events.

## LR-4 — Managed secrets

Remove development signing defaults from production startup. Add configuration loading from environment or a secret-manager interface, explicit secret version metadata, rotation support, and redacted diagnostics. A missing production secret must prevent startup or disable execution handoffs.

**Acceptance criteria:** secret values never appear in logs, trajectories, reports, or exceptions; old tokens follow a documented rotation policy; production profile rejects the development secret; secret scans pass.

## LR-5 — Provider matrix

Formalize provider contract tests and run them against deterministic fakes plus any approved live provider in a controlled environment. Measure verifier-only, persistence-only, and end-to-end latency separately.

**Acceptance criteria:** timeout, malformed response, disagreement, retry, cancellation, rate limit, and provider-unavailable cases never proceed; each provider has a latency budget; results identify provider, model, environment, fixture count, and cost boundary.

## LR-6 — Customer policy onboarding

Create a policy bundle format with import validation, dry-run diff, reviewer approval, version history, activation, and rollback. A policy change must not silently alter active enforcement without an approval event.

**Acceptance criteria:** invalid bundles are rejected; policy simulation shows added pauses and newly permitted actions; activation is attributable; rollback restores the previous version; every decision references the active policy version.

## LR-7 — Security and deployment hardening

Complete the threat-model review and close deployment risks: upstream URL allowlists, SSRF protections, payload and credential redaction, secure headers, non-root container execution, bounded request sizes, timeouts, rate limiting, and production configuration checks.

**Acceptance criteria:** security tests cover disallowed upstream targets, oversized payloads, secret leakage, invalid handoffs, unauthorized review, and unsafe defaults; Docker health checks pass; the deployment profile contains no development credentials.

## Final go/no-go gate

The system may proceed to a controlled customer staging pilot only when every LR sprint has a published trace and all mandatory gates pass together. The final review must include a complete adversarial replay, a simulated side-effect executor, storage restart and concurrency evidence, authenticated reviewer evidence, provider fault results, active-policy version evidence, secret scan output, and security review sign-off.

A production go decision is prohibited if any verifier, storage, authentication, executor, or secret-management failure can produce an unvalidated side effect.
