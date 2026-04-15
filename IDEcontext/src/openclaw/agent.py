"""Agent engine — the main agentic loop that ties LLM ↔ Tools ↔ Memory together."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from openclaw.config import OpenClawConfig
from openclaw.llm import LLMClient
from openclaw.memory import FileMemoryStore
from openclaw.models import (
    InboundMessage,
    LLMMessage,
    LLMToolCall,
    MemoryEntry,
    MemoryRole,
    OutboundMessage,
)
from openclaw.skills import SkillRegistry
from openclaw.tools.registry import ToolRegistry, get_default_registry

# Ensure built-in tools are registered on import
import openclaw.tools.builtins  # noqa: F401

logger = logging.getLogger("openclaw.agent")

SYSTEM_PROMPT = """\
You are **OpenClaw**, a self-hosted personal AI assistant.
You live on the user's own machine and communicate via messaging apps.

## Capabilities
- Execute shell commands (tool: exec)
- Read/write/append files (tools: read_file, write_file, append_file)
- List directories (tool: list_dir)
- Search the web (tool: web_search)

## Rules
1. Be concise but helpful.
2. Always confirm before destructive operations (delete, overwrite, git push --force).
3. When you perform an action, report the result clearly.
4. If you are unsure, ask the user to clarify.

{skill_textbooks}
"""


class Agent:
    """Core agentic loop: receives a message, thinks, uses tools, replies."""

    def __init__(self, config: OpenClawConfig) -> None:
        self.config = config
        self.workspace = str(config.resolved_workspace)
        self.llm = LLMClient(config.llm)
        self.memory = FileMemoryStore(config.resolved_workspace)
        self.tools: ToolRegistry = get_default_registry()
        self.skills = SkillRegistry()

        # Load skills
        self.skills.load_bundled()
        self.skills.load_workspace(config.resolved_workspace)
        logger.info(
            "Agent initialised — tools: %s | skills: %s",
            self.tools.list_names(),
            self.skills.names,
        )

    async def handle_message(self, msg: InboundMessage) -> OutboundMessage:
        """Process one inbound message and return the agent's reply."""
        cid = msg.conversation_id

        # Record user message
        self.memory.append(
            cid,
            MemoryEntry(role=MemoryRole.USER, content=msg.text, timestamp=time.time()),
        )

        # Build LLM messages
        llm_messages = self._build_messages(cid)

        # Agentic loop (tool-use iterations)
        max_iterations = 10
        for _ in range(max_iterations):
            response = await self.llm.chat(
                llm_messages,
                tools=self.tools.openai_schemas(),
            )

            if response.tool_calls:
                # Record assistant message with tool calls
                llm_messages.append(
                    LLMMessage(
                        role="assistant",
                        content=response.content,
                        tool_calls=response.tool_calls,
                    )
                )

                # Execute each tool call
                for tc in response.tool_calls:
                    result = await self.tools.invoke(
                        tc.function_name,
                        tc.function_arguments,
                        workspace_dir=self.workspace,
                    )
                    llm_messages.append(
                        LLMMessage(
                            role="tool",
                            content=result.output,
                            tool_call_id=tc.id,
                        )
                    )
                    logger.info("Tool %s → success=%s", tc.function_name, result.success)
            else:
                # No more tool calls — we have a final text reply
                break

        reply_text = response.content or "(no response)"

        # Record assistant reply
        self.memory.append(
            cid,
            MemoryEntry(role=MemoryRole.ASSISTANT, content=reply_text, timestamp=time.time()),
        )
        await self.memory.save()

        return OutboundMessage(
            conversation_id=cid,
            channel=msg.channel,
            text=reply_text,
        )

    # ── internal helpers ─────────────────────────────────────────

    def _build_messages(self, conversation_id: str) -> list[LLMMessage]:
        """Assemble the full prompt: system + skill textbooks + conversation history."""
        skill_text = ""
        for skill in self.skills.all():
            skill_text += f"\n\n## Skill: {skill.meta.name}\n{skill.textbook}"

        system = SYSTEM_PROMPT.format(skill_textbooks=skill_text)
        messages: list[LLMMessage] = [LLMMessage(role="system", content=system)]

        for entry in self.memory.get_history(conversation_id, limit=40):
            messages.append(
                LLMMessage(
                    role=entry.role.value,
                    content=entry.content,
                    tool_call_id=entry.tool_call_id,
                )
            )
        return messages
