import pytest

from honest_agent.ops.deployment import DeploymentConfigurationError, validate_deployment_manifest


_DIGEST = "sha256:" + "a" * 64


def test_development_manifest_is_credential_free_and_separates_boundaries():
    result = validate_deployment_manifest({"environment": "development"})
    assert result["managed"] is False
    assert result["protocol_boundary"] == "honestagent.control.v1"
    assert result["billing_enforcement"] is False
    assert result["safety_certification"] is False


def test_managed_manifest_requires_digest_sbom_audit_operator_tls_and_secrets():
    base = {
        "environment": "production",
        "image_digest": _DIGEST,
        "sbom_reference": "sbom://release-1",
        "audit_sink": "immutable://audit",
        "operator_auth": "oidc://operators",
        "tls_required": True,
        "managed_secrets": True,
        "side_effect_mode": "simulated",
    }
    result = validate_deployment_manifest(base)
    assert result["managed"] is True
    assert result["enterprise_services_included"] is False
    for field in ("image_digest", "sbom_reference", "audit_sink", "operator_auth"):
        invalid = dict(base)
        invalid.pop(field)
        with pytest.raises(DeploymentConfigurationError, match=field):
            validate_deployment_manifest(invalid)


def test_managed_manifest_rejects_unsafe_transport_secrets_and_side_effects():
    base = {
        "environment": "staging",
        "image_digest": _DIGEST,
        "sbom_reference": "sbom://release-1",
        "audit_sink": "immutable://audit",
        "operator_auth": "oidc://operators",
        "tls_required": True,
        "managed_secrets": True,
        "side_effect_mode": "simulated",
    }
    for change, message in [
        ({"tls_required": False}, "TLS"),
        ({"managed_secrets": False}, "managed secrets"),
        ({"allow_private_upstream": True}, "private upstream"),
        ({"side_effect_mode": "unrestricted"}, "side_effect_mode"),
        ({"image_digest": "latest"}, "image_digest"),
    ]:
        invalid = {**base, **change}
        with pytest.raises(DeploymentConfigurationError, match=message):
            validate_deployment_manifest(invalid)


def test_unknown_modes_and_malformed_manifests_fail_closed():
    with pytest.raises(DeploymentConfigurationError):
        validate_deployment_manifest([])
    with pytest.raises(DeploymentConfigurationError, match="commercial"):
        validate_deployment_manifest({"environment": "production", "commercial_mode": "free-unrestricted"})
