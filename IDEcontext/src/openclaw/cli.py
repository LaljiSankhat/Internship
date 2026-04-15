"""
OpenClaw CLI — the main entry-point.

Usage:
    openclaw serve          # Start API server + adapters + heartbeat
    openclaw mcp            # Start MCP server (stdio, for IDE integration)
    openclaw chat           # Interactive CLI chat with the agent
    openclaw workspace sync # Sync agent brain → IDE rule files
"""

from __future__ import annotations

import asyncio
import sys
import time
import uuid

import click

from openclaw.logger import get_logger


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """OpenClaw — self-hosted AI agent & MCP server."""
    get_logger()


# ─── serve ───────────────────────────────────────────────────────────

@main.command()
@click.option("--port", default=None, type=int, help="HTTP port (default from env/3100)")
def serve(port: int | None) -> None:
    """Start the full OpenClaw server (REST API + messaging adapters + heartbeat)."""
    from openclaw.config import load_config
    from openclaw.server import start_server

    cfg = load_config()
    if port:
        cfg.port = port  # type: ignore[misc]

    click.echo(f"🔥 Starting OpenClaw server on :{cfg.port}")
    asyncio.run(start_server(cfg))


# ─── mcp ─────────────────────────────────────────────────────────────

@main.command()
def mcp() -> None:
    """Start the MCP server (stdio) for VS Code / Cursor integration."""
    from openclaw.mcp_server import run_mcp_server

    click.echo("🔌 Starting OpenClaw MCP server (stdio)…")
    asyncio.run(run_mcp_server())


# ─── chat ────────────────────────────────────────────────────────────

@main.command()
@click.option("--conversation", "-c", default="cli-chat", help="Conversation ID")
def chat(conversation: str) -> None:
    """Interactive CLI conversation with the OpenClaw agent."""
    from openclaw.agent import Agent
    from openclaw.config import load_config
    from openclaw.models import ChannelKind, InboundMessage

    cfg = load_config()
    agent = Agent(cfg)

    click.echo("💬 OpenClaw CLI chat (type 'exit' to quit)\n")

    async def _chat_loop() -> None:
        while True:
            try:
                user_input = click.prompt("You", prompt_suffix=" > ")
            except (EOFError, KeyboardInterrupt):
                break
            if user_input.strip().lower() in ("exit", "quit", "/exit", "/quit"):
                break

            msg = InboundMessage(
                id=str(uuid.uuid4()),
                channel=ChannelKind.CLI,
                conversation_id=conversation,
                user_id="cli-user",
                text=user_input,
                timestamp=time.time(),
            )
            reply = await agent.handle_message(msg)
            click.echo(f"\n🤖 {reply.text}\n")

    asyncio.run(_chat_loop())
    click.echo("Bye!")


# ─── workspace ───────────────────────────────────────────────────────

@main.group()
def workspace() -> None:
    """Workspace management commands."""


@workspace.command()
@click.option(
    "--editors",
    "-e",
    default="cursor",
    help="Comma-separated list of editors to sync to (cursor, vscode)",
)
def sync(editors: str) -> None:
    """Sync OpenClaw's brain into IDE rule files (.cursorrules, .vscode/, etc.)."""
    from openclaw.config import load_config
    from openclaw.workspace import sync_to_editors

    cfg = load_config()
    editor_list = [e.strip() for e in editors.split(",")]
    sync_to_editors(cfg, editor_list)
    click.echo(f"✅ Workspace synced for: {', '.join(editor_list)}")


# ─── init ────────────────────────────────────────────────────────────

@main.command()
@click.argument("directory", default=".")
def init(directory: str) -> None:
    """Initialise an OpenClaw workspace in the given directory."""
    from pathlib import Path

    root = Path(directory).resolve()
    oc_dir = root / ".openclaw"

    # Create directories
    (oc_dir / "memory").mkdir(parents=True, exist_ok=True)
    (oc_dir / "skills").mkdir(parents=True, exist_ok=True)

    # Create default files if they don't exist
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        agents_md.write_text(
            "# Agent Instructions\n\n"
            "Describe your project and how the agent should behave here.\n",
            encoding="utf-8",
        )

    heartbeat_md = root / "HEARTBEAT.md"
    if not heartbeat_md.exists():
        heartbeat_md.write_text(
            "# Heartbeat Tasks\n\n"
            "Add tasks as `- [ ] do something` and the agent will pick them up.\n",
            encoding="utf-8",
        )

    progress_md = root / "PROGRESS.md"
    if not progress_md.exists():
        progress_md.write_text("# Progress Log\n\n", encoding="utf-8")

    # Create example skill
    example_skill = oc_dir / "skills" / "example.md"
    if not example_skill.exists():
        example_skill.write_text(
            "---\n"
            "name: example\n"
            "description: An example skill — delete or replace this.\n"
            "required_tools:\n"
            "  - exec\n"
            "examples:\n"
            "  - 'run the example'\n"
            "---\n\n"
            "# Example Skill\n\n"
            "This is a template. Write instructions here that teach the agent\n"
            "how to perform a specific task using the available tools.\n",
            encoding="utf-8",
        )

    click.echo(f"✅ OpenClaw workspace initialised in {root}")
    click.echo(f"   Created: .openclaw/, AGENTS.md, HEARTBEAT.md, PROGRESS.md")


if __name__ == "__main__":
    main()
