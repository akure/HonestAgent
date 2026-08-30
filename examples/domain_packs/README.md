# Synthetic EA-2 Domain Policy Packs

These artifacts are **synthetic examples only** for the EA-2 Healthcare and Recruiting/HR workstream. They do not provide regulatory certification, employment-decision authority, clinical authority, or production authorization. They contain no credentials and are configured for `dry_run` rollout.

## Included packs

| Artifact | Scope | Hard stops |
|---|---|---|
| `healthcare_operations_synthetic_v1.json` | Clinical-support and healthcare operations | No PHI export, diagnosis, treatment, prescription, or clinical-order execution. |
| `recruiting_hr_synthetic_v1.json` | Recruiting workflow assistance | No autonomous rejection, hiring, compensation, promotion, or termination decision. |

## Import workflow

The `signature.value` is an intentionally non-authoritative placeholder so the artifact can be reviewed as source configuration. A deployment must load the artifact into a managed `DomainPolicyRegistry`, which signs the normalized content during import, requires reviewer approval, verifies the signature again, and only then activates the exact tenant/version. Never treat the checked-in placeholder as an authorization to execute.

```python
import json
from honest_agent.domain import DomainPolicyPack, DomainPolicyRegistry

with open("examples/domain_packs/healthcare_operations_synthetic_v1.json") as stream:
    pack = DomainPolicyPack.model_validate(json.load(stream))

registry = DomainPolicyRegistry("/var/lib/honest-agent/domain-packs.json", signing_secret="managed-secret")
registry.import_pack(pack, imported_by="synthetic-reviewer")
registry.approve(pack.tenant_id, pack.pack_id, pack.pack_version, "clinician-reviewer")
registry.activate(pack.tenant_id, pack.pack_id, pack.pack_version, "operations-operator")
```

In a real deployment, the signing secret must come from managed secret storage, not source control. The caller must provide trusted `tenant_id` metadata and evidence; prompt text and retrieved content are not authorization inputs.
