from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from honest_agent.schemas.workflow import EvidenceEnvelope, TrustClass


_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    re.compile(r"disregard\s+(the\s+)?(system|safety|security)\s+(message|policy|rules)", re.I),
    re.compile(r"reveal\s+(the\s+)?(system\s+prompt|secret|credential)", re.I),
    re.compile(r"you\s+are\s+now\s+the\s+system", re.I),
)


class RetrievalBlocked(ValueError):
    pass


@dataclass(frozen=True)
class RetrievalChunk:
    evidence: EvidenceEnvelope
    content: str
    egress_class: str


@dataclass(frozen=True)
class RetrievalDecision:
    outcome: str
    accepted_evidence_ids: tuple[str, ...]
    rejected_evidence_ids: tuple[str, ...]
    injection_detected: bool
    reasons: tuple[str, ...]


class RAGEvidenceBoundary:
    """Keep retrieved content untrusted and separate from authorization metadata."""

    def __init__(self, tenant_id: str, allowed_source_ids: frozenset[str] | None = None, allowed_egress_classes: frozenset[str] = frozenset({"internal"}), high_impact_requires_trusted: bool = True):
        self.tenant_id = tenant_id
        self.allowed_source_ids = allowed_source_ids
        self.allowed_egress_classes = allowed_egress_classes
        self.high_impact_requires_trusted = high_impact_requires_trusted

    def inspect(self, chunks: Iterable[RetrievalChunk], now: float | None = None, high_impact: bool = False) -> RetrievalDecision:
        accepted: list[str] = []
        rejected: list[str] = []
        reasons: list[str] = []
        injection = False
        for chunk in chunks:
            evidence = chunk.evidence
            reason = None
            if evidence.tenant_scope != self.tenant_id:
                reason = "CROSS_TENANT_EVIDENCE"
            elif self.allowed_source_ids is not None and evidence.source_id not in self.allowed_source_ids:
                reason = "SOURCE_NOT_ALLOWED"
            elif chunk.egress_class not in self.allowed_egress_classes:
                reason = "EGRESS_CLASS_NOT_ALLOWED"
            elif not evidence.is_fresh(now):
                reason = "STALE_EVIDENCE"
            elif high_impact and self.high_impact_requires_trusted and evidence.trust_class is not TrustClass.TRUSTED:
                reason = "HIGH_IMPACT_EVIDENCE_NOT_TRUSTED"
            if any(pattern.search(chunk.content) for pattern in _INJECTION_PATTERNS):
                injection = True
                if reason is None:
                    reason = "PROMPT_INJECTION_SIGNAL"
            if reason is None:
                accepted.append(evidence.evidence_id)
            else:
                rejected.append(evidence.evidence_id)
                reasons.append(f"{evidence.evidence_id}:{reason}")
        if injection or rejected:
            return RetrievalDecision("PAUSE", tuple(accepted), tuple(rejected), injection, tuple(reasons))
        return RetrievalDecision("ALLOW", tuple(accepted), (), False, ())

    def require_citation_coverage(self, evidence_ids: Iterable[str], cited_evidence_ids: Iterable[str], high_impact: bool = False) -> None:
        expected = set(evidence_ids)
        cited = set(cited_evidence_ids)
        if high_impact and expected - cited:
            raise RetrievalBlocked("CITATION_COVERAGE_INCOMPLETE")

    @staticmethod
    def authorization_evidence(evidence: EvidenceEnvelope) -> None:
        if not evidence.authorization_bearing or evidence.trust_class is not TrustClass.TRUSTED:
            raise RetrievalBlocked("retrieved content cannot bear authorization")
