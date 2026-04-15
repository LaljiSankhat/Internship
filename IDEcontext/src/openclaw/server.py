"""
Main server — wires together FastAPI, adapters, heartbeat, and the agent.
"""

from __future__ import annotations

import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from openclaw.agent import Agent
from openclaw.config import OpenClawConfig, load_config
from openclaw.heartbeat import Heartbeat

logger = logging.getLogger("openclaw.server")


async def start_server(config: OpenClawConfig | None = None) -> None:
    """Boot the full OpenClaw server: REST API + messaging adapters + heartbeat."""
    cfg = config or load_config()
    agent = Agent(cfg)

    app = FastAPI(title="OpenClaw", version="0.1.0")

    # ── REST / webhook routes ────────────────────────────────────
    from openclaw.adapters.webhook import mount_webhook_routes

    mount_webhook_routes(app, agent)

    # ── Optional WhatsApp webhook ────────────────────────────────
    if cfg.whatsapp and cfg.whatsapp.api_token:
        from openclaw.adapters.whatsapp_adapter import WhatsAppAdapter

        WhatsAppAdapter(agent, cfg, app)
        logger.info("WhatsApp adapter enabled")

    # ── Optional Telegram ────────────────────────────────────────
    telegram_adapter = None
    if cfg.telegram and cfg.telegram.bot_token:
        from openclaw.adapters.telegram_adapter import TelegramAdapter

        telegram_adapter = TelegramAdapter(agent, cfg)
        logger.info("Telegram adapter enabled")

    # ── Optional Slack ───────────────────────────────────────────
    slack_adapter = None
    if cfg.slack and cfg.slack.bot_token:
        from openclaw.adapters.slack_adapter import SlackAdapter

        slack_adapter = SlackAdapter(agent, cfg)
        logger.info("Slack adapter enabled")

    # ── Heartbeat ────────────────────────────────────────────────
    heartbeat = Heartbeat(agent, cfg)

    # ── Start everything ─────────────────────────────────────────
    uvi_config = uvicorn.Config(app, host="0.0.0.0", port=cfg.port, log_level="info")
    server = uvicorn.Server(uvi_config)

    tasks: list[asyncio.Task] = []  # type: ignore[type-arg]

    async def run_all() -> None:
        if telegram_adapter:
            await telegram_adapter.start()
        if slack_adapter:
            await slack_adapter.start()
        await heartbeat.start()

        await server.serve()

        # Cleanup
        await heartbeat.stop()
        if telegram_adapter:
            await telegram_adapter.stop()
        if slack_adapter:
            await slack_adapter.stop()

    await run_all()
