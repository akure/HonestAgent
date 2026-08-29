# HonestAgent — Conditional-Pilot Evidence Sprint Plan

**Current release position:** **NO-GO for unrestricted production**  
**Target transition:** A tightly scoped **CONDITIONAL PILOT**  
**Baseline:** Dependency/security remediation commit `4ad8c3e`

## Operating rule

Each sprint follows the sequence **build or fix → test or drill → attach evidence → commit → review → next sprint**. No sprint may mark deployment-dependent evidence `PASS` from unit tests alone. Side effects remain simulated or explicitly allowlisted until the pilot approval record is signed.

## Sprint sequence

| Sprint | Scope | Primary deliverables | Exit gate |
|---|---|---|---|
| CP-1 | Immutable build and supply chain | Reproducible clean build, image digest, SBOM, pytest/FastAPI/Starlette scan, secret scan | Digest matches commit; clean scan; Security accepts dependency remediation |
| CP-2 | Provider reliability | Approved live endpoint run, timeout/malformed/disagreement/retry/cancellation matrix, p50/p95/p99 report | Zero unsafe execution; thresholds reviewed by SRE; redacted evidence retained |
| CP-3 | Durable storage and recovery | Migration record, CAS concurrency run, restart/failover drill, backup/restore, retention/legal-hold configuration | Integrity verified; RTO/RPO recorded; Platform accepts topology |
| CP-4 | Executor inventory and side-effect safety | Deployed executor inventory, invalid/replay/mismatch tests, duplicate/race results, human approval matrix | Every consequential path is guarded; zero invalid-path side effects |
| CP-5 | Identity and audit operations | Approved IdP login, role/least-privilege matrix, expiry/revocation drill, immutable sink retrieval | Revoked identity denied; audit has subject/action/time/policy/trajectory |
| CP-6 | Policy governance | Customer-controlled import, signed version, simulation, quorum approval, activation, rollback drill | Unsigned/unapproved/unsimulated versions cannot activate; rollback meets target |
| CP-7 | Platform security and operations | Egress/DNS/TLS tests, container/host review, vulnerability/SBOM report, dashboards, alerts, kill-switch and incident drills | No stop condition; alerts and disable path demonstrated |
| CP-8 | Pilot decision and controlled launch | Completed evidence manifest, named scope, allowlist, owner signatures, pilot runbook | B-7 gate returns `CONDITIONAL PILOT`; no unrestricted-production claim |

## Evidence requirements by sprint

### CP-1 — Build and supply chain

Record the exact source commit, immutable image digest, build provenance, SBOM, Python/package versions, `pip-audit` output, and secret-scan output. The current tested package set is FastAPI 0.137.1, Starlette 1.6.0, pytest 9.0.3, Uvicorn 0.34.0, Pydantic 2.10.4, and HTTPX 0.28.1. GitHub Dependabot must be rechecked with security-alert permission because the current integration returned HTTP 403.

### CP-2 — Provider reliability

Use only an approved provider endpoint and deployment secret references. Run the existing B-1 runner and retain a redacted JSON report covering timeout, malformed output, disagreement, bounded retry, cancellation, latency percentiles, and zero unsafe execution. Record provider/model, test window, sample count, thresholds, and operator approval.

### CP-3 — Storage and recovery

Use the approved production-like transactional topology. Attach migration output, schema version, concurrent compare-and-set evidence, restart and failover timestamps, backup location, restore integrity hash, RTO/RPO, retention, deletion, and legal-hold decisions. SQLite single-host evidence is insufficient for an HA claim.

### CP-4 — Executors and human approval

Inventory every callable or external executor, including adapters not directly owned by the repository. For each, demonstrate that missing, expired, altered, wrong-payload, wrong-trajectory, replayed, duplicate, and raced handoffs invoke zero side effects. Attach the irreversible-action policy and a human approval trajectory.

### CP-5 — Identity and audit

Attach approved IdP configuration, role matrix, test login, expiry and revocation evidence, reviewer roster ownership, emergency disable procedure, and a retrieved redacted audit sample. Verify the append-only chain and access controls from the target environment.

### CP-6 — Policy governance

Attach a customer-authorized import record, policy signature verification, simulation output, quorum approvals, activation record, policy version in decisions/handoffs, rollback drill, and audit review. Include signing-key custody and rotation evidence.

### CP-7 — Platform and operations

Attach egress allowlists, DNS-rebinding/resolver results, TLS certificate validation and rotation, container non-root/read-only/drop-capability review, host patch posture, dependency/SBOM report, dashboards, alert notification test, incident runbook, rollback drill, and kill-switch drill.

### CP-8 — Decision and launch

Complete the companion transition template, name one customer and workflow, set side effects to `SIMULATED` or an explicit allowlist, confirm human review, attach owner signatures, and run the deterministic B-7 gate. The output must state **CONDITIONAL PILOT**, not `GO`, unless all mandatory production evidence is independently `PASS` and residual risk is accepted for production.

## Stop conditions

Stop immediately if a provider failure can fail open, an executor bypasses validation, credentials appear in artifacts, private-network egress is uncontrolled, state cannot be restored, identity revocation fails, policy approval is bypassed, audit attribution is missing, the kill switch does not work, or the vulnerability scan returns an unresolved runtime finding.

## Stakeholder approval matrix

| Decision | Required approvers |
|---|---|
| Build artifact accepted | Release owner and Security |
| Provider evidence accepted | SRE and Runtime |
| Storage/recovery accepted | Platform and SRE |
| Executor/human-review accepted | Runtime, Product, and Security |
| Identity/audit accepted | Security and Platform |
| Policy governance accepted | Product and Security |
| Pilot launch accepted | Release owner, Security, Platform, Product, and named customer owner |
