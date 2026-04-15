"""
OpenClaw MCP (Model Context Protocol) Server.

Exposes the agent's tools and workspace context over the MCP protocol
so that VS Code / Cursor / any MCP-compatible IDE can use OpenClaw as
an intelligent backend.

Run standalone:
    openclaw mcp
    # or
    python -m openclaw.mcp_server
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    Resource,
    TextContent,
    Tool,
)

from openclaw.config import OpenClawConfig, load_config
from openclaw.memory import FileMemoryStore
from openclaw.skills import SkillRegistry
from openclaw.tools.registry import get_default_registry

# Register built-in tools
import openclaw.tools.builtins  # noqa: F401

logger = logging.getLogger("openclaw.mcp")

# ─── Server factory ─────────────────────────────────────────────────


def create_mcp_server(config: OpenClawConfig | None = None) -> Server:
    """Build and return a fully-configured MCP Server instance."""

    cfg = config or load_config()
    workspace = cfg.resolved_workspace
    tools_registry = get_default_registry()
    skills = SkillRegistry()
    skills.load_bundled()
    skills.load_workspace(workspace)
    memory = FileMemoryStore(workspace)

    app = Server("openclaw")

    # ── List tools ───────────────────────────────────────────────

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        """Advertise every registered OpenClaw tool to the IDE."""
        result: list[Tool] = []
        for schema in tools_registry.openai_schemas():
            fn = schema["function"]
            result.append(
                Tool(
                    name=fn["name"],
                    description=fn.get("description", ""),
                    inputSchema=fn.get("parameters", {"type": "object", "properties": {}}),
                )
            )
        # Add a high-level "ask_agent" meta-tool
        result.append(
            Tool(
                name="ask_agent",
                description=(
                    "Send a natural-language request to the OpenClaw agent. "
                    "The agent will reason, use tools, and return a text answer."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Your question or instruction for the agent.",
                        },
                        "conversation_id": {
                            "type": "string",
                            "description": "Optional conversation ID to continue a session.",
                        },
                    },
                    "required": ["message"],
                },
            )
        )
        return result

    # ── Call a tool ──────────────────────────────────────────────

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute an OpenClaw tool or the meta 'ask_agent' tool."""
        if name == "ask_agent":
            return await _handle_ask_agent(arguments, cfg)

        result = await tools_registry.invoke(
            name,
            json.dumps(arguments),
            workspace_dir=str(workspace),
        )
        return [TextContent(type="text", text=result.output)]

    # ── List resources (project context files) ───────────────────

    @app.list_resources()
    async def list_resources() -> list[Resource]:
        """Expose key workspace files as MCP resources."""
        resources: list[Resource] = []
        context_files = [
            "AGENTS.md",
            "SOUL.md",
            "IDENTITY.md",
            "HEARTBEAT.md",
            "PROGRESS.md",
            ".cursorrules",
            ".openclaw/config.yaml",
        ]
        for name in context_files:
            fpath = workspace / name
            if fpath.exists():
                resources.append(
                    Resource(
                        uri=f"file://{fpath}",
                        name=name,
                        description=f"OpenClaw context file: {name}",
                        mimeType="text/markdown",
                    )
                )

        # Expose loaded skills
        for skill in skills.all():
            resources.append(
                Resource(
                    uri=f"openclaw://skill/{skill.name}",
                    name=f"skill:{skill.name}",
                    description=skill.meta.description,
                    mimeType="text/markdown",
                )
            )
        return resources

    @app.read_resource()
    async def read_resource(uri: str) -> str:
        """Return the content of an OpenClaw resource."""
        if uri.startswith("openclaw://skill/"):
            skill_name = uri.split("/")[-1]
            skill = skills.get(skill_name)
            return skill.textbook if skill else f"Skill '{skill_name}' not found."

        if uri.startswith("file://"):
            fpath = Path(uri.removeprefix("file://"))
            if fpath.exists():
                return fpath.read_text(encoding="utf-8")
            return f"File not found: {fpath}"

        return f"Unknown resource URI: {uri}"

    return app


# ── ask_agent helper ─────────────────────────────────────────────────

async def _handle_ask_agent(
    arguments: dict[str, Any], config: OpenClawConfig
) -> list[TextContent]:
    """Run a full agent loop for the 'ask_agent' MCP tool."""
    from openclaw.agent import Agent
    from openclaw.models import ChannelKind, InboundMessage
    import time, uuid

    agent = Agent(config)
    msg = InboundMessage(
        id=str(uuid.uuid4()),
        channel=ChannelKind.CLI,
        conversation_id=arguments.get("conversation_id", "mcp-session"),
        user_id="mcp-client",
        text=arguments["message"],
        timestamp=time.time(),
    )
    reply = await agent.handle_message(msg)
    return [TextContent(type="text", text=reply.text)]


# ── Entry-point ──────────────────────────────────────────────────────

async def run_mcp_server(config: OpenClawConfig | None = None) -> None:
    """Start the MCP server on stdio."""
    server = create_mcp_server(config)
    logger.info("Starting OpenClaw MCP server (stdio)…")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """CLI entry-point for `openclaw mcp`."""
    from openclaw.logger import get_logger
    get_logger()
    asyncio.run(run_mcp_server())


if __name__ == "__main__":
    main()
