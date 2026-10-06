"""Mini AutoGen/AG2 use case: function proposal versus protected mutation."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest
from examples.autogen.adapter import AutoGenFunctionTool


async def main() -> None:
    function_tool = AutoGenFunctionTool(HonestGuard())
    proposals = [
        EvaluationRequest(
            agent_id="autogen-support-agent",
            tool_name="get_order_status",
            context="synthetic order inquiry",
            tool_input={"order_id": "synthetic-order-001"},
        ),
        EvaluationRequest(
            agent_id="autogen-support-agent",
            tool_name="change_shipping_address",
            context="address change proposed; identity and approval are absent",
            tool_input={"order_id": "synthetic-order-001", "address": "synthetic"},
            irreversible=True,
        ),
    ]
    for proposal in proposals:
        result = await function_tool.call(proposal, lambda payload: {"tool_result": payload})
        print({"tool": proposal.tool_name, "status": result.status, "executed": result.executed})


if __name__ == "__main__":
    asyncio.run(main())
