from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextTelemetry:
    token_count: int
    max_context_tokens: int
    ratio: float
    near_capacity: bool


class ContextEvaluator:
    """Deterministic tokenizer fallback suitable for reproducible local evaluation."""

    _TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)

    def count_tokens(self, text: str) -> int:
        return len(self._TOKEN_RE.findall(text or ""))

    def evaluate(self, text: str, max_context_tokens: int, escalation_ratio: float = 0.80) -> ContextTelemetry:
        if max_context_tokens <= 0:
            raise ValueError("max_context_tokens must be positive")
        count = self.count_tokens(text)
        ratio = min(1.0, count / max_context_tokens)
        return ContextTelemetry(
            token_count=count,
            max_context_tokens=max_context_tokens,
            ratio=ratio,
            near_capacity=ratio >= escalation_ratio,
        )
