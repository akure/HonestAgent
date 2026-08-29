from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from honest_agent.core.evaluator import ContextEvaluator
from honest_agent.core.providers import OpenAICompatibleVerifierProvider, ProviderContractError
from honest_agent.interfaces import proxy
from honest_agent.interfaces.upstream import UpstreamClient
from honest_agent.schemas.models import EvaluationRequest, RiskLevel, RecommendedAction, VerifierTier


def test_provider_adapter_parses_structured_response():
    async def run():
        async def handler(request: httpx.Request):
            payload = {"confidence_score": 0.91, "has_sufficient_context": True, "hallucination_risk": "LOW", "reasoning": "grounded", "recommended_action": "PROCEED"}
            return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(payload)}}]})
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        provider = OpenAICompatibleVerifierProvider("https://provider.test/v1/chat/completions", "test-key", "test-model", client)
        request = EvaluationRequest(context="known", tool_name="lookup", tool_input={"id": 1})
        result = await provider.verify(request, ContextEvaluator().evaluate(request.context, request.max_context_tokens, 0.8), VerifierTier.FAST)
        assert result.confidence_score == 0.91
        assert result.recommended_action == RecommendedAction.PROCEED
        await client.aclose()
    asyncio.run(run())


def test_provider_adapter_rejects_malformed_response():
    async def run():
        async def handler(request: httpx.Request):
            return httpx.Response(200, json={"choices": []})
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        provider = OpenAICompatibleVerifierProvider("https://provider.test", "test-key", "test-model", client)
        request = EvaluationRequest(context="known", tool_name="lookup", tool_input={"id": 1})
        try:
            await provider.verify(request, ContextEvaluator().evaluate(request.context, request.max_context_tokens, 0.8), VerifierTier.FAST)
        except ProviderContractError:
            pass
        else:
            raise AssertionError("malformed provider response must fail closed")
        await client.aclose()
    asyncio.run(run())


def test_upstream_client_forwards_payload_once():
    async def run():
        calls = []
        async def handler(request: httpx.Request):
            calls.append(json.loads(request.content))
            return httpx.Response(200, json={"id": "upstream-1", "choices": []})
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        upstream = UpstreamClient("https://upstream.test/v1", client)
        response = await upstream.chat_completions({"model": "x", "messages": []})
        assert response["id"] == "upstream-1"
        assert len(calls) == 1
        await client.aclose()
    asyncio.run(run())


def test_paused_proxy_request_does_not_call_upstream(monkeypatch):
    calls = []
    class FakeUpstream:
        enabled = True
        async def chat_completions(self, payload):
            calls.append(payload)
            return {}
    monkeypatch.setattr(proxy, "upstream", FakeUpstream())
    response = TestClient(proxy.app).post("/v1/chat/completions", json={"model": "x", "messages": [{"role": "user", "content": "unknown dependency"}], "honest_agent": {"tool_name": "db_migrate", "irreversible": True}})
    assert response.status_code == 200
    assert response.json()["honest_agent"]["status"] == "PAUSED"
    assert calls == []
