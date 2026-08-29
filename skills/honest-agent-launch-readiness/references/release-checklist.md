# Conservative Production Release Checklist

Use one row per control. Require a concrete artifact or deployment owner before marking `PASS`.

| Control | Status | Evidence / command | Owner | Blocker if absent |
|---|---|---|---|---|
| Full regression suite passes | `NOT RUN` | Test command and output | Engineering | Yes |
| Reviewer authentication and authorization | `NOT RUN` | 401/403/expiry/attribution tests | Security / Platform | Yes |
| Durable transactional checkpoint store | `NOT RUN` | Restart/concurrency/CAS tests | Platform | Yes |
| Executor validates handoff immediately before side effect | `NOT RUN` | Zero-side-effect invalid-handoff tests | Runtime | Yes |
| Managed secrets injected; no development defaults | `NOT RUN` | Deployment config and secret scan | Platform / Security | Yes |
| Secret rotation runbook tested | `NOT RUN` | Current/previous-key overlap evidence | Platform | Yes |
| Provider fault matrix and production latency SLOs | `NOT RUN` | Timeout/malformed/disagreement/retry/cancel and live p50/p95/p99 | SRE | Yes |
| Customer policy import/simulation/approval/rollback | `NOT RUN` | Policy lifecycle evidence | Product / Security | Yes |
| SSRF and egress controls | `NOT RUN` | URL, DNS, network policy evidence | Security | Yes |
| Payload redaction and retention | `NOT RUN` | Log samples, retention config, scan | Security / Privacy | Yes |
| TLS, container, dependency, and host hardening | `NOT RUN` | Deployment security review | Platform | Yes |
| Backups, restore, monitoring, and incident response | `NOT RUN` | Restore drill and alert/runbook links | SRE | Yes |
| Human approval and pilot scope | `NOT RUN` | Signed operating scope and reviewer roster | Product / Customer | Yes |
| Rollback plan and tested release artifact | `NOT RUN` | Rollback drill and immutable artifact | Release owner | Yes |

## Decision rule

Set the overall decision to **NO-GO** when any mandatory row is `BLOCKED`, `NOT RUN`, or `PARTIAL` without an explicit risk acceptance from the accountable owner. Unit tests alone do not establish production readiness for deployment-dependent controls.
