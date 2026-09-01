from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from honest_agent.core.guardrail import HonestGuard
from honest_agent.sdk import HonestAgent, make_request
from honest_agent.schemas.models import Config

_STARTER = '''from honest_agent import HonestAgent, make_request

agent = HonestAgent()
request = make_request("lookup", {"id": "synthetic-1"})
# await agent.check(request) or await agent.invoke(request, your_tool)
'''


def _init(path: Path, force: bool) -> int:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite {path}; pass --force to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_STARTER, encoding="utf-8")
    print(f"created {path}")
    return 0


async def _demo() -> dict[str, object]:
    with TemporaryDirectory(prefix="honest-agent-demo-") as directory:
        guard = HonestAgent(HonestGuard(Config(trajectory_dir=directory, checkpoint_path=f"{directory}/checkpoints.json")))
        request = make_request("lookup", {"id": "synthetic-1"}, context="Synthetic local demo record")
        result = await guard.invoke(request, lambda payload: {"found": payload["id"]})
        return {"status": result.status, "executed": result.executed, "result": result.result, "credential_free": True}


def main() -> int:
    parser = argparse.ArgumentParser(prog="honest-agent", description="HonestAgent safe Python workflow helpers")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="write a minimal guarded-tool starter")
    init.add_argument("path", nargs="?", type=Path, default=Path("honest_agent_app.py"))
    init.add_argument("--force", action="store_true")
    commands.add_parser("demo", help="run an offline synthetic guarded-tool demo")
    args = parser.parse_args()
    if args.command == "init":
        return _init(args.path, args.force)
    print(json.dumps(asyncio.run(_demo()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
