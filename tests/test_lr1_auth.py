import asyncio
import base64
import hashlib
import hmac
import json
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest

from honest_agent.core.audit import AppendOnlyAuditSink, AuditIntegrityError
from honest_agent.core.auth import ReviewerAuthenticator, ReviewerRoster
from honest_agent.core.guardrail import HonestGuard
from honest_agent.interfaces.webhooks import build_router
from honest_agent.schemas.models import Config, EvaluationRequest


def _runtime(tmp_path, required=True):
    config = Config(
        trajectory_dir=str(tmp_path / "trajectories"),
        checkpoint_path=str(tmp_path / "checkpoints.json"),
        reviewer_auth_secret="test-reviewer-secret",
        require_reviewer_auth=required,
    )
    guard = HonestGuard(config=config)
    auth = ReviewerAuthenticator(config.reviewer_auth_secret, required=config.require_reviewer_auth)
    app = FastAPI()
    app.include_router(build_router(guard, auth))
    return guard, auth, TestClient(app)


def test_missing_reviewer_auth_is_rejected(tmp_path):
    guard, _, client = _runtime(tmp_path)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="ambiguous unknown", tool_name="write_file", tool_input={"path": "x"})))
    response = client.post(f"/approve/{pending.trajectory_id}", json={"reviewer": "spoofed"})
    assert response.status_code == 401


def test_expired_reviewer_token_is_rejected(tmp_path):
    guard, auth, client = _runtime(tmp_path)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="ambiguous unknown", tool_name="write_file", tool_input={"path": "x"})))
    token = auth.issue_for_test("alice", expires_at=int(time.time()) - 1)
    response = client.post(f"/approve/{pending.trajectory_id}", headers={"Authorization": f"Bearer {token}"}, json={"reviewer": "alice"})
    assert response.status_code == 401


def test_reviewer_role_is_required(tmp_path):
    guard, auth, client = _runtime(tmp_path)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="ambiguous unknown", tool_name="write_file", tool_input={"path": "x"})))
    claims = {"sub": "observer", "role": "observer", "exp": int(time.time()) + 900}
    encoded = base64.urlsafe_b64encode(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(b"test-reviewer-secret", encoded.encode(), hashlib.sha256).hexdigest()
    token = f"{encoded}.{signature}"
    response = client.post(f"/approve/{pending.trajectory_id}", headers={"Authorization": f"Bearer {token}"}, json={"reviewer": "observer"})
    assert response.status_code == 403


def test_authenticated_identity_overrides_body_spoof_and_is_persisted(tmp_path):
    guard, auth, client = _runtime(tmp_path)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="ambiguous unknown", tool_name="write_file", tool_input={"path": "x"})))
    token = auth.issue_for_test("alice", role="reviewer")
    response = client.post(f"/approve/{pending.trajectory_id}", headers={"Authorization": f"Bearer {token}"}, json={"reviewer": "spoofed"})
    assert response.status_code == 200
    assert response.json()["reviewer"] == "alice"
    payload = __import__("json").loads(open(pending.trajectory_path).read())
    assert payload["trajectory"][0]["human_checkpoint"]["reviewer"] == "alice"


def test_revoked_token_and_roster_identity_are_rejected():
    roster = ReviewerRoster({"alice": "reviewer"})
    auth = ReviewerAuthenticator("secret", required=True, roster=roster)
    token = auth.issue_for_test("alice")
    assert auth.authenticate(f"Bearer {token}").subject == "alice"
    auth.revoke_token(token)
    with pytest.raises(Exception, match="revoked"):
        auth.authenticate(f"Bearer {token}")
    token = auth.issue_for_test("alice", expires_at=int(time.time()) + 901)
    roster.revoke("alice")
    with pytest.raises(Exception, match="not active"):
        auth.authenticate(f"Bearer {token}")


def test_append_only_audit_sink_verifies_chain_and_redacts(tmp_path):
    sink = AppendOnlyAuditSink(str(tmp_path / "events.jsonl"))
    sink.append("approve", subject="alice", trajectory_id="t-1", policy_version="p-1", details={"api_key": "secret"})
    sink.append("reject", subject="alice", trajectory_id="t-2", policy_version="p-1")
    assert sink.verify()
    assert "secret" not in (tmp_path / "events.jsonl").read_text()
    lines = (tmp_path / "events.jsonl").read_text().splitlines()
    lines[0] = lines[0].replace("approve", "tampered")
    (tmp_path / "events.jsonl").write_text("\n".join(lines) + "\n")
    with pytest.raises(AuditIntegrityError):
        sink.verify()
