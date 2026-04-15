"""Unified LLM client — wraps OpenAI-compatible chat/completions API."""

from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from openclaw.config import LLMSettings
from openclaw.models import LLMMessage, LLMResponse, LLMToolCall


class LLMClient:
    """Async LLM client that works with OpenAI, Anthropic (via proxy), and Ollama."""

    def __init__(self, settings: LLMSettings) -> None:
        self.model = settings.llm_model

        api_key = settings.openai_api_key or settings.anthropic_api_key or "ollama"
        base_url: str | None = None
        if settings.llm_provider == "ollama":
            base_url = settings.ollama_url + "/v1"

        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def chat(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """Send a chat completion request and return a normalised response."""
        raw_msgs = [self._convert_message(m) for m in messages]
        kwargs: dict[str, Any] = {"model": self.model, "messages": raw_msgs}
        if tools:
            kwargs["tools"] = tools

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        tool_calls: list[LLMToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    LLMToolCall(
                        id=tc.id,
                        type="function",
                        function_name=tc.function.name,
                        function_arguments=tc.function.arguments,
                    )
                )

        return LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
        )

    # ── helpers ──────────────────────────────────────────────────

    @staticmethod
    def _convert_message(m: LLMMessage) -> dict[str, Any]:
        if m.role == "tool":
            return {"role": "tool", "content": m.content or "", "tool_call_id": m.tool_call_id}
        if m.role == "assistant" and m.tool_calls:
            return {
                "role": "assistant",
                "content": m.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function_name,
                            "arguments": tc.function_arguments,
                        },
                    }
                    for tc in m.tool_calls
                ],
            }
        return {"role": m.role, "content": m.content or ""}
