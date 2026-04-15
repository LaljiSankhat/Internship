"""Core data models for OpenClaw."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ─── Channel / Messaging ────────────────────────────────────────────

class ChannelKind(str, Enum):
    TELEGRAM = "telegram"
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    WEBHOOK = "webhook"
    CLI = "cli"


class InboundMessage(BaseModel):
    """A message arriving from any channel."""
    id: str
    channel: ChannelKind
    conversation_id: str
    user_id: str
    text: str
    timestamp: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class OutboundMessage(BaseModel):
    """A reply the agent sends back on a channel."""
    conversation_id: str
    channel: ChannelKind
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# ─── Tool system ────────────────────────────────────────────────────

class ToolParameter(BaseModel):
    type: str  # "string" | "number" | "boolean" | "object" | "array"
    description: str
    required: bool = True
    default: Any = None


class ToolResult(BaseModel):
    success: bool
    output: str
    data: Any = None


# ─── Memory ─────────────────────────────────────────────────────────

class MemoryRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MemoryEntry(BaseModel):
    role: MemoryRole
    content: str
    timestamp: float
    tool_name: str | None = None
    tool_call_id: str | None = None


# ─── LLM abstraction ────────────────────────────────────────────────

class LLMToolCall(BaseModel):
    id: str
    type: str = "function"
    function_name: str
    function_arguments: str  # JSON string


class LLMMessage(BaseModel):
    role: str  # user | assistant | system | tool
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)


class LLMResponse(BaseModel):
    content: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    finish_reason: str = "stop"


# ─── Skill ──────────────────────────────────────────────────────────

class SkillMeta(BaseModel):
    """Metadata for a loaded skill (the textbook body is stored separately)."""
    name: str
    description: str
    required_tools: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
