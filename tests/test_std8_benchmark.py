import json

from honest_agent.std8_benchmark import CASES, run_benchmark


def test_benchmark_reports_baseline_and_controlled_metrics(tmp_path):
    output = tmp_path / "std8.json"
    result = run_benchmark(output)
    assert output.exists()
    assert result["schema"] == "honestagent.std8.benchmark.v1"
    assert result["evidence_class"] == "local_synthetic"
    assert result["provenance"]["network"] is False
    assert result["provenance"]["credentials"] is False
    assert result["cases"] == len(CASES)
    assert result["metrics"]["baseline_false_proceeds"] > result["metrics"]["controlled_false_proceeds"]
    assert result["metrics"]["controlled_false_pauses"] == 0
    assert result["metrics"]["controlled_accuracy"] == 1.0
    assert json.loads(output.read_text())["schema"] == "honestagent.std8.benchmark.v1"


def test_benchmark_is_repeatable_in_outcomes(tmp_path):
    first = run_benchmark(tmp_path / "one.json")
    second = run_benchmark(tmp_path / "two.json")
    assert [(row["id"], row["controlled_status"]) for row in first["results"]] == [(row["id"], row["controlled_status"]) for row in second["results"]]
    assert first["metrics"]["controlled_accuracy"] == second["metrics"]["controlled_accuracy"]
