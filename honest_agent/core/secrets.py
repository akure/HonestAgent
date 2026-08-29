from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Mapping


_DEVELOPMENT_HANDOFF = "honest-agent-development-secret"
_DEVELOPMENT_REVIEWER = "honest-agent-reviewer-development-secret"


class SecretConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class SecretConfig:
    handoff_secret: str
    handoff_previous_secrets: tuple[str, ...]
    reviewer_auth_secret: str
    reviewer_previous_secrets: tuple[str, ...]
    environment: str
    managed: bool

    def fingerprints(self) -> dict[str, str]:
        return {
            "handoff": secret_fingerprint(self.handoff_secret),
            "reviewer_auth": secret_fingerprint(self.reviewer_auth_secret),
        }


def secret_fingerprint(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:12]


def _csv(value: str | None) -> tuple[str, ...]:
    return tuple(item.strip() for item in (value or "").split(",") if item.strip())


def load_secret_config(environ: Mapping[str, str] | None = None) -> SecretConfig:
    env = environ if environ is not None else os.environ
    environment = env.get("HONEST_AGENT_ENV", "development").lower()
    managed = env.get("HONEST_AGENT_MANAGED_SECRETS", "false").lower() == "true"
    required = environment in {"production", "staging"} or managed
    handoff = env.get("HONEST_AGENT_HANDOFF_SECRET", "")
    reviewer = env.get("HONEST_AGENT_REVIEWER_AUTH_SECRET", "")
    if not required:
        handoff = handoff or _DEVELOPMENT_HANDOFF
        reviewer = reviewer or _DEVELOPMENT_REVIEWER
    if required:
        if not handoff or not reviewer:
            raise SecretConfigurationError("managed handoff and reviewer secrets are required")
        if len(handoff) < 32 or len(reviewer) < 32:
            raise SecretConfigurationError("managed secrets must be at least 32 characters")
        if handoff == _DEVELOPMENT_HANDOFF or reviewer == _DEVELOPMENT_REVIEWER:
            raise SecretConfigurationError("development secrets are not permitted in managed environments")
    return SecretConfig(
        handoff_secret=handoff,
        handoff_previous_secrets=_csv(env.get("HONEST_AGENT_HANDOFF_PREVIOUS_SECRETS")),
        reviewer_auth_secret=reviewer,
        reviewer_previous_secrets=_csv(env.get("HONEST_AGENT_REVIEWER_PREVIOUS_SECRETS")),
        environment=environment,
        managed=required,
    )
