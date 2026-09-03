from pathlib import Path

import pytest

from honest_agent.ops.release_packaging import source_manifest_hash, verify_release_inputs


def test_release_inputs_verify_required_files_and_deterministic_source_hash():
    root = Path(__file__).resolve().parents[1]
    report = verify_release_inputs(root)
    assert report["required_files"]["pass"] is True
    assert report["source_manifest_sha256"] == source_manifest_hash(root)
    assert report["dockerfile_safety"] == {
        "non_root_user": True,
        "pinned_dependency_manifest": True,
        "no_privileged_runtime_user": True,
    }
    assert report["claims"] == {
        "production_ready": False,
        "safety_certified": False,
        "commercial_entitlement": False,
    }


def test_missing_release_input_fails_hash_and_is_reported(tmp_path):
    (tmp_path / "Dockerfile").write_text("USER honestagent\n")
    report = verify_release_inputs(tmp_path)
    assert report["required_files"]["pass"] is False
    assert report["source_manifest_sha256"] is None
    with pytest.raises(FileNotFoundError):
        source_manifest_hash(tmp_path)


def test_unavailable_packaging_tools_are_not_reported_as_pass():
    report = verify_release_inputs(Path(__file__).resolve().parents[1])
    assert report["image_build"] in {"NOT_RUN", "AVAILABLE_NOT_RUN"}
    assert report["sbom"] in {"NOT_RUN", "AVAILABLE_NOT_RUN"}
    assert report["vulnerability_scan"] in {"NOT_RUN", "AVAILABLE_NOT_RUN"}
    assert all(value is False for value in report["claims"].values())
