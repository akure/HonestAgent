"""Mini LangGraph use case: support state graph at a guarded tool node."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest
from examples.langgraph.adapter import LangGraphGuardNode


async def main() -> None:
    adapter = LangGraphGuardNode(HonestGuard())
    proposals = [
        EvaluationRequest(
            tool_name="lookup_customer",
            context="synthetic support ticket",
            tool_input={"customer_id": "synthetic-001"},
        ),
        EvaluationRequest(
            tool_name="issue_refund",
            context="refund requested; no authenticated reviewer approval",
            tool_input={"customer_id": "synthetic-001", "amount": 25},
            irreversible=True,
        ),
    ]
    for proposal in proposals:
        result = await adapter.call(proposal, lambda payload: {"tool_result": payload})
        print({"tool": proposal.tool_name, "status": result.status, "executed": result.executed})


if __name__ == "__main__":
    asyncio.run(main())
