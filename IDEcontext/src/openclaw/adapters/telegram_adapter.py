"""Telegram adapter — uses python-telegram-bot (async)."""

from __future__ import annotations

import logging
import time
import uuid

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from openclaw.agent import Agent
from openclaw.config import OpenClawConfig
from openclaw.models import ChannelKind, InboundMessage

logger = logging.getLogger("openclaw.adapters.telegram")


class TelegramAdapter:
    """Bridge between Telegram Bot API and the OpenClaw Agent."""

    def __init__(self, agent: Agent, config: OpenClawConfig) -> None:
        self.agent = agent
        self.config = config
        tg = config.telegram
        if not tg or not tg.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required for the Telegram adapter")

        self.allowed_users = tg.allowed_user_list
        self.app = Application.builder().token(tg.bot_token).build()

        # Register handlers
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("clear", self._cmd_clear))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message))

    async def start(self) -> None:
        """Start polling for messages."""
        logger.info("Telegram adapter starting (polling)…")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()  # type: ignore[union-attr]

    async def stop(self) -> None:
        await self.app.updater.stop()  # type: ignore[union-attr]
        await self.app.stop()
        await self.app.shutdown()

    # ── handlers ─────────────────────────────────────────────────

    def _is_allowed(self, user_id: int) -> bool:
        if not self.allowed_users:
            return True  # no whitelist = allow all
        return str(user_id) in self.allowed_users

    async def _cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user and not self._is_allowed(update.effective_user.id):
            return
        await update.message.reply_text(  # type: ignore[union-attr]
            "👋 Hey! I'm **OpenClaw**, your self-hosted AI agent.\n"
            "Send me any message and I'll get to work.",
            parse_mode="Markdown",
        )

    async def _cmd_clear(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user and not self._is_allowed(update.effective_user.id):
            return
        chat_id = str(update.effective_chat.id)  # type: ignore[union-attr]
        self.agent.memory.clear(chat_id)
        await update.message.reply_text("🗑️ Conversation cleared.")  # type: ignore[union-attr]

    async def _on_message(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return
        user = update.effective_user
        if user and not self._is_allowed(user.id):
            return

        chat_id = str(update.effective_chat.id)  # type: ignore[union-attr]

        inbound = InboundMessage(
            id=str(uuid.uuid4()),
            channel=ChannelKind.TELEGRAM,
            conversation_id=chat_id,
            user_id=str(user.id) if user else "unknown",
            text=update.message.text,
            timestamp=time.time(),
        )

        reply = await self.agent.handle_message(inbound)

        # Telegram has a 4096-char limit per message
        text = reply.text
        for i in range(0, len(text), 4096):
            await update.message.reply_text(text[i : i + 4096])
