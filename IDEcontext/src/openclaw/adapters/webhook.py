"""Generic webhook API — a FastAPI server that also hosts the REST endpoint for any HTTP client."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from openclaw.agent import Agent
from openclaw.models import ChannelKind, InboundMessage

logger = logging.getLogger("openclaw.adapters.webhook")


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"
    user_id: str = "api-user"


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


def mount_webhook_routes(app: FastAPI, agent: Agent) -> None:
    """Add REST /chat and /health endpoints."""

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest) -> ChatResponse:
        inbound = InboundMessage(
            id=str(uuid.uuid4()),
            channel=ChannelKind.WEBHOOK,
            conversation_id=req.conversation_id,
            user_id=req.user_id,
            text=req.message,
            timestamp=time.time(),
        )
        reply = await agent.handle_message(inbound)
        return ChatResponse(reply=reply.text, conversation_id=reply.conversation_id)

    @app.get("/health")
    async def health() -> dict:
        return {
            "status": "ok",
            "tools": agent.tools.list_names(),
            "skills": agent.skills.names,
        }
