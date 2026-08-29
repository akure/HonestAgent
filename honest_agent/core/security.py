from __future__ import annotations

import ipaddress
from typing import Any, Mapping
from urllib.parse import urlparse


SENSITIVE_KEY_FRAGMENTS = ("password", "passwd", "secret", "token", "api_key", "apikey", "authorization", "cookie", "credential")
REDACTED = "[REDACTED]"


class SecurityConfigurationError(ValueError):
    pass


class SSRFBlocked(ValueError):
    pass


def validate_outbound_url(url: str, allow_private: bool = False) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
        raise SSRFBlocked("outbound URL must use http(s) without embedded credentials")
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if not hostname or hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".localhost"):
        raise SSRFBlocked("local hostnames are not permitted")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not allow_private and (address.is_private or address.is_loopback or address.is_link_local or address.is_multicast or address.is_unspecified or address.is_reserved):
        raise SSRFBlocked("private or special-use outbound address is not permitted")
    return url.rstrip("/")


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): REDACTED if any(fragment in str(key).lower() for fragment in SENSITIVE_KEY_FRAGMENTS) else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return [redact(item) for item in value]
    return value


def validate_deployment_security(environment: str, allow_private_upstream: bool, max_payload_bytes: int) -> None:
    if max_payload_bytes <= 0:
        raise SecurityConfigurationError("max payload size must be positive")
    if environment.lower() in {"production", "staging"} and allow_private_upstream:
        raise SecurityConfigurationError("private upstream access requires an explicit non-production deployment")
