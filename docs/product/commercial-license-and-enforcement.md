# HonestAgent Commercial Licensing and Technical Enforcement

**Status:** Business and engineering draft for legal, security, and pricing review.  
**Related license:** [`LICENSE-SUSTAINABLE-USE-DRAFT.md`](../../LICENSE-SUSTAINABLE-USE-DRAFT.md)

## 1. Recommended distribution model

Use a **source-available sustainable-use license** for internal evaluation, internal business use, consulting, implementation, training, and support. Require a separate Commercial Enterprise License for hosted HonestAgent, customer-facing safety decisions, multi-tenant operation, white-labeling, resale, OEM embedding, or a competing offering.

The license creates legal boundaries. Technical controls make those boundaries easier to operate, measure, and enforce, but they cannot guarantee that a recipient with source access will be unable to copy or modify the Software. The strongest technical control is to keep the enforcement engine on infrastructure we operate and expose only an authenticated API or SDK client.

## 2. Technical enforcement mechanisms

### 2.1 Hosted control plane — strongest control

Operate the policy engine, provider adapters, audit service, entitlement service, and decision API on HonestAgent infrastructure. Give the customer an API client or thin integration library rather than the core source.

Enforce:

- Tenant-scoped authentication and authorization.
- Subscription status and contract end date at the API gateway.
- Request, environment, workflow, and volume entitlements.
- Rate limits and abuse detection.
- Provider and region allowlists.
- Central policy and release versioning.
- Central audit retention and export.
- Immediate suspension or downgrade when a contract ends or a security incident occurs.

This provides meaningful usage visibility because every decision request reaches the service. It does not suit customers that require fully disconnected private deployment unless a separate enterprise option is offered.

### 2.2 Signed private deployment — medium control

For regulated customers, distribute a signed OCI image or package from a private registry. Bind the release manifest to a customer entitlement and approved environment.

Use:

- Image signing and verification, for example Sigstore/Cosign or an equivalent enterprise signing system.
- Immutable image digest recorded in the contract and deployment manifest.
- Private registry authentication and pull audit logs.
- Customer-specific license entitlement containing customer ID, environment IDs, enabled modules, issue time, expiry, and maximum instances.
- Runtime verification of a signed entitlement where network access is acceptable.
- Offline signed entitlement with a short renewal window where the customer requires disconnected operation.
- Signed SBOM and provenance attached to every release.
- Support and security updates only for registered, approved release digests.

A customer with administrative control of the host may still copy or modify the image. Treat image signing as release authenticity and support control, not unbreakable DRM.

### 2.3 License entitlement service

Maintain a small entitlement service that answers whether a deployment is authorized for a defined contract. The entitlement should be signed by the Licensor and contain no customer secret.

Suggested claims:

```json
{
  "license_id": "ha-ent-000123",
  "customer_id": "customer-uuid",
  "deployment_ids": ["pilot-staging-01"],
  "modules": ["guard", "policy", "audit"],
  "max_environments": 1,
  "max_monthly_decisions": 100000,
  "valid_from": "2026-09-01T00:00:00Z",
  "valid_until": "2026-09-30T23:59:59Z",
  "side_effect_mode": "simulated",
  "features": {"sso": false, "multi_tenant": false},
  "issuer": "honestagent",
  "signature": "<detached-signature>"
}
```

Never put provider keys, reviewer secrets, or signing private keys in the entitlement. Store them in the customer’s secret manager or the hosted control plane.

### 2.4 Module separation and open evaluation edition

Keep the public evaluation surface deliberately narrow. Separate proprietary modules such as hosted orchestration, enterprise identity, multi-tenant controls, managed audit, billing, advanced policy governance, and operational dashboards from the evaluation package.

This is an organizational and packaging control, not a substitute for a license. Do not falsely describe a limited edition as security-equivalent to the enterprise deployment.

### 2.5 Telemetry and metering — opt-in and disclosed

For hosted service usage, meter requests at the service boundary. For private deployments, collect only contractually permitted operational telemetry, such as signed release digest, entitlement ID, environment ID, decision counts, error class, and version. Do not collect customer payloads or secrets by default.

Provide:

- A documented telemetry schema.
- Disablement or offline mode where contractually required.
- Data-retention limits.
- Customer access to usage records.
- A privacy and data-processing agreement where applicable.

Telemetry must not be represented as a guarantee that unauthorized source use will be detected.

### 2.6 Operational and contractual controls

Combine technical controls with:

- Private source repository and role-based access.
- Contributor and customer confidentiality agreements.
- Commercial license IDs in orders and deployment records.
- Customer-specific support channels.
- Audit rights limited by contract and applicable law.
- Notice-and-cure process for license breaches.
- Termination, deletion, and credential-rotation procedures.
- Trademark and marketing approval rules.
- Source escrow only for separately priced enterprise arrangements.

## 3. Commercial Enterprise License tiers

Prices below are starting hypotheses for discovery, not binding offers. Each tier should be sold with a signed order form and license schedule that identifies the legal customer, permitted environments, modules, term, users, decision allowance, support, and prohibited redistribution.

| Tier | Indicative price | Deployment | Rights | Included controls |
|---|---:|---|---|---|
| Evaluation | Free or 30-day time-limited | Customer laptop or sandbox | Internal evaluation only; no production, resale, client delivery, or hosted access | Synthetic data, basic examples, community-style documentation; no SLA |
| Team | $1,500/month | Hosted service or one approved self-hosted environment | One internal team and one company; no customer-facing service or resale | Guard API, basic policy configuration, reviewer workflow, usage metering, business-hours support |
| Business | $5,000–$10,000/month | Hosted or approved private deployment | Multiple internal teams and agreed environments; no white-labeling or OEM | SSO/RBAC, durable audit, policy versioning, environment separation, provider configuration, SLA, quarterly control review |
| Enterprise Private | $75,000–$200,000 ARR starting range plus implementation | Signed private image in customer-controlled environment | Named legal entity, named environments, private deployment, custom integration; no redistribution | Dedicated support, security review, image signing, SBOM/provenance, release channel, incident coordination, data-residency options |
| OEM / Embedded | Custom annual agreement, typically $150,000+ ARR | Embedded in customer product or managed platform | Explicit customer-facing, embedding, redistribution, or OEM rights | Commercial integration rights, entitlement service, architecture review, branding terms, audit/reporting, negotiated support |
| Managed Service Provider | Custom annual agreement plus usage | Provider operates service for its clients | Explicit multi-tenant hosting, resale, and client access rights | Tenant controls, metering, support escalation, security commitments, abuse controls, revenue/usage reporting |
| Source Access / Escrow | Custom premium fee and negotiated minimum commitment | Source escrow or restricted source repository | Narrow source inspection, modification, or continuity rights only if expressly listed | Segregated access, audit logs, confidentiality, no redistribution, no competing product, release and deletion controls |

Implementation, migration, training, policy taxonomy, threat modeling, benchmark design, and custom integrations should be priced separately. Third-party model, hosting, storage, identity, and data-processing costs should be passed through or listed as exclusions.

## 4. Entitlement dimensions to price and record

Do not price only by raw token volume. Record the dimensions that create operational and legal scope:

| Dimension | Example entitlement |
|---|---|
| Legal customer | One named company; affiliates excluded unless listed |
| Deployment | Hosted tenant, staging, production, or private cluster |
| Environments | One, three, or unlimited contracted environments |
| Workflows | One named workflow or organization-wide use |
| Decisions | Monthly decision allowance and overage policy |
| Users/reviewers | Named or maximum active reviewer count |
| Modules | Guard, policy, audit, SSO, dashboards, provider adapters |
| Data region | Approved hosting region or customer-controlled storage |
| Side effects | Simulated, explicit allowlist, or production-enabled after acceptance |
| Term | Evaluation window, annual term, renewal, and grace period |
| Support | Business hours, 24×7 response, or dedicated support |
| Rights | Internal use, hosted service, embedding, OEM, resale, source access |

## 5. Example commercial offers

### Control-readiness pilot — $15,000 fixed

One workflow, 14 calendar days, one staging environment, simulated side effects, action taxonomy, integration, baseline-versus-guard benchmark, reviewer procedure, redacted evidence report, and closeout meeting. Payment could be 50% at signature and 50% at report delivery. This offer grants only the named pilot rights; it does not grant unrestricted production, redistribution, source ownership, or resale rights.

### Business annual subscription — $60,000 to $120,000 annually

Multiple internal teams, hosted or approved private deployment, SSO/RBAC, durable audit, policy lifecycle, provider configuration, support, and quarterly control review. Implementation and third-party costs are separate. The order form should define environments, decision allowance, retention, SLA, and renewal.

### OEM agreement

A SaaS provider that wants to expose HonestAgent-powered safety decisions to its own customers needs an OEM or embedded agreement. Price should reflect customer count, decision volume, modules, support, data processing, branding, audit obligations, and the value of granting customer-facing rights. Do not grant this right through a standard Team or Business subscription.

## 6. Limits of technical enforcement

Technical mechanisms can authenticate approved deployments, meter hosted requests, sign releases, restrict support, and make unauthorized use more visible. They cannot reliably prevent an administrator from copying source code, patching a private image, removing a client-side entitlement check, or operating an offline fork. The enforceable boundary therefore remains the written license and commercial agreement.

## References

[1]: https://docs.n8n.io/privacy-and-security/sustainable-use-license "n8n Sustainable Use License documentation"
[2]: https://github.com/n8n-io/n8n/blob/master/LICENSE.md "n8n Sustainable Use License text"
