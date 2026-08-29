from __future__ import annotations

from dataclasses import dataclass
from re import findall
from typing import Mapping

from honest_agent.schemas.models import ActionClass, PolicyRule


DEFAULT_IRREVERSIBLE_VERBS = frozenset(
    {"write", "delete", "drop", "migrate", "send", "publish", "execute", "run", "transfer", "charge"}
)


@dataclass(frozen=True)
class PolicyDecision:
    action_class: ActionClass
    requires_escalation: bool
    reason: str
    policy_version: str


class ActionPolicy:
    """Deterministic action classification; verifier output never authorizes execution."""

    def __init__(self, rules: Mapping[str, PolicyRule] | None = None, version: str = "default-v1"):
        self.version = version
        self.rules = {
            "rewrite_summary": PolicyRule(
                action_class=ActionClass.REVERSIBLE,
                requires_review=False,
                reason="built-in pure text transformation",
            ),
            "calculate": PolicyRule(
                action_class=ActionClass.REVERSIBLE,
                requires_review=False,
                reason="built-in pure calculation",
            ),
            **dict(rules or {}),
        }

    def register(self, tool_name: str, rule: PolicyRule) -> "ActionPolicy":
        if not tool_name.strip():
            raise ValueError("tool_name must not be empty")
        self.rules[tool_name] = rule
        return self

    def classify(self, tool_name: str, explicitly_irreversible: bool = False) -> PolicyDecision:
        if explicitly_irreversible:
            return PolicyDecision(ActionClass.IRREVERSIBLE, True, "caller declared an irreversible action", self.version)
        if tool_name in self.rules:
            rule = self.rules[tool_name]
            return PolicyDecision(rule.action_class, rule.requires_review, rule.reason, self.version)
        if not tool_name.strip():
            return PolicyDecision(ActionClass.UNKNOWN, True, "tool name is missing", self.version)
        tokens = set(findall(r"[a-z0-9]+", tool_name.lower()))
        if tokens & DEFAULT_IRREVERSIBLE_VERBS:
            return PolicyDecision(ActionClass.IRREVERSIBLE, True, "tool name matches an irreversible convention", self.version)
        if tokens & {"read", "get", "list", "lookup", "search", "fetch", "inspect", "health", "status"}:
            return PolicyDecision(ActionClass.READ_ONLY, False, "tool name matches a read-only convention", self.version)
        return PolicyDecision(ActionClass.UNKNOWN, True, "tool is not explicitly classified", self.version)
