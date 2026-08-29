import asyncio
import base64
import hashlib
import hmac
import json
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient

from honest_agent.core.auth import ReviewerAuthenticator
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
