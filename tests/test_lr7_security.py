import json

import pytest

from honest_agent.core.logger import TrajectoryLogger
from honest_agent.core.security import SSRFBlocked, SecurityConfigurationError, redact, validate_deployment_security, validate_outbound_url
from honest_agent.interfaces.upstream import UpstreamClient
from honest_agent.schemas.models import ActionClass, Config, DecisionStatus, EvaluationRequest, GuardDecision, RiskLevel, RecommendedAction, VerifierTier


def test_ssrf_blocks_local_private_and_credential_urls():
    for url in ("http://127.0.0.1:8080", "http://10.0.0.1", "http://localhost/admin", "http://user:pass@example.com"):
        with pytest.raises(SSRFBlocked):
            validate_outbound_url(url)
    assert validate_outbound_url("https://api.example.com/v1") == "https://api.example.com/v1"


def test_upstream_constructor_applies_ssrf_policy():
    with pytest.raises(SSRFBlocked):
        UpstreamClient("http://169.254.169.254/latest/meta-data")
    assert UpstreamClient("http://127.0.0.1:8080", allow_private_network=True).enabled


def test_redaction_is_recursive_and_preserves_non_sensitive_shape():
    payload = {"user": "alice", "details": {"api_key": "secret", "nested": [{"password": "pw"}]}, "count": 2}
    redacted = redact(payload)
    assert redacted["user"] == "alice"
    assert redacted["details"]["api_key"] == "[REDACTED]"
    assert redacted["details"]["nested"][0]["password"] == "[REDACTED]"
    assert redacted["count"] == 2


def test_trajectory_logger_redacts_sensitive_tool_input(tmp_path):
    request = EvaluationRequest(tool_name="lookup", tool_input={"account": "a-1", "authorization": "Bearer secret"})
    decision = GuardDecision(status=DecisionStatus.PROCEED, confidence_score=0.9, verifier_tier=VerifierTier.FAST, hallucination_risk=RiskLevel.LOW, action_class=ActionClass.READ_ONLY, reasoning="ok", recommended_action=RecommendedAction.PROCEED, action_taken="PROCEEDED")
    path = TrajectoryLogger(str(tmp_path)).write(request, decision)
    body = json.loads(path.read_text())
    assert body["trajectory"][0]["tool_call"]["input"]["authorization"] == "[REDACTED]"
    assert "Bearer secret" not in path.read_text()


def test_deployment_security_rejects_private_upstream_in_managed_environment():
    with pytest.raises(SecurityConfigurationError):
        validate_deployment_security("production", True, 1_000_000)
    validate_deployment_security("production", False, 1_000_000)
    with pytest.raises(SecurityConfigurationError):
        validate_deployment_security("development", False, 0)
