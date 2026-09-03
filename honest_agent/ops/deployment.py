from __future__ import annotations

import re
from typing import Any, Mapping


class DeploymentConfigurationError(ValueError):
    pass


_COMMERCIAL_MODES = {"source-available", "private-deployment", "hosted", "oem"}
_MANAGED_ENVIRONMENTS = {"staging", "production"}
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def validate_deployment_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate deployment prerequisites without contacting external services.

    This is a packaging gate, not a safety certification or a billing/license
    enforcement mechanism. Secrets are represented only by configuration flags.
    """
    if not isinstance(manifest, Mapping):
        raise DeploymentConfigurationError("deployment manifest must be an object")
    environment = manifest.get("environment")
    mode = manifest.get("commercial_mode", "source-available")
    if environment not in {"development", "test", "staging", "production"}:
        raise DeploymentConfigurationError("environment must be development, test, staging, or production")
    if mode not in _COMMERCIAL_MODES:
        raise DeploymentConfigurationError("unsupported commercial deployment mode")
    managed = environment in _MANAGED_ENVIRONMENTS
    required = ("image_digest", "sbom_reference", "audit_sink", "operator_auth")
    if managed:
        for field in required:
            if not isinstance(manifest.get(field), str) or not manifest[field].strip():
                raise DeploymentConfigurationError(f"{field} is required for managed environments")
        if not _SHA256_RE.fullmatch(manifest["image_digest"]):
            raise DeploymentConfigurationError("managed image_digest must be a sha256 digest")
        if not bool(manifest.get("tls_required")):
            raise DeploymentConfigurationError("TLS is required for managed environments")
        if not bool(manifest.get("managed_secrets")):
            raise DeploymentConfigurationError("managed secrets are required for managed environments")
        if manifest.get("allow_private_upstream"):
            raise DeploymentConfigurationError("private upstream access is not permitted in managed environments")
        side_effect_mode = manifest.get("side_effect_mode", "simulated")
        if side_effect_mode not in {"simulated", "allowlisted"}:
            raise DeploymentConfigurationError("managed side_effect_mode must be simulated or allowlisted")
    else:
        side_effect_mode = manifest.get("side_effect_mode", "simulated")
    return {
        "manifest_version": "std10e-v1",
        "environment": environment,
        "commercial_mode": mode,
        "managed": managed,
        "side_effect_mode": side_effect_mode,
        "protocol_boundary": "honestagent.control.v1",
        "reference_kernel_included": True,
        "enterprise_services_included": mode in {"private-deployment", "hosted", "oem"},
        "billing_enforcement": False,
        "safety_certification": False,
    }


__all__ = ["DeploymentConfigurationError", "validate_deployment_manifest"]
