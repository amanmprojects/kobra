from __future__ import annotations

import asyncio
import base64
import re
from typing import Any
from urllib.parse import urlencode

import httpx

from backend.config import settings


GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


class GmailService:
    def build_authorization_url(self) -> str:
        params = {
            "client_id": settings.gmail_client_id,
            "redirect_uri": settings.gmail_redirect_uri,
            "response_type": "code",
            "scope": GMAIL_SCOPE,
            "access_type": "online",
            "prompt": "consent",
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    async def exchange_code(self, code: str) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.gmail_client_id,
                    "client_secret": settings.gmail_client_secret,
                    "redirect_uri": settings.gmail_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        response.raise_for_status()
        return response.json()["access_token"]

    async def fetch_emails(self, access_token: str, max_results: int = 20) -> list[dict[str, Any]]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                params={"maxResults": max_results, "labelIds": "INBOX"},
                headers=headers,
            )
            response.raise_for_status()
            refs = response.json().get("messages", [])
            tasks = [
                self._fetch_message_detail(client, headers, ref["id"])
                for ref in refs
            ]
            details = await asyncio.gather(*tasks)
        emails = []
        for detail in details:
            if detail is not None:
                emails.append(self._parse_message(detail))
        return emails

    async def _fetch_message_detail(self, client: httpx.AsyncClient, headers: dict[str, str], message_id: str) -> dict[str, Any] | None:
        try:
            detail = await client.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}",
                params={"format": "full"},
                headers=headers,
            )
            detail.raise_for_status()
            return detail.json()
        except Exception:
            return None

    def _parse_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {item["name"].lower(): item["value"] for item in payload.get("payload", {}).get("headers", [])}
        body = self._extract_plain_text(payload.get("payload", {}))
        urls = list(dict.fromkeys(re.findall(r"https?://[^\s<>'\"\\]+", body)))[:5]
        sender = headers.get("from", "")
        sender_domain = sender.split("@")[-1].strip(">").lower() if "@" in sender else ""
        return {
            "id": payload["id"],
            "subject": headers.get("subject", "(no subject)"),
            "sender": sender,
            "sender_domain": sender_domain,
            "received_at": headers.get("date", ""),
            "snippet": payload.get("snippet", ""),
            "body": body[:4000],
            "urls": urls,
        }

    def _extract_plain_text(self, payload: dict[str, Any]) -> str:
        if payload.get("mimeType") == "text/plain":
            return self._decode_b64(payload.get("body", {}).get("data", ""))
        for part in payload.get("parts", []) or []:
            if part.get("mimeType") == "text/plain":
                return self._decode_b64(part.get("body", {}).get("data", ""))
        if payload.get("body", {}).get("data"):
            return self._decode_b64(payload["body"]["data"])
        return ""

    def _decode_b64(self, data: str) -> str:
        if not data:
            return ""
        missing = (-len(data)) % 4
        return base64.urlsafe_b64decode(data + ("=" * missing)).decode("utf-8", errors="ignore")
