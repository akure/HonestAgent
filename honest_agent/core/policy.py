from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class ActionClass(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    IRREVERSIBLE = "irreversible"
    UNKNOWN = "unknown"


DEFAULT_IRREVERSIBLE_VERBS = frozenset({"write", "delete", "drop", "migrate", "send", "publish", "execute", "run", "transfer", "charge"})


@dataclass(frozen=True)
class PolicyDecision:
    action_class: ActionClass
    requires_escalation: bool
    reason: str


class ActionPolicy:
    """Deterministic policy boundary; model output never decides action class."""

    def __init__(self, irreversible_verbs: frozenset[str] = DEFAULT_IRREVERSIBLE_VERBS):
        self.irreversible_verbs = irreversible_verbs

    def classify(self, tool_name: str, explicitly_irreversible: bool = False) -> PolicyDecision:
        if explicitly_irreversible:
            return PolicyDecision(ActionClass.IRREVERSIBLE, True, "caller declared an irreversible action")
        tokens = set(re.findall(r"[a-z0-9]+", tool_name.lower()))
        if tokens & self.irreversible_verbs:
            return PolicyDecision(ActionClass.IRREVERSIBLE, True, "tool name contains a configured irreversible verb")
        if not tool_name:
            return PolicyDecision(ActionClass.UNKNOWN, True, "tool name is missing")
        if any(token in tokens for token in ("read", "get", "list", "lookup", "search", "fetch", "inspect", "health", "status")):
            return PolicyDecision(ActionClass.READ_ONLY, False, "tool name matches a read-only convention")
        return PolicyDecision(ActionClass.UNKNOWN, False, "tool is not classified by default policy")
