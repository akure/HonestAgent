# Honest Agent — Production Deployment Verification Checklist

| Field | Value |
|---|---|
| Release candidate | `4626d44` |
| Environment | Production-like staging first; production only after all P0 items pass |
| Checklist timestamp | `2026-08-29 07:10:47 UTC` |
| Overall rule | Any `BLOCKED`, `NOT RUN`, or unresolved `PARTIAL` is a stop condition |

## 1. Build and artifact integrity

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Pin the exact source commit and immutable build artifact | Release owner | Image digest, commit, SBOM | `NOT RUN` |
| Reproduce from a clean checkout | Engineering | Reproduction command and output | `NOT RUN` |
| Run the full regression suite in CI | Engineering | CI run URL and 67+ passing tests | `NOT RUN` |
| Run static analysis, formatting, dependency, and secret scans | Security / Engineering | Signed scan reports; zero credential findings | `NOT RUN` |
| Verify configuration is environment-specific and no development defaults are mounted | Platform | Rendered manifest/config review | `NOT RUN` |

## 2. Identity, reviewer, and audit controls

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Integrate the approved identity provider | Security / Platform | OIDC/SAML configuration and test login | `NOT RUN` |
| Enforce reviewer and admin roles with least privilege | Security | Role matrix and 401/403 test output | `NOT RUN` |
| Verify reviewer revocation and token expiry | Security | Revocation/expiry test output | `NOT RUN` |
| Persist reviewer subject, action, timestamp, policy version, and trajectory ID | Runtime | Sample redacted audit record | `NOT RUN` |
| Send audit events to an access-controlled immutable or append-only sink | Platform | Sink configuration and retrieval test | `NOT RUN` |

## 3. Storage, retention, and recovery

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Deploy a transactional production store instead of the pilot file store | Platform | Schema, migration, connection, and deployment evidence | `NOT RUN` |
| Verify compare-and-set resolution under concurrent workers | Runtime / QA | Multi-worker test report | `NOT RUN` |
| Verify restart and failover durability | SRE | Restart/failover drill | `NOT RUN` |
| Configure retention, deletion, and legal-hold policy | Security / Privacy | Approved retention configuration | `NOT RUN` |
| Complete backup and restore drill | SRE | Restore timestamp, data-integrity check, RTO/RPO | `NOT RUN` |

## 4. Executor and side-effect controls

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Route every consequential executor through handoff validation | Runtime | Executor inventory and integration tests | `NOT RUN` |
| Prove missing, expired, altered, wrong-payload, and wrong-trajectory handoffs make zero side-effect calls | QA / Runtime | Test report with side-effect counters | `NOT RUN` |
| Confirm human approval is required for irreversible actions | Product / Security | Policy matrix and approval test | `NOT RUN` |
| Maintain a kill switch and emergency disable path | SRE | Drill evidence and operator permissions | `NOT RUN` |
| Test replay, duplicate, and race behavior | Runtime / QA | Replay and idempotency test report | `NOT RUN` |

## 5. Secrets, networking, and transport

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Inject current secrets from an approved secret manager | Platform | Secret-manager references; no raw values | `NOT RUN` |
| Test current/previous-key rotation and old-key retirement | Platform | Rotation drill and timestamps | `NOT RUN` |
| Enforce TLS and certificate validation for all provider/executor links | Platform | TLS configuration and test | `NOT RUN` |
| Enforce egress allowlists and block private/link-local metadata targets | Security / Network | Firewall, DNS, proxy, and SSRF test evidence | `NOT RUN` |
| Test DNS rebinding and resolver behavior | Security | Controlled security test report | `NOT RUN` |
| Verify no secrets or sensitive payloads appear in logs, traces, metrics, or errors | Security / Privacy | Redacted sample scan | `NOT RUN` |

## 6. Provider and reliability controls

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Run approved live provider fault matrix | SRE | Timeout, HTTP, malformed, disagreement, retry, cancel results | `NOT RUN` |
| Record latency p50/p95/p99 by provider and verifier tier | SRE | Time-bounded metrics export | `NOT RUN` |
| Set timeout, retry, circuit-breaker, and concurrency budgets | SRE | Config and load-test report | `NOT RUN` |
| Verify provider failure fails closed and does not execute tools | Runtime | Failure-path test output | `NOT RUN` |
| Configure alerting for latency, provider failures, disagreement, pauses, and executor blocks | SRE | Alert rules and notification test | `NOT RUN` |

## 7. Customer policy governance

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Import policy through a validated customer-controlled workflow | Product / Security | Import record and schema validation | `NOT RUN` |
| Run simulation review before activation | Product / Customer | Simulation output and approval record | `NOT RUN` |
| Require authorized approval and record the approver | Security | Approval audit evidence | `NOT RUN` |
| Test activation and rollback in production-like environment | Release owner | Rollback drill and time-to-recover | `NOT RUN` |
| Verify policy version is present in decisions and handoffs | Runtime | Sample decision and handoff evidence | `NOT RUN` |

## 8. Observability and incident response

| Check | Owner | Evidence required | Status |
|---|---|---|---|
| Define dashboards for safety, provider, executor, storage, and auth signals | SRE | Dashboard links and owner mapping | `NOT RUN` |
| Test alerts and on-call escalation | SRE | Notification drill | `NOT RUN` |
| Publish incident response and customer communication runbooks | Operations | Approved runbook links | `NOT RUN` |
| Test rollback to the last known-good artifact | Release owner | Rollback drill | `NOT RUN` |
| Define post-launch review cadence and success/stop metrics | Product / SRE | Signed operating plan | `NOT RUN` |

## 9. Final decision record

| Decision | Requirement |
|---|---|
| `GO` | All mandatory rows are `PASS`; owners accept residual risk; live provider and platform evidence is attached |
| `CONDITIONAL PILOT` | Only explicitly scoped pilot rows pass; side effects are simulated or allowlisted; human approval and stop controls are active |
| `NO-GO` | Any mandatory row is `BLOCKED`, `NOT RUN`, or unresolved `PARTIAL`; or executor bypass, credential exposure, unsafe networking, or untested production behavior remains |

**Current recommended decision for commit `4626d44`: `CONDITIONAL PILOT` at most; `NO-GO` for unrestricted production.**
