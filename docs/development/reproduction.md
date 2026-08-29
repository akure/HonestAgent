# Honest Agent — Reproduction Guide

## Prerequisites

Use Python 3.12 or newer. The project contains only synthetic fixtures in `tests/fixtures.py`; no private data, model credentials, or external service is required. Runtime and benchmark cost are effectively local compute only.

## Setup

```bash
git clone <submission-repository-url>
cd honest-agent
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Run the baseline

The baseline is the transparent pass-through executor. It performs no guard checks and is run as part of the shared evaluation command:

```bash
PYTHONPATH=. python3 tests/benchmark.py
```

The expected baseline field is `"baseline_unsafe_caught": 0`.

## Run the solution tests

```bash
PYTHONPATH=. python3 -m pytest -q
```

Expected output is 80 passing tests (the exact progress formatting may vary).

## Run the solution and evaluation

```bash
PYTHONPATH=. python3 tests/benchmark.py
cat benchmark_results.json
```

Expected key output from the verified run is:

```json
{
  "cases": 12,
  "baseline_unsafe_caught": 0,
  "solution_unsafe_caught": 10,
  "unsafe_cases": 10,
  "unsafe_action_catch_rate": 1.0
}
```

`mean_guard_latency_ms` is measured on the local machine and should remain below the 25 ms target in the default deterministic path. The exact value varies with hardware.

## Run the HTTP gateway

```bash
uvicorn honest_agent.interfaces.proxy:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
curl -s http://127.0.0.1:8000/v1/guard \
  -H 'content-type: application/json' \
  -d '{"context":"missing dependency; maybe unknown","tool_name":"write_file","tool_input":{"path":"unknown"}}'
```

The response must have `decision.status` equal to `PAUSED` and include a `trajectory_id`. No file is written. The trajectory JSON is placed under `trajectories/`.

## Versions and limitations

The pinned dependencies are FastAPI 0.137.1, Starlette 1.6.0 (resolved transitively), Uvicorn 0.34.0, Pydantic 2.10.4, pytest 9.0.3, and HTTPX 0.28.1. The prototype does not call Groq, Gemini, Ollama, or a real executor by default; those are intentionally optional extension points so the benchmark is deterministic and credential-free.
