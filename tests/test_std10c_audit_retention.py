from concurrent.futures import ThreadPoolExecutor

import pytest

from honest_agent.core.audit import AppendOnlyAuditSink, AuditIntegrityError


def test_concurrent_append_preserves_hash_chain_and_retrieves_by_scope(tmp_path):
    sink = AppendOnlyAuditSink(str(tmp_path / "events.jsonl"))
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda index: sink.append("approve", subject=f"user-{index}", trajectory_id="run-1", policy_version="v1"), range(32)))
    assert sink.verify()
    records = sink.retrieve(trajectory_id="run-1", limit=100)
    assert len(records) == 32
    assert len({record["hash"] for record in records}) == 32


def test_retention_filters_retrieval_without_deleting_immutable_records(tmp_path):
    now = [1000.0]
    sink = AppendOnlyAuditSink(str(tmp_path / "events.jsonl"), retention_seconds=60, clock=lambda: now[0])
    sink.append("old", subject="alice", trajectory_id="run-old", policy_version="v1")
    now[0] = 1061.0
    sink.append("new", subject="alice", trajectory_id="run-new", policy_version="v1")
    assert [record["event"] for record in sink.retrieve(subject="alice")] == ["new"]
    assert len(sink.retrieve(subject="alice", since=0, limit=10)) == 2
    assert sink.verify()


def test_malformed_or_tampered_audit_record_fails_closed(tmp_path):
    path = tmp_path / "events.jsonl"
    sink = AppendOnlyAuditSink(str(path))
    sink.append("approve", subject="alice", trajectory_id="run-1", policy_version="v1")
    path.write_text(path.read_text() + "not-json\n")
    with pytest.raises(AuditIntegrityError, match="malformed"):
        sink.verify()
    with pytest.raises(AuditIntegrityError, match="malformed"):
        sink.retrieve()


def test_audit_append_rejects_missing_identity_fields(tmp_path):
    sink = AppendOnlyAuditSink(str(tmp_path / "events.jsonl"))
    with pytest.raises(ValueError):
        sink.append("approve", subject="", trajectory_id="run-1", policy_version="v1")
    with pytest.raises(ValueError):
        sink.append("approve", subject="alice", trajectory_id="run-1", policy_version="")
    with pytest.raises(ValueError):
        AppendOnlyAuditSink(str(tmp_path / "other.jsonl"), retention_seconds=0)
