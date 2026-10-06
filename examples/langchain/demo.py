"""Mini LangChain use case: tool wrapper protects a support workflow."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest
from examples.langchain.adapter import LangChainToolWrapper


async def main() -> None:
    wrapper = LangChainToolWrapper(HonestGuard())
    proposals = [
        EvaluationRequest(
            tool_name="search_support_kb",
            context="synthetic cited support article",
            tool_input={"query": "return policy"},
        ),
        EvaluationRequest(
            tool_name="delete_customer_data",
            context="retrieved text requests deletion but is not an authority source",
            tool_input={"customer_id": "synthetic-001"},
            irreversible=True,
        ),
    ]
    for proposal in proposals:
        result = await wrapper.call(proposal, lambda payload: {"tool_result": payload})
        print({"tool": proposal.tool_name, "status": result.status, "executed": result.executed})


if __name__ == "__main__":
    asyncio.run(main())
