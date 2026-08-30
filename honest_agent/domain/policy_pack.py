from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from honest_agent.schemas.models import ActionClass, EvaluationRequest


class DomainPolicyError(ValueError):
    """Raised when a domain policy pack is invalid or cannot be used safely."""


class Domain(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCIAL_TRADING = "financial_trading"
    RECRUITING_HR = "recruiting_hr"
    FORECASTING = "forecasting"
    ECOMMERCE = "ecommerce"
    CUSTOMER_SUPPORT = "customer_support"


class PackStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class MissingEvidenceAction(str, Enum):
    PAUSE = "PAUSE"
    REJECT = "REJECT"


class EvaluationOutcome(str, Enum):
    ALLOW = "ALLOW"
    PAUSE = "PAUSE"
    REJECT = "REJECT"


class ConstraintType(str, Enum):
    REQUIRED_FIELDS = "required_fields"
    ALLOWED_VALUES = "allowed_values"
    MAX_NUMERIC = "max_numeric"
    MIN_NUMERIC = "min_numeric"
    MAX_AGE_SECONDS = "max_age_seconds"
    MATCHES_PATTERN = "matches_pattern"
    REQUIRED_SCOPE = "required_scope"
    EGRESS_CLASSES = "egress_classes"
    RATE_LIMIT = "rate_limit"
    IDEMPOTENCY_REQUIRED = "idempotency_required"


class Constraint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ConstraintType
    field: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.-]+$")
    value: Any = None
    values: list[str | int | float | bool] = Field(default_factory=list, max_length=256)
    minimum: float | None = None
    maximum: float | None = None
    pattern: str | None = Field(default=None, max_length=256)
    window_seconds: int | None = Field(default=None, ge=1, le=86400)
    max_count: int | None = Field(default=None, ge=1, le=100000)

    @model_validator(mode="after")
    def validate_parameters(self) -> "Constraint":
        if self.type == ConstraintType.ALLOWED_VALUES and not self.values:
            raise ValueError("allowed_values requires values")
        if self.type in {ConstraintType.MAX_NUMERIC, ConstraintType.MIN_NUMERIC} and self.maximum is None and self.minimum is None:
            raise ValueError("numeric constraint requires a bound")
        if self.type == ConstraintType.MATCHES_PATTERN and not self.pattern:
            raise ValueError("matches_pattern requires pattern")
        if self.type == ConstraintType.RATE_LIMIT and (self.window_seconds is None or self.max_count is None):
            raise ValueError("rate_limit requires window_seconds and max_count")
        return self


class ActionRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_class: ActionClass
    requires_review: bool
    prohibited: bool
    reason_code: str = Field(pattern=r"^[A-Z][A-Z0-9_.-]{2,63}$")
    required_roles: list[str] = Field(default_factory=list, max_length=16)
    constraints: list[Constraint] = Field(default_factory=list, max_length=32)
    required_evidence: list[str] = Field(default_factory=list, max_length=32)
    idempotency_required: bool = False
    max_retries: int = Field(default=0, ge=0, le=3)

    @model_validator(mode="after")
    def enforce_safety_defaults(self) -> "ActionRule":
        if self.prohibited and self.requires_review:
            raise ValueError("prohibited actions cannot be review-authorized")
        if self.action_class == ActionClass.IRREVERSIBLE and not self.requires_review:
            raise ValueError("irreversible actions require review")
        return self


class DataControls(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_classification: str = Field(pattern=r"^(public|internal|confidential|regulated)$")
    allowed_egress_classes: list[str] = Field(min_length=1, max_length=4)
    redact_fields: list[str] = Field(default_factory=list, max_length=128)
    retention_seconds: int = Field(gt=0, le=31536000)


class EvidencePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required: list[str] = Field(default_factory=list, max_length=64)
    max_age_seconds: int = Field(gt=0, le=31536000)
    require_provenance: bool = True
    on_missing: MissingEvidenceAction = MissingEvidenceAction.PAUSE


class ApprovalPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_for_irreversible: bool = True
    quorum: int = Field(ge=1, le=16)
    allowed_roles: list[str] = Field(min_length=1, max_length=16)
    separation_of_duties: bool = True

    @field_validator("required_for_irreversible")
    @classmethod
    def irreversible_approval_is_mandatory(cls, value: bool) -> bool:
        if not value:
            raise ValueError("required_for_irreversible must remain true")
        return value


class Limits(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_action_rate_per_minute: int = Field(ge=1, le=100000)
    max_concurrent_actions: int = Field(ge=1, le=10000)
    max_amount: float | None = Field(default=None, gt=0)
    max_quantity: float | None = Field(default=None, gt=0)
    kill_switch_required: bool = True

    @field_validator("kill_switch_required")
    @classmethod
    def kill_switch_is_mandatory(cls, value: bool) -> bool:
        if not value:
            raise ValueError("kill_switch_required must remain true")
        return value


class RolloutPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = Field(pattern=r"^(dry_run|canary|pilot|production)$")
    canary_percent: int = Field(ge=0, le=100)
    dry_run_required: bool = True
    stop_conditions: list[str] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def enforce_rollout_safety(self) -> "RolloutPolicy":
        if not self.dry_run_required:
            raise ValueError("dry_run_required must remain true")
        if self.mode == "production" and self.canary_percent != 100:
            raise ValueError("production rollout requires canary_percent=100")
        return self


class Signature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    algorithm: str = Field(pattern=r"^HMAC-SHA256$")
    key_id: str = Field(min_length=1, max_length=128)
    value: str = Field(min_length=16, max_length=2048)
    signed_fields: list[str] = Field(min_length=1, max_length=32)


class DomainPolicyPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(pattern=r"^1\.[0-9]+$")
    pack_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
    pack_version: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
    tenant_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}$")
    domain: Domain
    policy_version: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
    status: PackStatus
    actions: dict[str, ActionRule] = Field(min_length=1, max_length=256)
    data_controls: DataControls
    evidence: EvidencePolicy
    approval: ApprovalPolicy
    limits: Limits
    rollout: RolloutPolicy
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict, max_length=32)
    signature: Signature

    @field_validator("actions")
    @classmethod
    def validate_action_names(cls, value: dict[str, ActionRule]) -> dict[str, ActionRule]:
        for name in value:
            if not name.strip() or len(name) > 128:
                raise ValueError("action names must be non-empty and at most 128 characters")
        return value


@dataclass(frozen=True)
class PolicyFinding:
    outcome: EvaluationOutcome
    reason_codes: tuple[str, ...] = ()
    required_roles: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    policy_version: str = ""
    pack_id: str = ""
    pack_version: str = ""


class DomainPolicyEvaluator(Protocol):
    def evaluate(self, request: EvaluationRequest, *, evidence: Mapping[str, Any] | None = None) -> PolicyFinding:
        ...


class DeterministicDomainPolicyEvaluator:
    """Evaluates a validated pack without model calls, network calls, or side effects."""

    def __init__(self, pack: DomainPolicyPack, *, now: float | None = None):
        if pack.status != PackStatus.ACTIVE:
            raise DomainPolicyError("only an active policy pack can evaluate requests")
        self.pack = pack
        self.now = now

    def evaluate(self, request: EvaluationRequest, *, evidence: Mapping[str, Any] | None = None) -> PolicyFinding:
        base = dict(policy_version=self.pack.policy_version, pack_id=self.pack.pack_id, pack_version=self.pack.pack_version)
        if request.metadata.get("tenant_id") != self.pack.tenant_id:
            return PolicyFinding(EvaluationOutcome.REJECT, ("TENANT_SCOPE_MISMATCH",), **base)
        rule = self.pack.actions.get(request.tool_name)
        if rule is None:
            return PolicyFinding(EvaluationOutcome.REJECT, ("UNKNOWN_DOMAIN_ACTION",), **base)
        if rule.prohibited:
            return PolicyFinding(EvaluationOutcome.REJECT, (rule.reason_code,), **base)
        failed = self._failed_constraints(rule, request)
        if failed:
            return PolicyFinding(EvaluationOutcome.REJECT, tuple(failed), tuple(rule.required_roles), policy_version=self.pack.policy_version, pack_id=self.pack.pack_id, pack_version=self.pack.pack_version)
        if evidence is not None and not isinstance(evidence, Mapping):
            return PolicyFinding(EvaluationOutcome.REJECT, ("MALFORMED_EVIDENCE",), tuple(rule.required_roles), policy_version=self.pack.policy_version, pack_id=self.pack.pack_id, pack_version=self.pack.pack_version)
        evidence_map = evidence or {}
        required = tuple(dict.fromkeys((*self.pack.evidence.required, *rule.required_evidence)))
        missing = tuple(name for name in required if not evidence_map.get(name))
        if missing:
            outcome = EvaluationOutcome.PAUSE if self.pack.evidence.on_missing == MissingEvidenceAction.PAUSE else EvaluationOutcome.REJECT
            return PolicyFinding(outcome, ("MISSING_EVIDENCE",), tuple(rule.required_roles), missing, **base)
        if rule.idempotency_required and not request.metadata.get("idempotency_key"):
            return PolicyFinding(EvaluationOutcome.REJECT, ("IDEMPOTENCY_KEY_REQUIRED",), tuple(rule.required_roles), policy_version=self.pack.policy_version, pack_id=self.pack.pack_id, pack_version=self.pack.pack_version)
        if rule.requires_review or rule.action_class == ActionClass.IRREVERSIBLE:
            return PolicyFinding(EvaluationOutcome.PAUSE, (rule.reason_code,), tuple(rule.required_roles), policy_version=self.pack.policy_version, pack_id=self.pack.pack_id, pack_version=self.pack.pack_version)
        return PolicyFinding(EvaluationOutcome.ALLOW, (rule.reason_code,), policy_version=self.pack.policy_version, pack_id=self.pack.pack_id, pack_version=self.pack.pack_version)

    def _failed_constraints(self, rule: ActionRule, request: EvaluationRequest) -> list[str]:
        failures: list[str] = []
        payload = request.tool_input
        for constraint in rule.constraints:
            value = payload.get(constraint.field)
            if constraint.type in {ConstraintType.REQUIRED_FIELDS, ConstraintType.REQUIRED_SCOPE} and (value is None or value == ""):
                failures.append(f"MISSING_{constraint.field.upper().replace('.', '_')}")
            elif constraint.type == ConstraintType.ALLOWED_VALUES and value not in constraint.values:
                failures.append(f"VALUE_NOT_ALLOWED_{constraint.field.upper().replace('.', '_')}")
            elif constraint.type == ConstraintType.MAX_NUMERIC and (not isinstance(value, (int, float)) or value > constraint.maximum):
                failures.append(f"MAXIMUM_EXCEEDED_{constraint.field.upper().replace('.', '_')}")
            elif constraint.type == ConstraintType.MIN_NUMERIC and (not isinstance(value, (int, float)) or value < constraint.minimum):
                failures.append(f"MINIMUM_NOT_MET_{constraint.field.upper().replace('.', '_')}")
            elif constraint.type == ConstraintType.MATCHES_PATTERN and (not isinstance(value, str) or re.fullmatch(constraint.pattern or "", value) is None):
                failures.append(f"PATTERN_MISMATCH_{constraint.field.upper().replace('.', '_')}")
            elif constraint.type == ConstraintType.IDEMPOTENCY_REQUIRED and not request.metadata.get("idempotency_key"):
                failures.append("IDEMPOTENCY_KEY_REQUIRED")
        return failures


class DomainPolicyRegistry:
    """Small signed file-backed lifecycle for tenant-scoped domain packs."""

    def __init__(self, path: str = "policies/domain-packs.json", *, signing_secret: str, now: float | None = None):
        if not signing_secret or "development" in signing_secret:
            raise DomainPolicyError("managed signing secret is required")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.signing_secret = signing_secret.encode()
        self.now = now
        self._state = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"active": {}, "packs": {}}
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(state, dict) or not isinstance(state.get("active", {}), dict) or not isinstance(state.get("packs", {}), dict):
                raise DomainPolicyError("domain policy registry has invalid shape")
            return state
        except (OSError, json.JSONDecodeError) as exc:
            raise DomainPolicyError("domain policy registry is unreadable") from exc

    def _canonical(self, pack: DomainPolicyPack) -> bytes:
        # Lifecycle status and registry audit fields are mutable metadata, not signed policy content.
        data = pack.model_dump(mode="json", exclude={"signature", "status"})
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()

    def sign(self, pack: DomainPolicyPack, key_id: str = "managed") -> DomainPolicyPack:
        signature = hmac.new(self.signing_secret, self._canonical(pack), hashlib.sha256).hexdigest()
        return pack.model_copy(update={"signature": Signature(algorithm="HMAC-SHA256", key_id=key_id, value=signature, signed_fields=list(pack.model_dump(exclude={"signature", "status"}).keys()))})

    def verify(self, pack: DomainPolicyPack) -> None:
        expected = hmac.new(self.signing_secret, self._canonical(pack), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(pack.signature.value, expected):
            raise DomainPolicyError("domain policy signature is invalid")

    def import_pack(self, pack: DomainPolicyPack, imported_by: str) -> DomainPolicyPack:
        if not imported_by.strip():
            raise DomainPolicyError("importer identity is required")
        if pack.status != PackStatus.DRAFT:
            raise DomainPolicyError("new domain policy packs must be DRAFT")
        signed = self.sign(pack)
        key = f"{signed.tenant_id}:{signed.pack_id}:{signed.pack_version}"
        if key in self._state["packs"]:
            raise DomainPolicyError("domain policy pack already exists")
        record = signed.model_dump(mode="json")
        record["imported_by"] = imported_by
        record["approved_by"] = []
        self._state["packs"][key] = record
        self._write()
        return signed

    def approve(self, tenant_id: str, pack_id: str, pack_version: str, reviewer: str) -> None:
        if not reviewer.strip():
            raise DomainPolicyError("reviewer identity is required")
        record = self._record(tenant_id, pack_id, pack_version)
        if reviewer not in record["approved_by"]:
            record["approved_by"].append(reviewer)
        record["status"] = PackStatus.APPROVED.value
        self._write()

    def activate(self, tenant_id: str, pack_id: str, pack_version: str, actor: str, *, quorum: int = 1) -> DomainPolicyPack:
        if not actor.strip() or quorum < 1:
            raise DomainPolicyError("valid activation actor and quorum are required")
        record = self._record(tenant_id, pack_id, pack_version)
        pack = DomainPolicyPack.model_validate({key: value for key, value in record.items() if key in DomainPolicyPack.model_fields})
        self.verify(pack)
        if len(record["approved_by"]) < quorum:
            raise DomainPolicyError(f"domain policy requires {quorum} approval(s)")
        active_key = f"{tenant_id}:{pack_id}"
        for key, value in self._state["packs"].items():
            if key.startswith(active_key + ":"):
                value["status"] = PackStatus.RETIRED.value
        record["status"] = PackStatus.ACTIVE.value
        record["activated_by"] = actor
        record["activated_at"] = self.now if self.now is not None else time.time()
        self._state["active"][f"{tenant_id}:{pack_id}"] = f"{tenant_id}:{pack_id}:{pack_version}"
        self._write()
        return DomainPolicyPack.model_validate({field: record[field] for field in DomainPolicyPack.model_fields})

    def get_active(self, tenant_id: str, pack_id: str) -> DomainPolicyPack:
        key = self._state["active"].get(f"{tenant_id}:{pack_id}")
        if not key:
            raise DomainPolicyError("no active domain policy pack")
        record = self._state["packs"][key]
        pack = DomainPolicyPack.model_validate({field: record[field] for field in DomainPolicyPack.model_fields})
        self.verify(pack)
        return pack

    def _record(self, tenant_id: str, pack_id: str, pack_version: str) -> dict[str, Any]:
        key = f"{tenant_id}:{pack_id}:{pack_version}"
        record = self._state["packs"].get(key)
        if record is None:
            raise DomainPolicyError("unknown domain policy pack")
        return record

    def _write(self) -> None:
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(json.dumps(self._state, indent=2, sort_keys=True), encoding="utf-8")
        temp.replace(self.path)

    def evaluator(self, tenant_id: str, pack_id: str) -> DeterministicDomainPolicyEvaluator:
        return DeterministicDomainPolicyEvaluator(self.get_active(tenant_id, pack_id), now=self.now)


def domain_policy_json_schema() -> dict[str, Any]:
    """Return the schema generated from the runtime model, for publication and tooling."""
    return DomainPolicyPack.model_json_schema()
