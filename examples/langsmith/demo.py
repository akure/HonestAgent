"""Offline LangSmith observability example.

Use case: a support agent proposes a customer lookup and then proposes a
refund. HonestAgent allows the read-only lookup and pauses the irreversible
refund. The trace records both decisions without sending data to a service.
"""

import asyncio
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).parents[2]))

from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest
from examples.langgraph.adapter import LangGraphGuardNode
from examples.langsmith.adapter import LocalTraceSink, langsmith_metadata


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="honestagent-langsmith-") as directory:
        sink = LocalTraceSink(Path(directory) / "trace.jsonl")
        adapter = LangGraphGuardNode(HonestGuard())

        proposals = [
            EvaluationRequest(
                tool_name="lookup_customer",
                context="synthetic support ticket",
                tool_input={"customer_id": "synthetic-001"},
            ),
            EvaluationRequest(
                tool_name="issue_refund",
                context="customer requests a refund; reviewer approval is absent",
                tool_input={"customer_id": "synthetic-001", "amount": 25},
                irreversible=True,
            ),
        ]
        for proposal in proposals:
            result = await adapter.call(proposal, lambda payload: {"accepted": payload})
            record = sink.record(result, framework="langgraph+langsmith", tool_name=proposal.tool_name)
            print(langsmith_metadata(record))


if __name__ == "__main__":
    asyncio.run(main())
