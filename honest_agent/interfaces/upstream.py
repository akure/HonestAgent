from __future__ import annotations

from typing import Any, Mapping

import httpx

from honest_agent.core.security import SSRFBlocked, validate_transport_url


class UpstreamError(RuntimeError):
    pass


class UpstreamClient:
    def __init__(self, base_url: str | None = None, client: httpx.AsyncClient | None = None, allow_private_network: bool = False, require_tls: bool = False):
        self.base_url = validate_transport_url(
            base_url,
            require_tls=require_tls,
            allow_private=allow_private_network,
            resolve_hostname=client is None,
        ) if base_url else None
        self.client = client or httpx.AsyncClient(timeout=30.0)

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    async def chat_completions(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not self.base_url:
            raise UpstreamError("upstream client is not configured")
        try:
            response = await self.client.post(f"{self.base_url}/chat/completions", json=dict(payload))
            response.raise_for_status()
            return response.json()
        except SSRFBlocked:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            raise UpstreamError(f"upstream request failed: {type(exc).__name__}") from exc
