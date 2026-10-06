"""Mini CrewAI use case: researcher proposes lookup and outbound contact."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest
from examples.crewai.adapter import CrewAIToolBoundary


async def main() -> None:
    boundary = CrewAIToolBoundary(HonestGuard())
    proposals = [
        EvaluationRequest(
            agent_id="researcher-agent",
            tool_name="read_account_context",
            context="synthetic account research",
            tool_input={"account_id": "synthetic-001"},
        ),
        EvaluationRequest(
            agent_id="outreach-agent",
            tool_name="send_customer_message",
            context="draft exists; recipient and reviewer approval are not verified",
            tool_input={"recipient": "synthetic@example.test", "body": "draft only"},
            irreversible=True,
        ),
    ]
    for proposal in proposals:
        result = await boundary.call(proposal, lambda payload: {"tool_result": payload})
        print({"tool": proposal.tool_name, "status": result.status, "executed": result.executed})


if __name__ == "__main__":
    asyncio.run(main())
