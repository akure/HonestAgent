# HonestAgent Domain Policy Pack — EA-1 Schema Proposal

## Review status

**Approved and implemented for EA-1.** This document defines the EA-1 contract and its security boundaries. The runtime implementation is in `honest_agent/domain/policy_pack.py`; domain packs remain an additional restrictive gate and never replace the generic safety kernel.

## Design intent

A domain policy pack is a signed, versioned, tenant-scoped configuration artifact that adapts the generic HonestAgent guard without adding industry conditionals to `HonestGuard`. It describes action classifications, deterministic constraints, data and egress rules, evidence requirements, approval requirements, and rollout safeguards. A pack can make a decision stricter than the generic kernel, but it must never authorize execution by itself.

The runtime should combine the pack with the existing `ActionPolicy` and `PolicyRegistry` as follows:

```text
request
  -> select tenant/domain/policy version
  -> validate request against pack constraints
  -> classify action using generic policy + pack rule
  -> evaluate context/verifier requirements
  -> return PROCEED, PAUSED, REJECTED, or CAP_EXCEEDED
  -> issue a signed handoff only after all required gates pass
```

A missing, malformed, unsigned, expired, unauthorized, ambiguous, or incompatible pack must fail closed. If pack evaluation is unavailable, the guard must not silently fall back to a less restrictive policy.

## Proposed normalized contract

| Field | Required | Purpose | Security boundary |
|---|---:|---|---|
| `schema_version` | Yes | Version of this JSON contract | Unknown major versions reject; minor versions require compatibility rules |
| `pack_id` | Yes | Stable pack identifier | Safe identifier; not a secret |
| `pack_version` | Yes | Immutable pack version | Safe identifier; activation references this exact version |
| `tenant_id` | Yes | Customer/tenant scope | Must be selected by trusted caller metadata, not model text |
| `domain` | Yes | One of the six supported domain labels or an extension label | Descriptive namespace; domain does not change kernel control flow |
| `policy_version` | Yes | Version surfaced in decisions and audit records | Must match the registry version used for handoff signing |
| `status` | Yes | `DRAFT`, `APPROVED`, `ACTIVE`, or `RETIRED` | Runtime accepts only an authorized active version |
| `actions` | Yes | Action rules keyed by stable tool/action name | Unknown actions remain fail closed |
| `data_controls` | Yes | Data classes, minimization, redaction, and egress defaults | Must not be used to weaken core secret redaction |
| `evidence` | Yes | Freshness, provenance, and required evidence signals | Missing/contradictory evidence pauses or rejects |
| `approval` | Yes | Reviewer roles, quorum, and high-impact action rules | Caller identity and reviewer identity are separate |
| `limits` | Yes | Generic numeric, rate, amount, geography, and time limits | Limits are deny-by-default when configured |
| `rollout` | Yes | Dry-run, canary, kill-switch, and stop-condition settings | Production activation requires explicit scope |
| `metadata` | No | Non-authoritative display metadata | Never affects authorization |
| `signature` | Yes for persisted/imported artifacts | Integrity and authenticity envelope | Signature is verified before simulation/activation/use |

## Domain labels

The initial built-in labels are:

- `healthcare`
- `financial_trading`
- `recruiting_hr`
- `forecasting`
- `ecommerce`
- `customer_support`

The label is used for reporting, pack selection, and documentation. It must not cause `HonestGuard` to contain domain-specific `if/elif` authorization logic. New domains can use the same contract only after their action rules and tests are reviewed.

## Action rule model

Each action rule has a stable action name and includes:

- `action_class`: `read_only`, `reversible`, `irreversible`, or `unknown`;
- `requires_review`: whether a reviewer checkpoint is mandatory;
- `prohibited`: an unconditional deny rule;
- `reason_code`: a stable, non-sensitive audit code;
- `required_roles`: allowed reviewer roles when review is required;
- `constraints`: deterministic checks over normalized request metadata and tool arguments;
- `required_evidence`: evidence keys and freshness requirements;
- `idempotency_required`: whether a caller-provided idempotency key is mandatory;
- `max_retries`: a policy ceiling, never an instruction to retry after rejection.

A prohibited action always results in `REJECTED`. A required review results in `PAUSED` unless a previously approved, request-bound reviewer decision is already represented by a valid handoff. A rule cannot set `action_taken` to an execution-success value.

## Generic constraint vocabulary

EA-1 should support a deliberately small vocabulary rather than an unrestricted expression language:

| Constraint | Example | Failure |
|---|---|---|
| `required_fields` | `account_id`, `amount` | Reject |
| `allowed_values` | approved venues or regions | Reject |
| `max_numeric` / `min_numeric` | maximum refund or order quantity | Reject |
| `max_age_seconds` | quote or evidence freshness | Pause or reject according to rule |
| `matches_pattern` | safe identifier format | Reject |
| `required_scope` | tenant, account, patient, ticket | Reject |
| `egress_classes` | permitted destination data classes | Reject |
| `rate_limit` | actions per actor/window | Reject or pause |
| `idempotency_required` | transaction key required | Reject |

The expression language must not support arbitrary Python, shell commands, network calls, model-generated code, or callbacks. Domain-specific checks that cannot be represented safely must use a reviewed deterministic validator plugin with an explicit test contract.

## JSON Schema

The following is the proposed Draft 2020-12 schema. It validates shape and bounded values; semantic checks such as signature verification, tenant authorization, policy conflicts, and constraint evaluation remain runtime responsibilities.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://honestagent.example/schema/domain-policy-pack.ea1.json",
  "title": "HonestAgent Domain Policy Pack",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "pack_id",
    "pack_version",
    "tenant_id",
    "domain",
    "policy_version",
    "status",
    "actions",
    "data_controls",
    "evidence",
    "approval",
    "limits",
    "rollout",
    "signature"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^1\\.[0-9]+$"
    },
    "pack_id": {
      "type": "string",
      "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
    },
    "pack_version": {
      "type": "string",
      "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
    },
    "tenant_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128,
      "pattern": "^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}$"
    },
    "domain": {
      "type": "string",
      "enum": [
        "healthcare",
        "financial_trading",
        "recruiting_hr",
        "forecasting",
        "ecommerce",
        "customer_support"
      ]
    },
    "policy_version": {
      "type": "string",
      "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
    },
    "status": {
      "type": "string",
      "enum": ["DRAFT", "APPROVED", "ACTIVE", "RETIRED"]
    },
    "actions": {
      "type": "object",
      "minProperties": 1,
      "maxProperties": 256,
      "propertyNames": {
        "pattern": "^\\S.{0,127}$"
      },
      "additionalProperties": {
        "$ref": "#/$defs/actionRule"
      }
    },
    "data_controls": {
      "$ref": "#/$defs/dataControls"
    },
    "evidence": {
      "$ref": "#/$defs/evidencePolicy"
    },
    "approval": {
      "$ref": "#/$defs/approvalPolicy"
    },
    "limits": {
      "$ref": "#/$defs/limits"
    },
    "rollout": {
      "$ref": "#/$defs/rolloutPolicy"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": {
        "type": ["string", "number", "boolean"]
      },
      "maxProperties": 32
    },
    "signature": {
      "$ref": "#/$defs/signature"
    }
  },
  "$defs": {
    "actionClass": {
      "type": "string",
      "enum": ["read_only", "reversible", "irreversible", "unknown"]
    },
    "actionRule": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "action_class",
        "requires_review",
        "prohibited",
        "reason_code",
        "constraints",
        "required_evidence",
        "idempotency_required",
        "max_retries"
      ],
      "properties": {
        "action_class": {"$ref": "#/$defs/actionClass"},
        "requires_review": {"type": "boolean"},
        "prohibited": {"type": "boolean"},
        "reason_code": {
          "type": "string",
          "pattern": "^[A-Z][A-Z0-9_.-]{2,63}$"
        },
        "required_roles": {
          "type": "array",
          "uniqueItems": true,
          "maxItems": 16,
          "items": {
            "type": "string",
            "pattern": "^[A-Za-z0-9._:-]{1,64}$"
          }
        },
        "constraints": {
          "type": "array",
          "maxItems": 32,
          "items": {"$ref": "#/$defs/constraint"}
        },
        "required_evidence": {
          "type": "array",
          "uniqueItems": true,
          "maxItems": 32,
          "items": {
            "type": "string",
            "pattern": "^[a-z][a-z0-9_.-]{0,63}$"
          }
        },
        "idempotency_required": {"type": "boolean"},
        "max_retries": {"type": "integer", "minimum": 0, "maximum": 3}
      },
      "allOf": [
        {
          "if": {"properties": {"prohibited": {"const": true}}},
          "then": {"properties": {"requires_review": {"const": false}}}
        },
        {
          "if": {"properties": {"action_class": {"const": "irreversible"}}},
          "then": {"properties": {"requires_review": {"const": true}}}
        }
      ]
    },
    "constraint": {
      "type": "object",
      "additionalProperties": false,
      "required": ["type", "field"],
      "properties": {
        "type": {
          "type": "string",
          "enum": [
            "required_fields",
            "allowed_values",
            "max_numeric",
            "min_numeric",
            "max_age_seconds",
            "matches_pattern",
            "required_scope",
            "egress_classes",
            "rate_limit",
            "idempotency_required"
          ]
        },
        "field": {
          "type": "string",
          "pattern": "^[A-Za-z0-9_.-]{1,128}$"
        },
        "value": {},
        "values": {
          "type": "array",
          "maxItems": 256,
          "items": {"type": ["string", "number", "boolean"]}
        },
        "minimum": {"type": "number"},
        "maximum": {"type": "number"},
        "pattern": {"type": "string", "maxLength": 256},
        "window_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
        "max_count": {"type": "integer", "minimum": 1, "maximum": 100000}
      }
    },
    "dataControls": {
      "type": "object",
      "additionalProperties": false,
      "required": ["default_classification", "allowed_egress_classes", "redact_fields", "retention_seconds"],
      "properties": {
        "default_classification": {
          "type": "string",
          "enum": ["public", "internal", "confidential", "regulated"]
        },
        "allowed_egress_classes": {
          "type": "array",
          "uniqueItems": true,
          "items": {
            "type": "string",
            "enum": ["public", "internal", "confidential", "regulated"]
          }
        },
        "redact_fields": {
          "type": "array",
          "uniqueItems": true,
          "maxItems": 128,
          "items": {"type": "string", "pattern": "^[A-Za-z0-9_.-]{1,128}$"}
        },
        "retention_seconds": {
          "type": "integer",
          "minimum": 1,
          "maximum": 31536000
        }
      }
    },
    "evidencePolicy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["required", "max_age_seconds", "require_provenance", "on_missing"],
      "properties": {
        "required": {
          "type": "array",
          "uniqueItems": true,
          "maxItems": 64,
          "items": {"type": "string", "pattern": "^[a-z][a-z0-9_.-]{0,63}$"}
        },
        "max_age_seconds": {"type": "integer", "minimum": 1, "maximum": 31536000},
        "require_provenance": {"type": "boolean"},
        "on_missing": {"type": "string", "enum": ["PAUSE", "REJECT"]}
      }
    },
    "approvalPolicy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["required_for_irreversible", "quorum", "allowed_roles", "separation_of_duties"],
      "properties": {
        "required_for_irreversible": {"type": "boolean", "const": true},
        "quorum": {"type": "integer", "minimum": 1, "maximum": 16},
        "allowed_roles": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": {"type": "string", "pattern": "^[A-Za-z0-9._:-]{1,64}$"}
        },
        "separation_of_duties": {"type": "boolean"}
      }
    },
    "limits": {
      "type": "object",
      "additionalProperties": false,
      "required": ["max_action_rate_per_minute", "max_concurrent_actions", "kill_switch_required"],
      "properties": {
        "max_action_rate_per_minute": {"type": "integer", "minimum": 1, "maximum": 100000},
        "max_concurrent_actions": {"type": "integer", "minimum": 1, "maximum": 10000},
        "max_amount": {"type": "number", "exclusiveMinimum": 0},
        "max_quantity": {"type": "number", "exclusiveMinimum": 0},
        "kill_switch_required": {"type": "boolean", "const": true}
      }
    },
    "rolloutPolicy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["mode", "canary_percent", "dry_run_required", "stop_conditions"],
      "properties": {
        "mode": {"type": "string", "enum": ["dry_run", "canary", "pilot", "production"]},
        "canary_percent": {"type": "integer", "minimum": 0, "maximum": 100},
        "dry_run_required": {"type": "boolean", "const": true},
        "stop_conditions": {
          "type": "array",
          "minItems": 1,
          "maxItems": 32,
          "items": {"type": "string", "pattern": "^[A-Z][A-Z0-9_.-]{2,63}$"}
        }
      },
      "allOf": [
        {
          "if": {"properties": {"mode": {"const": "production"}}},
          "then": {"properties": {"canary_percent": {"const": 100}}}
        }
      ]
    },
    "signature": {
      "type": "object",
      "additionalProperties": false,
      "required": ["algorithm", "key_id", "value", "signed_fields"],
      "properties": {
        "algorithm": {"type": "string", "enum": ["HMAC-SHA256", "Ed25519"]},
        "key_id": {"type": "string", "pattern": "^[A-Za-z0-9._:-]{1,128}$"},
        "value": {"type": "string", "minLength": 16, "maxLength": 2048},
        "signed_fields": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": {"type": "string", "minLength": 1, "maxLength": 128}
        }
      }
    }
  }
}
```

## Example pack fragment

The following is illustrative only and is not yet a built-in production policy:

```json
{
  "schema_version": "1.0",
  "pack_id": "support-safe-refunds",
  "pack_version": "2026.08.30.1",
  "tenant_id": "synthetic-pilot",
  "domain": "customer_support",
  "policy_version": "support-policy-v1",
  "status": "DRAFT",
  "actions": {
    "lookup_ticket": {
      "action_class": "read_only",
      "requires_review": false,
      "prohibited": false,
      "reason_code": "SUPPORT_READ_ONLY",
      "constraints": [{"type": "required_scope", "field": "ticket_id"}],
      "required_evidence": ["authenticated_customer_scope"],
      "idempotency_required": false,
      "max_retries": 1
    },
    "issue_refund": {
      "action_class": "irreversible",
      "requires_review": true,
      "prohibited": false,
      "reason_code": "SUPPORT_REFUND_REVIEW",
      "required_roles": ["support_supervisor"],
      "constraints": [
        {"type": "required_fields", "field": "order_id"},
        {"type": "max_numeric", "field": "amount", "maximum": 250}
      ],
      "required_evidence": ["authenticated_customer_scope", "order_ownership"],
      "idempotency_required": true,
      "max_retries": 0
    }
  },
  "data_controls": {
    "default_classification": "confidential",
    "allowed_egress_classes": ["public", "internal"],
    "redact_fields": ["password", "token", "payment_number"],
    "retention_seconds": 2592000
  },
  "evidence": {
    "required": ["authenticated_customer_scope"],
    "max_age_seconds": 300,
    "require_provenance": true,
    "on_missing": "PAUSE"
  },
  "approval": {
    "required_for_irreversible": true,
    "quorum": 1,
    "allowed_roles": ["support_supervisor", "support_admin"],
    "separation_of_duties": true
  },
  "limits": {
    "max_action_rate_per_minute": 30,
    "max_concurrent_actions": 5,
    "max_amount": 250,
    "kill_switch_required": true
  },
  "rollout": {
    "mode": "dry_run",
    "canary_percent": 0,
    "dry_run_required": true,
    "stop_conditions": ["DUPLICATE_REFUND", "IDENTITY_SCOPE_FAILURE"]
  },
  "signature": {
    "algorithm": "Ed25519",
    "key_id": "synthetic-review-key",
    "value": "placeholder-for-signed-artifact",
    "signed_fields": ["schema_version", "pack_id", "pack_version", "tenant_id", "domain", "policy_version", "actions", "data_controls", "evidence", "approval", "limits", "rollout"]
  }
}
```

## Implementation constraints for EA-1

The first implementation should validate this contract with Pydantic and publish the JSON Schema from the same model where practical, avoiding two divergent sources of truth. It should add a domain-neutral `DomainPolicyPack` model, a deterministic `DomainPolicyEvaluator` protocol, and registry integration only after the schema is approved.

The evaluator should return structured findings, not an authorization boolean:

```text
PolicyEvaluation:
  outcome: ALLOW | PAUSE | REJECT
  reason_codes: list[str]
  required_roles: list[str]
  missing_evidence: list[str]
  policy_version: str
  pack_id: str
  pack_version: str
```

`ALLOW` must still pass the existing `HonestGuard` and signed-handoff gates. A domain evaluator must never issue a handoff token or call an executor.

## Open decisions for approval

1. Should `tenant_id` be mandatory in EA-1, or should a single-tenant development mode permit an explicit `tenant_id` default?
2. Should signatures use HMAC only for the first implementation, or should the model support both HMAC-SHA256 and Ed25519 from the start? Ed25519 is preferable for enterprise key separation, but adds a dependency and key-management work.
3. Should `status` be stored in the pack, or derived exclusively from the registry lifecycle to prevent conflicting states?
4. Should `data_controls.allowed_egress_classes` be a hard allow-list for every action, or may action rules further restrict it but never broaden it?
5. Should missing evidence always `PAUSE`, with `REJECT` reserved for explicit policy violations, or should packs choose per evidence class?
6. Should domain labels be fixed to these six values in EA-1, with extension labels deferred until after the first six packs are proven?

## Recommendation

Approve the contract with these defaults: mandatory trusted `tenant_id`; registry-derived lifecycle status; action rules may only tighten global data egress; missing evidence pauses unless the pack marks the evidence as safety-critical; HMAC-SHA256 for the first implementation with a clean signature-provider interface for later Ed25519; and the six listed domain labels only for EA-1.

No code changes should proceed until the open decisions are confirmed.
