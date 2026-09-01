import asyncio
import json

import pytest

from honest_agent.cli import main
from honest_agent.core.guardrail import HonestGuard
from honest_agent.sdk import GuardBlocked, HonestAgent, make_request
from honest_agent.schemas.models import Config, DecisionStatus


def _agent(tmp_path, **overrides):
    values = {"trajectory_dir": str(tmp_path / "traces"), "checkpoint_path": str(tmp_path / "checkpoints.json")}
    values.update(overrides)
    return HonestAgent(HonestGuard(Config(**values)))


def test_make_request_and_invoke_use_existing_guard_boundary(tmp_path):
    agent = _agent(tmp_path)
    request = make_request("lookup", {"id": "synthetic-1"}, context="Synthetic local lookup")
    result = asyncio.run(agent.invoke(request, lambda payload: payload["id"]))
    assert result.status == DecisionStatus.PROCEED.value
    assert result.executed is True
    assert result.result == "synthetic-1"


def test_protect_decorator_blocks_after_configured_cap(tmp_path):
    agent = _agent(tmp_path, max_checks=1)
    calls = []

    @agent.protect("lookup", context="Synthetic local lookup")
    def lookup(**kwargs):
        calls.append(kwargs)
        return "ok"

    assert asyncio.run(lookup(id="first")) == "ok"
    with pytest.raises(GuardBlocked) as blocked:
        asyncio.run(lookup(id="second"))
    assert blocked.value.decision.status == DecisionStatus.CAP_EXCEEDED
    assert len(calls) == 1


def test_cli_init_is_non_destructive_and_demo_is_credential_free(tmp_path, monkeypatch, capsys):
    target = tmp_path / "app.py"
    monkeypatch.setattr("sys.argv", ["honest-agent", "init", str(target)])
    assert main() == 0
    original = target.read_text()
    monkeypatch.setattr("sys.argv", ["honest-agent", "init", str(target)])
    with pytest.raises(SystemExit):
        main()
    assert target.read_text() == original

    monkeypatch.setattr("sys.argv", ["honest-agent", "demo"])
    assert main() == 0
    output = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert output["credential_free"] is True
    assert output["executed"] is True
