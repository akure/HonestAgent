from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class ProtocolError(ValueError):
    """Raised when a protocol version or extension cannot be safely interpreted."""


@dataclass(frozen=True)
class ProtocolVersion:
    major: int
    minor: int


class ExtensionClass(str, Enum):
    INFORMATIONAL = "informational"
    RESTRICTIVE = "restrictive"
    SECURITY_RELEVANT = "security_relevant"


_VERSION_RE = re.compile(r"^(\d+)\.(\d+)$")
_EXTENSION_RE = re.compile(r"^x-[a-z0-9][a-z0-9.-]*:[a-z][a-z0-9.-]{0,63}$")


def parse_version(value: str) -> ProtocolVersion:
    if not isinstance(value, str):
        raise ProtocolError("protocol version must be a string")
    match = _VERSION_RE.fullmatch(value)
    if match is None:
        raise ProtocolError("protocol version must use major.minor form")
    major, minor = (int(part) for part in match.groups())
    return ProtocolVersion(major=major, minor=minor)


def negotiate_version(peer_versions: list[str] | tuple[str, ...], *, supported_major: int = 1, supported_minor: int = 0) -> str:
    """Choose the highest explicitly supported minor version; never silently downgrade major versions."""
    candidates = [parse_version(value) for value in peer_versions]
    compatible = [version for version in candidates if version.major == supported_major and version.minor <= supported_minor]
    if not compatible:
        raise ProtocolError("no compatible protocol version")
    selected = max(compatible, key=lambda version: version.minor)
    return f"{selected.major}.{selected.minor}"


def validate_extension(name: str, classification: ExtensionClass | str) -> str:
    if _EXTENSION_RE.fullmatch(name) is None:
        raise ProtocolError("extension must be a namespaced x-authority:name key")
    try:
        kind = ExtensionClass(classification)
    except ValueError as exc:
        raise ProtocolError("unknown extension classification is not safe") from exc
    return kind.value


def require_known_major(value: str, *, supported_major: int = 1) -> ProtocolVersion:
    version = parse_version(value)
    if version.major != supported_major:
        raise ProtocolError("unsupported protocol major version")
    return version
