# STD-8 Independent Reproduction Protocol

## Purpose

Reproduce the local synthetic benchmark from a clean checkout and distinguish baseline comparison from production evidence. The benchmark uses identical fixed cases for an intentionally unguarded baseline and the HonestAgent controlled path.

## Clean-checkout command

```bash
git clone https://github.com/akure/HonestAgent.git
cd HonestAgent
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m pip install pytest
PYTHONPATH=. python scripts/run_std8_benchmark.py --output /tmp/std8-benchmark.json
python -m json.tool /tmp/std8-benchmark.json
python -m pytest -q tests/test_std8_benchmark.py
```

The command requires no API key, provider credential, vector database, network call from the benchmark, or live side effect. The clone and package installation naturally require network access; the benchmark itself records `network: false` for its execution path.

## Review protocol

An independent reviewer should record the commit tested, Python version, platform, exact command, output artifact checksum, and any environment changes. The reviewer should confirm that both baseline and controlled rows use the same seven fixed cases, that expected statuses are visible, and that no tool function is called by the benchmark. Re-run twice and compare case IDs, expected statuses, and controlled statuses; latency may vary.

## Result boundary

The checked-in result is **local synthetic evidence**. It reports baseline false proceeds, controlled false proceeds, controlled false pauses, accuracy, and mean controlled latency. The measured run produced baseline false proceeds `4`, controlled false proceeds `0`, controlled false pauses `0`, and controlled accuracy `1.0` across 7 cases.

These results do not establish customer, regulatory, independent third-party, production, provider, distributed-worker, or framework compatibility claims. Any independent reviewer should publish a separate signed reproduction record rather than editing this artifact.
