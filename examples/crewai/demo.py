import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from honest_agent.core.guardrail import HonestGuard
from honest_agent.schemas.models import EvaluationRequest
from examples.crewai.adapter import CrewAIToolBoundary

async def main():
    adapter = CrewAIToolBoundary(HonestGuard())
    request = EvaluationRequest(tool_name="lookup_customer", context="synthetic customer record", tool_input={"id": "synthetic"})
    result = await adapter.call(request, lambda payload: {"lookup": payload["id"]})
    print(result.status, result.executed, result.result)

if __name__ == "__main__":
    asyncio.run(main())
