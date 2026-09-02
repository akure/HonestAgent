import asyncio
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from honest_agent.core.auth import AuthError, ReviewerAuthenticator, ReviewerRoster
from honest_agent.core.audit import AppendOnlyAuditSink
from honest_agent.core.guardrail import HonestGuard
from honest_agent.interfaces.webhooks import build_router
from honest_agent.schemas.models import Config, EvaluationRequest


def test_tenant_claim_is_required_and_bound_to_authenticator():
    auth = ReviewerAuthenticator("tenant-secret", required=True, tenant_id="tenant-a")
    token = auth.issue_for_test("alice", tenant_id="tenant-b")
    with pytest.raises(AuthError, match="tenant scope"):
        auth.authenticate(f"Bearer {token}")
    valid = auth.issue_for_test("alice")
    assert auth.authenticate(f"Bearer {valid}").tenant_id == "tenant-a"


def test_subject_revocation_invalidates_all_tokens():
    auth = ReviewerAuthenticator("reviewer-secret", required=True)
    token = auth.issue_for_test("alice")
    assert auth.authenticate(f"Bearer {token}").subject == "alice"
    auth.revoke_subject("alice")
    with pytest.raises(AuthError, match="identity revoked"):
        auth.authenticate(f"Bearer {token}")


def test_expiry_boundary_is_fail_closed():
    auth = ReviewerAuthenticator("reviewer-secret", required=True)
    token = auth.issue_for_test("alice", expires_at=int(time.time()))
    with pytest.raises(AuthError, match="expired"):
        auth.authenticate(f"Bearer {token}")


def test_roster_revocation_remains_distinct_from_token_revocation():
    roster = ReviewerRoster({"alice": "reviewer"})
    auth = ReviewerAuthenticator("reviewer-secret", required=True, roster=roster)
    token = auth.issue_for_test("alice")
    roster.revoke("alice")
    with pytest.raises(AuthError, match="not active"):
        auth.authenticate(f"Bearer {token}")


def test_webhook_rejects_wrong_tenant_and_audits_authenticated_role(tmp_path):
    config = Config(
        trajectory_dir=str(tmp_path / "trajectories"),
        checkpoint_path=str(tmp_path / "checkpoints.json"),
        reviewer_auth_secret="reviewer-secret",
        require_reviewer_auth=True,
    )
    guard = HonestGuard(config=config)
    auth = ReviewerAuthenticator(config.reviewer_auth_secret, required=True, tenant_id="tenant-a")
    sink = AppendOnlyAuditSink(str(tmp_path / "audit.jsonl"))
    app = FastAPI()
    app.include_router(build_router(guard, auth, sink, tenant_id="tenant-a"))
    client = TestClient(app)
    pending = asyncio.run(guard.evaluate(EvaluationRequest(context="ambiguous unknown", tool_name="write_file", tool_input={"path": "x"})))

    wrong_tenant = auth.issue_for_test("alice", tenant_id="tenant-b")
    rejected = client.post(
        f"/approve/{pending.trajectory_id}",
        headers={"Authorization": f"Bearer {wrong_tenant}"},
        json={"reviewer": "spoofed"},
    )
    assert rejected.status_code == 403

    valid = auth.issue_for_test("alice", role="reviewer")
    approved = client.post(
        f"/approve/{pending.trajectory_id}",
        headers={"Authorization": f"Bearer {valid}"},
        json={"reviewer": "spoofed"},
    )
    assert approved.status_code == 200
    assert sink.verify()
    event = sink.path.read_text().splitlines()[0]
    assert '"subject": "alice"' in event
    assert '"role": "reviewer"' in event
    assert '"tenant_id": "tenant-a"' in event
