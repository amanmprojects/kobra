from __future__ import annotations

from typing import Any

import httpx

from backend.config import settings


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.litellm_master_key}",
        "Content-Type": "application/json",
    }


async def healthcheck() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.litellm_proxy_url}/health/liveliness")
            return response.status_code < 500
    except Exception:
        return False


async def chat_complete(messages: list[dict[str, Any]], model: str | None = None) -> str:
    payload = {"model": model or settings.prompt_model, "messages": messages}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.litellm_proxy_url}/v1/chat/completions",
            json=payload,
            headers=_headers(),
        )
        response.raise_for_status()
        body = response.json()
        return body["choices"][0]["message"]["content"]


async def check_prompt_injection(messages: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {"model": settings.prompt_model, "messages": messages}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.litellm_proxy_url}/v1/chat/completions",
            json=payload,
            headers=_headers(),
        )
        if response.status_code == 400:
            return {"safe": False, "error_body": response.json()}
        response.raise_for_status()
        return {
            "safe": True,
            "response": response.json()["choices"][0]["message"]["content"],
        }

