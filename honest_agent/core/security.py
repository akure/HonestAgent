from __future__ import annotations

import ipaddress
import socket
from typing import Any, Callable, Mapping
from urllib.parse import urlparse


SENSITIVE_KEY_FRAGMENTS = ("password", "passwd", "secret", "token", "api_key", "apikey", "authorization", "cookie", "credential")
REDACTED = "[REDACTED]"


class SecurityConfigurationError(ValueError):
    pass


class SSRFBlocked(ValueError):
    pass


def _is_special_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return any((address.is_private, address.is_loopback, address.is_link_local, address.is_multicast, address.is_unspecified, address.is_reserved))


def validate_outbound_url(
    url: str,
    allow_private: bool = False,
    *,
    resolve_hostname: bool = False,
    resolver: Callable[..., list[tuple[Any, ...]]] = socket.getaddrinfo,
) -> str:
    """Reject literal and DNS-resolved private addresses before outbound use."""
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
    if address is not None and not allow_private and _is_special_address(address):
        raise SSRFBlocked("private or special-use outbound address is not permitted")
    if address is None and resolve_hostname and not allow_private:
        try:
            resolved = resolver(hostname, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
        except OSError as exc:
            raise SSRFBlocked("outbound hostname could not be resolved") from exc
        addresses = {str(result[4][0]) for result in resolved if result[4]}
        if not addresses:
            raise SSRFBlocked("outbound hostname resolved to no addresses")
        for value in addresses:
            try:
                resolved_address = ipaddress.ip_address(value)
            except ValueError as exc:
                raise SSRFBlocked("outbound hostname returned an invalid address") from exc
            if _is_special_address(resolved_address):
                raise SSRFBlocked("outbound hostname resolves to a private or special-use address")
    return url.rstrip("/")


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): REDACTED if any(fragment in str(key).lower() for fragment in SENSITIVE_KEY_FRAGMENTS) else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return [redact(item) for item in value]
    return value


def validate_deployment_security(environment: str, allow_private_upstream: bool, max_payload_bytes: int, *, require_tls: bool = False) -> None:
    if max_payload_bytes <= 0:
        raise SecurityConfigurationError("max payload size must be positive")
    if environment.lower() in {"production", "staging"} and allow_private_upstream:
        raise SecurityConfigurationError("private upstream access requires an explicit non-production deployment")
    if environment.lower() in {"production", "staging"} and not require_tls:
        raise SecurityConfigurationError("managed deployments must require TLS for upstream links")


def validate_transport_url(url: str, *, require_tls: bool = False, allow_private: bool = False, resolve_hostname: bool = False) -> str:
    """Apply URL and transport policy at the final client boundary."""
    if require_tls and urlparse(url).scheme != "https":
        raise SecurityConfigurationError("TLS is required for this upstream connection")
    validated = validate_outbound_url(url, allow_private, resolve_hostname=resolve_hostname)
    return validated
