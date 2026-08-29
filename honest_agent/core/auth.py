from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Mapping


class AuthError(ValueError):
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ReviewerPrincipal:
    subject: str
    role: str
    expires_at: int
    auth_method: str = "bearer-hmac"


class ReviewerRoster:
    """Least-privilege reviewer roster with explicit active identities."""

    def __init__(self, members: Mapping[str, str] | None = None):
        self._members = dict(members or {})

    def role_for(self, subject: str) -> str | None:
        return self._members.get(subject)

    def revoke(self, subject: str) -> None:
        self._members.pop(subject, None)

    def add(self, subject: str, role: str = "reviewer") -> None:
        if not subject.strip() or role not in {"reviewer", "admin"}:
            raise ValueError("invalid reviewer roster entry")
        self._members[subject] = role


class ReviewerAuthenticator:
    def __init__(self, secret: str, required: bool = False, ttl_seconds: int = 900, previous_secrets: list[str] | tuple[str, ...] = (), roster: ReviewerRoster | None = None):
        if required and (not secret or "development" in secret):
            raise ValueError("production reviewer authentication requires a managed secret")
        self.secret = secret.encode("utf-8")
        self.validation_secrets = (self.secret, *(item.encode("utf-8") for item in previous_secrets if item))
        self.required = required
        self.ttl_seconds = ttl_seconds
        self.roster = roster
        self._revoked_tokens: set[str] = set()

    def revoke_token(self, token: str) -> None:
        """Revoke a specific bearer token without exposing token material in state."""
        self._revoked_tokens.add(hashlib.sha256(token.encode("utf-8")).hexdigest())

    def issue_for_test(self, subject: str, role: str = "reviewer", expires_at: int | None = None) -> str:
        if not subject.strip() or role not in {"reviewer", "admin"}:
            raise ValueError("invalid reviewer token claims")
        claims = {"sub": subject, "role": role, "exp": expires_at or int(time.time()) + self.ttl_seconds}
        encoded = base64.urlsafe_b64encode(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()).decode().rstrip("=")
        signature = hmac.new(self.secret, encoded.encode(), hashlib.sha256).hexdigest()
        return f"{encoded}.{signature}"

    def authenticate(self, authorization: str | None, required_role: str = "reviewer") -> ReviewerPrincipal | None:
        if not authorization:
            if self.required:
                raise AuthError("reviewer authentication required", 401)
            return None
        if not authorization.startswith("Bearer "):
            raise AuthError("invalid authorization scheme", 401)
        token = authorization[7:].strip()
        token_fingerprint = hashlib.sha256(token.encode("utf-8")).hexdigest()
        if token_fingerprint in self._revoked_tokens:
            raise AuthError("reviewer token revoked", 401)
        try:
            encoded, signature = token.split(".", 1)
            if not any(hmac.compare_digest(signature, hmac.new(key, encoded.encode(), hashlib.sha256).hexdigest()) for key in self.validation_secrets):
                raise AuthError("invalid reviewer token", 401)
            claims = json.loads(base64.urlsafe_b64decode(encoded + "===").decode("utf-8"))
            principal = ReviewerPrincipal(subject=claims["sub"], role=claims["role"], expires_at=int(claims["exp"]))
        except AuthError:
            raise
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AuthError("malformed reviewer token", 401) from exc
        if principal.expires_at < int(time.time()):
            raise AuthError("reviewer token expired", 401)
        if self.roster is not None and self.roster.role_for(principal.subject) != principal.role:
            raise AuthError("reviewer identity is not active", 403)
        if principal.role not in {required_role, "admin"}:
            raise AuthError("reviewer role required", 403)
        return principal
