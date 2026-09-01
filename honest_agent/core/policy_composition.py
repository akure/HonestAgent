from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from honest_agent.schemas.models import ActionClass, PolicyRule
from honest_agent.schemas.workflow import WorkflowBudgets, WorkflowRunContext


class PolicyCompositionError(ValueError):
    pass


@dataclass(frozen=True)
class PolicyLayer:
    name: str
    rules: Mapping[str, PolicyRule]
    allowed_tools: frozenset[str] | None = None
    budgets: WorkflowBudgets | None = None


@dataclass(frozen=True)
class EffectiveRule:
    tool_name: str
    rule: PolicyRule
    source_layers: tuple[str, ...]
    conflict_reason: str = ""


@dataclass(frozen=True)
class EffectivePolicy:
    snapshot_id: str
    rules: Mapping[str, EffectiveRule]
    allowed_tools: frozenset[str] | None
    budgets: WorkflowBudgets | None
    layers: tuple[str, ...]

    def rule_for(self, tool_name: str) -> EffectiveRule:
        try:
            return self.rules[tool_name]
        except KeyError as exc:
            raise PolicyCompositionError(f"no effective policy for tool: {tool_name}") from exc


_ACTION_STRICTNESS = {
    ActionClass.READ_ONLY: 0,
    ActionClass.REVERSIBLE: 1,
    ActionClass.IRREVERSIBLE: 2,
    ActionClass.UNKNOWN: 3,
}


def _rule_strictness(rule: PolicyRule) -> tuple[int, int]:
    return (_ACTION_STRICTNESS[rule.action_class], int(rule.requires_review))


def _budget_minimum(values: list[WorkflowBudgets]) -> WorkflowBudgets:
    fields = WorkflowBudgets.model_fields
    return WorkflowBudgets(**{field: min(getattr(value, field) for value in values) for field in fields})


class PolicyComposer:
    """Resolve layered policies monotonically; later layers cannot weaken earlier ones."""

    def resolve(self, layers: tuple[PolicyLayer, ...] | list[PolicyLayer]) -> EffectivePolicy:
        ordered = tuple(layers)
        if not ordered or any(not layer.name.strip() for layer in ordered) or len({layer.name for layer in ordered}) != len(ordered):
            raise PolicyCompositionError("policy layers require unique non-empty names")
        rules: dict[str, EffectiveRule] = {}
        for layer in ordered:
            for tool_name, candidate in layer.rules.items():
                if not tool_name.strip():
                    raise PolicyCompositionError("policy tool names must be non-empty")
                current = rules.get(tool_name)
                if current is None:
                    rules[tool_name] = EffectiveRule(tool_name, candidate, (layer.name,))
                    continue
                selected = candidate if _rule_strictness(candidate) > _rule_strictness(current.rule) else current.rule
                reasons = list(current.source_layers)
                if layer.name not in reasons:
                    reasons.append(layer.name)
                conflict = current.conflict_reason
                if candidate != current.rule:
                    conflict = f"strictest rule selected across {', '.join(reasons)}"
                rules[tool_name] = EffectiveRule(tool_name, selected, tuple(reasons), conflict)
        allowed_sets = [layer.allowed_tools for layer in ordered if layer.allowed_tools is not None]
        allowed_tools = frozenset.intersection(*allowed_sets) if allowed_sets else None
        budget_values = [layer.budgets for layer in ordered if layer.budgets is not None]
        budgets = _budget_minimum(budget_values) if budget_values else None
        snapshot_payload = {
            "layers": [layer.name for layer in ordered],
            "rules": {name: effective.rule.model_dump(mode="json") for name, effective in sorted(rules.items())},
            "allowed_tools": sorted(allowed_tools) if allowed_tools is not None else None,
            "budgets": budgets.model_dump(mode="json") if budgets else None,
        }
        snapshot_id = "policy-" + hashlib.sha256(json.dumps(snapshot_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:32]
        return EffectivePolicy(snapshot_id, MappingProxyType(rules), allowed_tools, budgets, tuple(layer.name for layer in ordered))

    def attenuate_child(self, parent: WorkflowRunContext, policy: EffectivePolicy, step_id: str, child_budgets: WorkflowBudgets, *, allowed_tools: frozenset[str] | None = None, deadline: float | None = None) -> WorkflowRunContext:
        requested_tools = parent.allowed_tools if allowed_tools is None else allowed_tools
        if policy.allowed_tools is not None:
            if not requested_tools.issubset(policy.allowed_tools):
                raise PolicyCompositionError("child delegation requests a tool outside the effective policy")
        if policy.budgets is not None:
            policy.budgets.attenuate(child_budgets)
        return parent.derive_child(step_id, child_budgets, allowed_tools=requested_tools, deadline=deadline).model_copy(update={"policy_snapshot_id": policy.snapshot_id})


__all__ = ["EffectivePolicy", "EffectiveRule", "PolicyCompositionError", "PolicyComposer", "PolicyLayer"]
