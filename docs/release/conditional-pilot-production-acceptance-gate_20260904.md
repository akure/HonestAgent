# Conditional-Pilot Production Acceptance Gate

**Product:** HonestAgent  
**Decision scope:** One named workflow, tenant boundary, tool set, destination set, and pilot window  
**Decision rule:** A conditional pilot is permitted only when every mandatory pilot gate is `PASS`, all non-applicable items are explicitly justified, and the accountable owner signs residual risk. Any executor bypass, credential exposure, unsafe network path, unverifiable audit record, failed kill switch, unresolved critical vulnerability, or failed rollback is an automatic `NO-GO`.

## A. Required sign-off roles

| Role | Required responsibility | Sign-off |
|---|---|---|
| Accountable business owner | Accept pilot scope, value hypothesis, and residual operational risk | Name/date/signature |
| Technical owner | Accept architecture, integration, performance, and rollback readiness | Name/date/signature |
| Security owner | Accept identity, secrets, egress, vulnerability, and audit controls | Name/date/signature |
| SRE/platform owner | Accept deployment, monitoring, alerting, backup, and recovery evidence | Name/date/signature |
| Privacy/compliance owner | Accept data scope, retention, human review, and regulatory boundary | Name/date/signature |
| Release owner | Confirm artifact, evidence completeness, and final decision record | Name/date/signature |

One person may hold multiple roles only when the organization’s separation-of-duties policy explicitly permits it. The policy registry importer, approver, and activator remain separate where configured.

## B. Pilot scope lock

| Gate | Acceptance criterion | Evidence | Status |
|---|---|---|---|
| Scope | Named workflow, tenant(s), tools, destinations, policy version, and start/end time are recorded | Signed pilot record | `NOT RUN` |
| Side effects | Only simulated or explicitly allowlisted effects are enabled | Policy and executor matrix | `NOT RUN` |
| Human approval | Irreversible actions require an authenticated, scoped reviewer | Approval test output | `NOT RUN` |
| Stop authority | Named operator can activate tenant/workflow/tool/global kill switch | Drill record | `NOT RUN` |
| Exit criteria | Success, stop, rollback, and expansion criteria are defined before launch | Approved operating plan | `NOT RUN` |

## C. Supply-chain and deployment gates

| Gate | Acceptance criterion | Evidence | Status |
|---|---|---|---|
| Source | Build starts from an approved immutable commit | Commit and CI record | `NOT RUN` |
| Image | Image is built successfully and referenced by immutable digest | Build log and digest | `NOT RUN` |
| SBOM | SBOM is generated for the exact image digest and retained | SPDX/CycloneDX plus hash | `NOT RUN` |
| Signature | Image digest signature verifies under approved keyless/KMS policy | Cosign/approved verification output | `NOT RUN` |
| Vulnerabilities | Image and dependencies pass the approved severity and exception policy | Timestamped scan reports | `NOT RUN` |
| Registry | Registry access is controlled and pull digest matches signed digest | Registry audit and pull check | `NOT RUN` |
| Deployment | Staging deployment uses the digest, not a mutable tag | Rendered manifest and rollout output | `NOT RUN` |
| Rollback | Known-good artifact rollback succeeds within the agreed recovery objective | Rollback drill | `NOT RUN` |

## D. Identity, secrets, and network gates

| Gate | Acceptance criterion | Evidence | Status |
|---|---|---|---|
| Identity provider | Approved OIDC/SAML provider is integrated | Configuration and login test | `NOT RUN` |
| Least privilege | Reviewer, operator, administrator, and break-glass roles are mapped | Role matrix and 401/403 tests | `NOT RUN` |
| Revocation | Expired, revoked, wrong-tenant, and removed-subject access is rejected | Drill output | `NOT RUN` |
| Secrets | No development defaults; secrets come from approved manager | Rendered config review | `NOT RUN` |
| Rotation | Current/previous key rotation and old-key retirement succeed | Rotation record | `NOT RUN` |
| Transport | TLS and certificate validation are enforced for provider/executor links | TLS test | `NOT RUN` |
| Egress | Egress allowlist blocks private, link-local, metadata, and unauthorized targets | Network/SSRF test | `NOT RUN` |
| Logging | Secret and protected payload scans find no leakage | Redacted log/metric scan | `NOT RUN` |

## E. Runtime safety and data gates

| Gate | Acceptance criterion | Evidence | Status |
|---|---|---|---|
| Executor inventory | Every consequential executor and bypass path is listed | Inventory and owner map | `NOT RUN` |
| Handoff binding | Run, step, attempt, tenant, policy, evidence, destination, and expiry are verified | Negative integration tests | `NOT RUN` |
| Bypass resistance | Altered, missing, stale, replayed, duplicate, wrong-tenant, and wrong-payload handoffs make zero protected side-effect calls | Side-effect counter report | `NOT RUN` |
| Provider failures | Timeout, malformed, unavailable, and disagreement paths fail closed | Fault matrix | `NOT RUN` |
| RAG boundary | Retrieved content cannot grant authority or alter tenant/tool/reviewer scope | Injection and cross-tenant tests | `NOT RUN` |
| Data minimization | Pilot data is synthetic or approved minimal data with classification recorded | Data inventory | `NOT RUN` |
| Retention | Audit and workflow retention, deletion, legal hold, and access rules are approved | Retention configuration | `NOT RUN` |
| Recovery | Backup/restore and restart/failover preserve integrity and safety state | RTO/RPO drill | `NOT RUN` |

## F. Operations and incident-response gates

| Gate | Acceptance criterion | Evidence | Status |
|---|---|---|---|
| Dashboard | Safety, provider, executor, storage, and auth signals are visible to named owners | Dashboard links/screenshots | `NOT RUN` |
| Alerts | Thresholds, severity, routing, and escalation are configured | Alert rule export | `NOT RUN` |
| Notification | At least one alert reaches the on-call route in a drill | Notification record | `NOT RUN` |
| Kill switch | Stop command blocks new claims and is attributable to an authenticated operator | Kill-switch drill | `NOT RUN` |
| Audit retrieval | Control changes and consequential actions are retrievable and integrity-verified | Retrieval report | `NOT RUN` |
| Incident runbook | Provider failure, data concern, unauthorized action, and rollback runbooks are approved | Runbook links | `NOT RUN` |
| Communications | Customer and internal communication templates have owners | Approved templates | `NOT RUN` |

## G. Decision criteria

### Conditional pilot — approve only when all are true

1. Every mandatory gate above is `PASS` or has an approved, documented non-applicability decision.
2. Scope is narrow, time-bounded, and reversible.
3. Side effects are simulated or allowlisted.
4. Human approval is active for irreversible actions.
5. Identity, secrets, audit, monitoring, and kill-switch drills pass.
6. No critical vulnerability, credential exposure, executor bypass, unsafe egress, or unresolved integrity failure exists.
7. The accountable owner signs residual risk and the release owner signs evidence completeness.

### No-go conditions

The decision is `NO-GO` if any required evidence is missing, any tool or target capability is unavailable, any critical vulnerability is unresolved, or any control is asserted only from a mock. It is also `NO-GO` if the team cannot prove rollback, cannot identify every consequential executor, or cannot stop new protected actions.

### Unrestricted production

Unrestricted production requires a separate release decision. Local tests, synthetic benchmarks, stubs, a conditional pilot, or a passing deployment manifest do not satisfy that decision by themselves. Production requires target-like evidence, independent review, accountable residual-risk acceptance, and completion of the organization’s regulatory and privacy obligations.

## H. Final decision record

| Field | Value |
|---|---|
| Pilot name |  |
| Approved commit/image digest |  |
| Policy version |  |
| Environment |  |
| Pilot window |  |
| Decision | `NO-GO` / `CONDITIONAL PILOT` / `GO` |
| Open exceptions |  |
| Expiry/review date |  |
| Accountable owner |  |
| Release owner |  |
| Evidence bundle location |  |
| Final signatures |  |
