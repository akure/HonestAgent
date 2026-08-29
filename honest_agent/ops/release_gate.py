from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


VALID_STATES = frozenset({"PASS", "PARTIAL", "BLOCKED", "NOT MEASURED"})
MANDATORY_BLOCKERS = ("B-1", "B-2", "B-3", "B-4", "B-5", "B-6")


@dataclass(frozen=True)
class ReleaseDecision:
    decision: str
    blockers: tuple[str, ...]
    rationale: str


def evaluate_release_gate(
    evidence: Mapping[str, str],
    *,
    residual_risk_accepted: bool = False,
    conditional_pilot: bool = False,
) -> ReleaseDecision:
    """Evaluate release evidence without inferring PASS from tests or omissions."""
    invalid = tuple(sorted(key for key, state in evidence.items() if state not in VALID_STATES))
    missing = tuple(blocker for blocker in MANDATORY_BLOCKERS if blocker not in evidence)
    blocked = tuple(blocker for blocker in MANDATORY_BLOCKERS if evidence.get(blocker) != "PASS")
    problems = tuple(dict.fromkeys((*invalid, *missing, *blocked)))
    if not problems and residual_risk_accepted:
        return ReleaseDecision("GO", (), "all mandatory blocker evidence is PASS and residual risk is accepted")
    if conditional_pilot and not invalid and not missing:
        return ReleaseDecision("CONDITIONAL PILOT", blocked, "pilot scope is explicit; unrestricted production evidence is incomplete")
    return ReleaseDecision("NO-GO", problems, "mandatory blocker evidence is incomplete or residual risk is not accepted")


__all__ = ["MANDATORY_BLOCKERS", "ReleaseDecision", "evaluate_release_gate"]
