import asyncio
import time

from honest_agent import HonestAgent
from honest_agent.core.guardrail import HonestGuard
from honest_agent.core.rag import RAGEvidenceBoundary, RetrievalChunk
from honest_agent.rag_workflow import RAGSafetyWorkflow
from honest_agent.schemas.models import Config
from honest_agent.schemas.workflow import DataClassification, EvidenceEnvelope, TrustClass
from honest_agent.sdk import make_request


def chunk():
    now = time.time()
    evidence = EvidenceEnvelope(evidence_id="support-e-1", source_id="support-kb", source_type="knowledge_base", tenant_scope="demo-tenant", content_hash="a" * 64, observed_at=now - 1, expires_at=now + 300, trust_class=TrustClass.TRUSTED, data_classification=DataClassification.INTERNAL, redacted_reference="ref:support-e-1")
    return RetrievalChunk(evidence, "Synthetic return policy: returns are accepted within 30 days.", "internal")


async def main():
    agent = HonestAgent(HonestGuard(Config(trajectory_dir="/tmp/honest-agent-rag-demo", checkpoint_path="/tmp/honest-agent-rag-demo/checkpoints.json")))
    workflow = RAGSafetyWorkflow(agent, RAGEvidenceBoundary("demo-tenant", frozenset({"support-kb"})))
    request = make_request("lookup_return_policy", {"order_id": "synthetic-order-1"}, context="Answer using the cited synthetic support policy")
    result = await workflow.run([chunk()], request, lambda payload: {"order_id": payload["order_id"], "policy": "30 days"}, cited_evidence_ids=["support-e-1"], high_impact=True)
    print({"outcome": result.outcome, "executed": result.executed, "result": result.result})


if __name__ == "__main__":
    asyncio.run(main())
