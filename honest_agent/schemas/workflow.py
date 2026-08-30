from __future__ import annotations

import hashlib
import json
import math
import time
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class WorkflowBudgets(ContractBase):
    verifier_calls: int = Field(default=10, ge=0)
    tool_calls: int = Field(default=10, ge=0)
    retries: int = Field(default=3, ge=0)
    tokens: int = Field(default=100_000, ge=0)
    fan_out: int = Field(default=1, ge=0)
    concurrency: int = Field(default=1, ge=0)
    cumulative_amount: float = Field(default=0.0, ge=0.0)

    def attenuate(self, child: "WorkflowBudgets") -> "WorkflowBudgets":
        if any(getattr(child, field) > getattr(self, field) for field in self.model_fields):
            raise ValueError("child budget cannot exceed parent budget")
        return child


class WorkflowRunContext(ContractBase):
    contract_version: str = "cx0"
    run_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    root_agent_id: str = Field(min_length=1, max_length=128)
    parent_step_id: str | None = None
    step_id: str = Field(min_length=1, max_length=128)
    attempt: int = Field(default=1, ge=1)
    delegation_chain: List[str] = Field(default_factory=list, max_length=32)
    workflow_version: str = Field(min_length=1, max_length=64)
    deadline: float = Field(gt=0)
    budgets: WorkflowBudgets = Field(default_factory=WorkflowBudgets)
    kill_switch_epoch: int = Field(default=0, ge=0)
    policy_snapshot_id: str = Field(min_length=1, max_length=128)
    allowed_tools: frozenset[str] = frozenset()

    @model_validator(mode="after")
    def validate_deadline(self) -> "WorkflowRunContext":
        if self.deadline <= 0:
            raise ValueError("deadline must be positive")
        return self

    def derive_child(self, step_id: str, child_budgets: WorkflowBudgets, allowed_tools: frozenset[str] | None = None, deadline: float | None = None) -> "WorkflowRunContext":
        tools = allowed_tools if allowed_tools is not None else self.allowed_tools
        if not tools.issubset(self.allowed_tools):
            raise ValueError("child delegation cannot add tools")
        child_deadline = self.deadline if deadline is None else deadline
        if child_deadline > self.deadline:
            raise ValueError("child delegation cannot extend deadline")
        self.budgets.attenuate(child_budgets)
        return WorkflowRunContext(
            run_id=self.run_id,
            tenant_id=self.tenant_id,
            root_agent_id=self.root_agent_id,
            parent_step_id=self.step_id,
            step_id=step_id,
            attempt=1,
            delegation_chain=[*self.delegation_chain, self.step_id],
            workflow_version=self.workflow_version,
            deadline=child_deadline,
            budgets=child_budgets,
            kill_switch_epoch=self.kill_switch_epoch,
            policy_snapshot_id=self.policy_snapshot_id,
            allowed_tools=tools,
        )


class IntentProvenance(str, Enum):
    MODEL = "model"
    HUMAN = "human"
    RULE = "rule"
    DELEGATED_AGENT = "delegated_agent"


class SideEffectMode(str, Enum):
    NONE = "none"
    SIMULATED = "simulated"
    EXTERNAL = "external"


class ToolIntent(ContractBase):
    contract_version: str = "cx0"
    tool_name: str = Field(min_length=1, max_length=128)
    argument_schema_version: str = Field(min_length=1, max_length=64)
    canonical_arguments: Dict[str, Any] = Field(default_factory=dict)
    declared_action_class: str = Field(min_length=1, max_length=32)
    resource_scope: Dict[str, str] = Field(default_factory=dict)
    destination: str = Field(default="local", min_length=1, max_length=256)
    idempotency_key: str = Field(min_length=1, max_length=256)
    expected_side_effect_mode: SideEffectMode = SideEffectMode.NONE
    provenance: IntentProvenance

    @model_validator(mode="after")
    def validate_json_values(self) -> "ToolIntent":
        encoded = json.dumps(self.canonical_arguments, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        if not encoded:
            raise ValueError("canonical arguments must be JSON serializable")
        return self

    def canonical_bytes(self) -> bytes:
        payload = self.model_dump(mode="json")
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")

    def canonical_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class TrustClass(str, Enum):
    UNKNOWN = "unknown"
    UNTRUSTED = "untrusted"
    ATTRIBUTABLE = "attributable"
    TRUSTED = "trusted"


class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class CitationSpan(ContractBase):
    start: int = Field(ge=0)
    end: int = Field(gt=0)

    @model_validator(mode="after")
    def ordered(self) -> "CitationSpan":
        if self.end <= self.start:
            raise ValueError("citation end must be greater than start")
        return self


class EvidenceEnvelope(ContractBase):
    contract_version: str = "cx0"
    evidence_id: str = Field(min_length=1, max_length=128)
    source_id: str = Field(min_length=1, max_length=256)
    source_type: str = Field(min_length=1, max_length=64)
    tenant_scope: str = Field(min_length=1, max_length=128)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    provenance_chain: List[str] = Field(default_factory=list, max_length=32)
    observed_at: float = Field(gt=0)
    expires_at: float | None = Field(default=None, gt=0)
    trust_class: TrustClass = TrustClass.UNKNOWN
    data_classification: DataClassification = DataClassification.INTERNAL
    lineage_references: List[str] = Field(default_factory=list, max_length=64)
    retrieval_query_id: str | None = Field(default=None, max_length=128)
    citation_spans: List[CitationSpan] = Field(default_factory=list, max_length=128)
    authorization_bearing: bool = False
    redacted_reference: str | None = Field(default=None, max_length=256)

    @model_validator(mode="after")
    def validate_authority_and_time(self) -> "EvidenceEnvelope":
        if self.authorization_bearing and self.trust_class is not TrustClass.TRUSTED:
            raise ValueError("authorization-bearing evidence requires a trusted producer")
        if self.expires_at is not None and self.expires_at <= self.observed_at:
            raise ValueError("evidence expiry must follow observation time")
        if self.redacted_reference is None:
            raise ValueError("raw evidence content is not accepted; provide a redacted reference")
        return self

    def is_fresh(self, now: float | None = None) -> bool:
        current = time.time() if now is None else now
        return self.observed_at <= current and (self.expires_at is None or current < self.expires_at)


class DecisionRecord(ContractBase):
    contract_version: str = "cx0"
    decision_id: str = Field(min_length=1, max_length=128)
    run_id: str = Field(min_length=1, max_length=128)
    step_id: str = Field(min_length=1, max_length=128)
    attempt: int = Field(ge=1)
    intent_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence_ids: List[str] = Field(default_factory=list)
    policy_snapshot_id: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=32)
    reason_codes: List[str] = Field(default_factory=list)
    redacted_references: List[str] = Field(default_factory=list)


class ControlEvent(ContractBase):
    contract_version: str = "cx0"
    event_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=64)
    occurred_at: float = Field(gt=0)
    run_id: str = Field(min_length=1, max_length=128)
    step_id: str = Field(min_length=1, max_length=128)
    actor_id: str = Field(min_length=1, max_length=128)
    redacted_payload: Dict[str, Any] = Field(default_factory=dict)
