import json
from pathlib import Path

from honest_agent.conformance import run_manifest

MANIFEST = Path(__file__).parents[1] / "fixtures" / "conformance" / "v1" / "manifest.json"


def test_v1_golden_manifest_is_conformant_and_machine_readable():
    result = run_manifest(MANIFEST)
    assert result["conformant"] is True
    assert result["failed"] == 0
    assert result["passed"] == 8
    assert all(item["conformant"] is True for item in result["results"])


def test_v1_golden_manifest_is_deterministic():
    assert run_manifest(MANIFEST) == run_manifest(MANIFEST)


def test_runner_reports_fixture_mismatch_without_authorizing_it(tmp_path):
    manifest = json.loads(MANIFEST.read_text())
    manifest["cases"][0]["expected"]["value"] = "2.0"
    altered = tmp_path / "manifest.json"
    altered.write_text(json.dumps(manifest))
    result = run_manifest(altered)
    assert result["conformant"] is False
    assert result["failed"] == 1
    assert result["results"][0]["value"] == "1.1"
