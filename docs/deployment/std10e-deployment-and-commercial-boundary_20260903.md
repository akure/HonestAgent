# STD-10E Deployment and Commercial Boundary

## Purpose

STD-10E defines a machine-checkable deployment boundary for HonestAgent. It does not implement billing, license enforcement, hosted-service behavior, or safety certification. The protocol remains `honestagent.control.v1`; the reference kernel remains separable from enterprise services.

## Deployment manifest

The validator is credential-free and does not contact a provider or deployment platform. Development and test environments may use the minimum manifest:

```json
{
  "environment": "development",
  "commercial_mode": "source-available"
}
```

Managed staging and production environments must declare an immutable image digest, SBOM reference, audit sink, operator-authentication reference, TLS enforcement, and managed-secrets configuration. Side effects must be `simulated` or `allowlisted`; unrestricted side effects are rejected.

```json
{
  "environment": "production",
  "commercial_mode": "private-deployment",
  "image_digest": "sha256:<64 lowercase hexadecimal characters>",
  "sbom_reference": "sbom://release-identifier",
  "audit_sink": "immutable://audit-target",
  "operator_auth": "oidc://operator-provider",
  "tls_required": true,
  "managed_secrets": true,
  "side_effect_mode": "simulated"
}
```

Validate with:

```python
from honest_agent.ops.deployment import validate_deployment_manifest
validated = validate_deployment_manifest(manifest)
```

## Product boundary

| Layer | Included boundary | Not implied |
|---|---|---|
| Protocol | `honestagent.control.v1` schemas and semantics | Standardization, certification, or universal compatibility |
| Reference kernel | Fail-closed policy, guard, handoff, execution, and audit controls | Production authorization |
| Source-available mode | Local reference implementation and interoperability surface under the repository license | Unrestricted commercial rights |
| Private deployment | Customer-operated deployment with separately agreed enterprise services | Managed hosting or billing enforcement by the code |
| Hosted/OEM mode | Commercially contracted operational service or embedded distribution | Safety certification or regulatory approval |

The validator explicitly reports `billing_enforcement: false` and `safety_certification: false`. Commercial rights are governed by the applicable license or contract, not by hidden runtime telemetry.

## Security and evidence boundary

A passing manifest proves only that required configuration declarations are present and structurally safe. It does not prove that the declared audit sink is immutable, the IdP is correctly configured, the SBOM is complete, secrets are properly held, or operators can respond to alerts. Those require deployment-target evidence, accountable ownership, and rollback drills.

## Rollback

Disable the validator at the packaging boundary only for development/test fixtures. Do not bypass it for managed staging or production; correct the manifest or return the deployment to a non-managed environment.
