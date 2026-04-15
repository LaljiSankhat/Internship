"""Slack adapter — uses slack-bolt (async)."""

from __future__ import annotations

import logging
import time
import uuid

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from openclaw.agent import Agent
from openclaw.config import OpenClawConfig
from openclaw.models import ChannelKind, InboundMessage

logger = logging.getLogger("openclaw.adapters.slack")


class SlackAdapter:
    """Bridge between Slack (Socket Mode) and the OpenClaw Agent."""

    def __init__(self, agent: Agent, config: OpenClawConfig) -> None:
        self.agent = agent
        self.config = config
        slack = config.slack
        if not slack or not slack.bot_token:
            raise ValueError("SLACK_BOT_TOKEN is required for the Slack adapter")

        self.bolt = AsyncApp(
            token=slack.bot_token,
            signing_secret=slack.signing_secret,
        )
        self._handler = AsyncSocketModeHandler(self.bolt, slack.app_token)

        # Listen to DMs and app mentions
        self.bolt.event("message")(self._on_message)
        self.bolt.event("app_mention")(self._on_mention)

    async def start(self) -> None:
        logger.info("Slack adapter starting (socket mode)…")
        await self._handler.start_async()

    async def stop(self) -> None:
        await self._handler.close_async()

    # ── handlers ─────────────────────────────────────────────────

    async def _on_message(self, event: dict, say: callable) -> None:  # type: ignore[type-arg]
        await self._process(event, say)

    async def _on_mention(self, event: dict, say: callable) -> None:  # type: ignore[type-arg]
        await self._process(event, say)

    async def _process(self, event: dict, say: callable) -> None:  # type: ignore[type-arg]
        text = event.get("text", "")
        if not text or event.get("bot_id"):
            return

        inbound = InboundMessage(
            id=str(uuid.uuid4()),
            channel=ChannelKind.SLACK,
            conversation_id=event.get("channel", "unknown"),
            user_id=event.get("user", "unknown"),
            text=text,
            timestamp=time.time(),
        )

        reply = await self.agent.handle_message(inbound)
        await say(reply.text)
