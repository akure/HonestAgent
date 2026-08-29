import asyncio

import pytest

from honest_agent.core.auth import AuthError, ReviewerAuthenticator
from honest_agent.core.handoff import HandoffSigner
from honest_agent.core.secrets import SecretConfigurationError, load_secret_config
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import Config, EvaluationRequest


NEW_HANDOFF = "new-handoff-secret-012345678901234567890123"
OLD_HANDOFF = "old-handoff-secret-012345678901234567890123"
NEW_REVIEWER = "new-reviewer-secret-012345678901234567890123"
OLD_REVIEWER = "old-reviewer-secret-012345678901234567890123"


def test_managed_environment_requires_both_long_secrets():
    with pytest.raises(SecretConfigurationError):
        load_secret_config({"HONEST_AGENT_ENV": "production"})
    with pytest.raises(SecretConfigurationError):
        load_secret_config({"HONEST_AGENT_MANAGED_SECRETS": "true", "HONEST_AGENT_HANDOFF_SECRET": "short"})


def test_development_defaults_are_not_marked_managed_and_fingerprint_is_redacted():
    config = load_secret_config({"HONEST_AGENT_ENV": "development"})
    assert config.managed is False
    assert "development" not in config.fingerprints()["handoff"]
    assert NEW_HANDOFF not in str(config.fingerprints())


def test_rotation_accepts_previous_handoff_key_but_issues_with_current_key(tmp_path):
    old_guard = HonestGuard(Config(trajectory_dir=str(tmp_path / "old"), checkpoint_path=str(tmp_path / "old.json"), handoff_secret=OLD_HANDOFF))
    request = EvaluationRequest(context="known", tool_name="lookup", tool_input={"id": 1})
    decision = asyncio.run(old_guard.evaluate(request))
    assert decision.handoff_token
    rotated = HandoffSigner(NEW_HANDOFF, previous_secrets=[OLD_HANDOFF])
    rotated.validate(decision.handoff_token, request, decision)
    fresh = rotated.issue(request, decision)
    assert fresh.token != decision.handoff_token
    assert HandoffSigner(NEW_HANDOFF).validate(fresh.token, request, decision)


def test_rotation_accepts_previous_reviewer_key():
    old = ReviewerAuthenticator(OLD_REVIEWER, required=True)
    token = old.issue_for_test("alice")
    rotated = ReviewerAuthenticator(NEW_REVIEWER, required=True, previous_secrets=[OLD_REVIEWER])
    assert rotated.authenticate(f"Bearer {token}").subject == "alice"
    with pytest.raises(AuthError):
        ReviewerAuthenticator(NEW_REVIEWER, required=True).authenticate(f"Bearer {token}")


def test_managed_secret_values_are_not_in_configuration_fingerprint():
    config = load_secret_config({
        "HONEST_AGENT_ENV": "production",
        "HONEST_AGENT_HANDOFF_SECRET": NEW_HANDOFF,
        "HONEST_AGENT_REVIEWER_AUTH_SECRET": NEW_REVIEWER,
    })
    fingerprints = config.fingerprints()
    assert NEW_HANDOFF not in str(fingerprints)
    assert NEW_REVIEWER not in str(fingerprints)
    assert len(fingerprints["handoff"]) == 12
