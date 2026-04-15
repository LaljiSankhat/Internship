"""WhatsApp adapter — receives messages via a FastAPI webhook (Meta Cloud API)."""

from __future__ import annotations

import logging
import time
import uuid

import httpx
from fastapi import FastAPI, Request, Response

from openclaw.agent import Agent
from openclaw.config import OpenClawConfig
from openclaw.models import ChannelKind, InboundMessage

logger = logging.getLogger("openclaw.adapters.whatsapp")


class WhatsAppAdapter:
    """Webhook-based WhatsApp integration via Meta Cloud API."""

    def __init__(self, agent: Agent, config: OpenClawConfig, app: FastAPI) -> None:
        self.agent = agent
        self.config = config
        wa = config.whatsapp
        if not wa or not wa.api_token:
            raise ValueError("WHATSAPP_API_TOKEN is required for the WhatsApp adapter")
        self._api_token = wa.api_token
        self._phone_id = wa.phone_number_id
        self._verify_token = wa.verify_token

        # Mount routes
        app.get("/webhook/whatsapp")(self._verify)
        app.post("/webhook/whatsapp")(self._receive)

    # ── webhook verification ─────────────────────────────────────

    async def _verify(self, request: Request) -> Response:
        params = request.query_params
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        if mode == "subscribe" and token == self._verify_token:
            return Response(content=challenge, media_type="text/plain")
        return Response(status_code=403)

    # ── receive messages ─────────────────────────────────────────

    async def _receive(self, request: Request) -> dict:
        body = await request.json()
        try:
            entry = body["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            message = value["messages"][0]
            from_number = message["from"]
            text = message.get("text", {}).get("body", "")
        except (KeyError, IndexError):
            return {"status": "ignored"}

        if not text:
            return {"status": "no_text"}

        inbound = InboundMessage(
            id=str(uuid.uuid4()),
            channel=ChannelKind.WHATSAPP,
            conversation_id=from_number,
            user_id=from_number,
            text=text,
            timestamp=time.time(),
        )

        reply = await self.agent.handle_message(inbound)

        # Send reply via Meta Cloud API
        await self._send_message(from_number, reply.text)
        return {"status": "ok"}

    async def _send_message(self, to: str, text: str) -> None:
        url = f"https://graph.facebook.com/v19.0/{self._phone_id}/messages"
        headers = {"Authorization": f"Bearer {self._api_token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error("WhatsApp send failed: %s", resp.text)
