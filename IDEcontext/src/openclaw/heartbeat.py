"""Heartbeat — periodically checks HEARTBEAT.md for tasks and runs them."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from pathlib import Path

from openclaw.agent import Agent
from openclaw.config import OpenClawConfig
from openclaw.models import ChannelKind, InboundMessage

logger = logging.getLogger("openclaw.heartbeat")


class Heartbeat:
    """
    Every N minutes, reads a heartbeat file for pending tasks.
    If the file contains instructions, they are forwarded to the agent.
    After processing, the file is updated with results/timestamps.
    """

    def __init__(self, agent: Agent, config: OpenClawConfig) -> None:
        self.agent = agent
        self.config = config
        self.interval = config.heartbeat_interval_minutes * 60  # seconds
        self.filepath = config.resolved_workspace / config.heartbeat_file
        self._running = False
        self._task: asyncio.Task | None = None  # type: ignore[type-arg]

    async def start(self) -> None:
        if not self.config.heartbeat_enabled:
            logger.info("Heartbeat disabled")
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Heartbeat started — checking every %d min", self.config.heartbeat_interval_minutes)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    # ── main loop ────────────────────────────────────────────────

    async def _loop(self) -> None:
        while self._running:
            try:
                await self._tick()
            except Exception:
                logger.exception("Heartbeat tick failed")
            await asyncio.sleep(self.interval)

    async def _tick(self) -> None:
        if not self.filepath.exists():
            return

        content = self.filepath.read_text(encoding="utf-8").strip()
        if not content:
            return

        # Extract pending tasks (lines starting with "- [ ]")
        lines = content.splitlines()
        pending: list[str] = []
        rest: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- [ ]"):
                pending.append(stripped.removeprefix("- [ ]").strip())
            else:
                rest.append(line)

        if not pending:
            return

        logger.info("Heartbeat found %d pending task(s)", len(pending))

        for task_text in pending:
            inbound = InboundMessage(
                id=str(uuid.uuid4()),
                channel=ChannelKind.CLI,
                conversation_id="heartbeat",
                user_id="heartbeat",
                text=task_text,
                timestamp=time.time(),
            )
            reply = await self.agent.handle_message(inbound)
            rest.append(f"- [x] {task_text}")
            rest.append(f"  > _{reply.text[:500]}_")
            rest.append(f"  > Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Write back updated heartbeat file
        self.filepath.write_text("\n".join(rest) + "\n", encoding="utf-8")
        logger.info("Heartbeat tick complete")
