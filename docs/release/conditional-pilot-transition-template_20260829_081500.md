# HonestAgent — NO-GO to CONDITIONAL PILOT Transition Template

**Purpose:** Complete this template in the target staging or pilot environment. Empty fields are not evidence. `PASS` must link to a reproducible artifact, run identifier, or controlled drill record.

## 1. Pilot decision record

| Field | Required value |
|---|---|
| Release commit | `1bcb080` or approved descendant |
| Environment | `<isolated staging / named pilot environment>` |
| Customer/workflow scope | `<one named workflow and customer>` |
| Pilot start/end | `<UTC timestamps>` |
| Release owner | `<name and role>` |
| Security owner | `<name and role>` |
| Platform owner | `<name and role>` |
| Side-effect mode | `SIMULATED` or explicit allowlist |
| Human approval required | `true` |
| Kill switch tested | `true` |
| Residual-risk decision | `ACCEPTED FOR PILOT ONLY` |

## 2. Required environment configuration

Use a secret manager or platform secret references. Do not commit values to this file, source control, logs, or evidence artifacts.

```yaml
environment: staging
release_commit: "<immutable commit SHA>"
side_effect_mode: simulated
allowlisted_executor_ids: []
require_reviewer_auth: true
reviewer_idp_issuer: "<approved OIDC issuer>"
reviewer_audience: "<pilot audience>"
reviewer_roles:
  - reviewer
  - admin
reviewer_token_ttl_seconds: 900
reviewer_revocation_source: "<managed roster or IdP group>"
require_policy_simulation: true
policy_approval_quorum: 2
policy_signing_key_ref: "<secret-manager://...>"
handoff_secret_ref: "<secret-manager://...>"
checkpoint_backend: sqlite
checkpoint_database_ref: "<managed or approved durable volume>"
checkpoint_retention_seconds: 2592000
backup_location: "<access-controlled backup target>"
provider_endpoint: "<approved HTTPS endpoint>"
provider_api_key_ref: "<secret-manager://...>"
provider_model: "<approved model>"
provider_timeout_seconds: 5
provider_max_retries: 2
require_tls: true
allow_private_upstream: false
max_payload_bytes: 1000000
egress_allowlist:
  - "<approved provider hostname>"
audit_sink: "<immutable or append-only sink reference>"
alert_routes:
  - "<on-call route>"
```

## 3. Evidence acceptance matrix

| Control | Required artifact | Acceptance test | Owner | Status |
|---|---|---|---|---|
| Build integrity | Immutable image digest, commit, SBOM | Digest matches source commit; SBOM retained | Release | `NOT MEASURED` |
| Dependency security | `pip-audit`/Dependabot output and remediation diff | No unresolved production-runtime vulnerability; pytest patched | Security | `NOT MEASURED` |
| Provider reliability | Redacted B-1 JSON report | Timeout, malformed, disagreement, retry, cancel, p50/p95/p99, zero unsafe execution | SRE | `NOT MEASURED` |
| Storage durability | Migration, backup/restore, failover records | Restore integrity and stated RTO/RPO pass | Platform | `NOT MEASURED` |
| Executor inventory | Adapter inventory and bypass tests | Invalid, replayed, mismatched handoffs produce zero side effects | Runtime | `PASS/PARTIAL` |
| Identity | IdP login, role matrix, expiry/revocation drill | 401/403 behavior and revoked identity denial | Security | `NOT MEASURED` |
| Audit | Redacted sample and sink retrieval | Subject, action, timestamp, policy version, trajectory ID present; chain verifies | Security | `NOT MEASURED` |
| Policy governance | Signed import, simulation, quorum, activation, rollback records | Unsigned/unapproved/unsimulated policy cannot activate | Product/Security | `NOT MEASURED` |
| Network security | Egress rules, DNS rebinding, TLS validation | Only allowlisted HTTPS destinations; private/link-local targets blocked | Platform | `NOT MEASURED` |
| Secrets | Secret-manager references and scan output | No raw values in source, logs, traces, metrics, or artifacts | Platform | `NOT MEASURED` |
| Observability | Dashboard, alert, escalation, stop drill | Alerts fire and operator can disable pilot | SRE | `NOT MEASURED` |
| Human review | Approval matrix and test trajectory | Irreversible actions pause and require authorized reviewer | Product | `NOT MEASURED` |

## 4. Conditional-pilot stop conditions

The pilot must not start, or must be stopped immediately, if any provider failure can fail open; an executor bypasses handoff validation; a secret appears in evidence; private-network egress is uncontrolled; durable state cannot be restored; identity revocation fails; a required human approval is absent; audit attribution is missing; or the dependency remediation has not been reviewed by Security.

## 5. Evidence packet manifest

```text
artifacts/
  build/
    commit.txt
    image-digest.txt
    sbom.json
  security/
    pip-audit.json
    secret-scan.txt
    tls-egress-dns-report.json
    container-host-review.md
  provider/
    b1-redacted-provider-evidence.json
  storage/
    migration.txt
    backup-restore-drill.md
    failover-drill.md
  identity/
    idp-role-expiry-revocation.md
    redacted-audit-sample.jsonl
  policy/
    signed-import-simulation-approval-rollback.md
  executor/
    executor-inventory.md
    bypass-resistance-test.txt
  operations/
    alert-notification-drill.md
    kill-switch-drill.md
    incident-runbook.md
  decision/
    pilot-approval.md
```

## 6. Decision rule

Run the repository gate with the evidence states for B-1 through B-6. A conditional pilot may be recommended only when every blocker has a recognized state, no stop condition is present, side effects are simulated or allowlisted, human approval is active, and the accountable owners sign the pilot record. This does not produce a production `GO`; unrestricted production still requires every mandatory blocker to be `PASS` and explicit residual-risk acceptance.
