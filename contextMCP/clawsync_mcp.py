#!/usr/bin/env python3
"""
clawsync_mcp.py — ClawSync MCP Server
=======================================
A FastMCP server that exposes the Global Context Bridge to any MCP client
(Cursor, VS Code, Claude Desktop, etc.).

Tools
-----
  set_global_context(path)          Bootstrap a project and register it.
  update_context(agent, update)     Post a status update from any agent.

Resources
---------
  clawsync://current-brain          Latest 10 lines of global_state.md.

Usage
-----
  Run directly              :  python clawsync_mcp.py
  Background (Linux/macOS)  :  nohup python clawsync_mcp.py &
  Background (Windows)      :  start /B pythonw clawsync_mcp.py
  Via uvicorn (HTTP/SSE)    :  uvicorn clawsync_mcp:mcp.app --host 0.0.0.0 --port 8765
"""

from __future__ import annotations

import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── FastMCP ─────────────────────────────────────────────────────────────────
try:
    from fastmcp import FastMCP
except ImportError:
    print("[ClawSync] FastMCP not found. Install with:  pip install fastmcp")
    sys.exit(1)

# ── Local init script ────────────────────────────────────────────────────────
try:
    from clawsync_init import init_project
except ImportError:
    # Allow running from a different CWD
    _SCRIPT_DIR = Path(__file__).parent.resolve()
    sys.path.insert(0, str(_SCRIPT_DIR))
    from clawsync_init import init_project  # type: ignore

# ────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────

GLOBAL_REGISTRY = Path.home() / ".openclaw" / "registry.json"
OPENCLAW_DIR = ".openclaw"
GLOBAL_STATE_FILE = "global_state.md"
ACTIVE_TASK_FILE = "active_task.md"

mcp = FastMCP(name="ClawSync")


# ────────────────────────────────────────────────────────────────────────────
# Registry helpers
# ────────────────────────────────────────────────────────────────────────────

def _load_registry() -> dict:
    GLOBAL_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    if GLOBAL_REGISTRY.exists():
        try:
            return json.loads(GLOBAL_REGISTRY.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def _save_registry(registry: dict) -> None:
    GLOBAL_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    GLOBAL_REGISTRY.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def _get_active_project() -> Optional[dict]:
    """Return the first project marked 'active' in the registry, or None."""
    registry = _load_registry()
    for entry in registry.values():
        if entry.get("status") == "active":
            return entry
    return None


def _resolve_state_path(project_path: Optional[str] = None) -> Optional[Path]:
    """
    Find global_state.md.
    Priority: explicit path > active registry project > CWD.
    """
    if project_path:
        p = Path(project_path).resolve() / OPENCLAW_DIR / GLOBAL_STATE_FILE
        if p.exists():
            return p

    active = _get_active_project()
    if active:
        p = Path(active["path"]) / OPENCLAW_DIR / GLOBAL_STATE_FILE
        if p.exists():
            return p

    # Fallback: look in CWD
    p = Path.cwd() / OPENCLAW_DIR / GLOBAL_STATE_FILE
    if p.exists():
        return p

    return None


# ────────────────────────────────────────────────────────────────────────────
# Tool 1 — set_global_context
# ────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def set_global_context(path: str) -> str:
    """
    Initialise the ClawSync Global Context Bridge for a project and mark it
    as the active project in the global registry.

    Parameters
    ----------
    path : str
        Absolute path to the project root directory.

    Returns
    -------
    str
        A human-readable confirmation message with the registry path.

    Example
    -------
    In any MCP-connected chat:
        "MCP, make this project global"
        → set_global_context("/home/user/my-project")
    """
    root = init_project(path, overwrite=False)
    project_name = root.name

    registry = _load_registry()

    # Deactivate all other projects
    for entry in registry.values():
        if entry.get("status") == "active":
            entry["status"] = "inactive"

    # Register this project as active
    registry[str(root)] = {
        "name": project_name,
        "path": str(root),
        "status": "active",
        "platform": platform.system(),
        "activated_at": datetime.now().isoformat(),
        "state_file": str(root / OPENCLAW_DIR / GLOBAL_STATE_FILE),
        "task_file": str(root / OPENCLAW_DIR / ACTIVE_TASK_FILE),
    }

    _save_registry(registry)

    return (
        f"✅ Project '{project_name}' is now the active ClawSync project.\n"
        f"   Root     : {root}\n"
        f"   Registry : {GLOBAL_REGISTRY}\n"
        f"   State    : {root / OPENCLAW_DIR / GLOBAL_STATE_FILE}\n\n"
        f"All MCP clients (.cursorrules, Copilot instructions, AGENTS.md) "
        f"are now pointing to this project's shared memory."
    )


# ────────────────────────────────────────────────────────────────────────────
# Tool 2 — update_context
# ────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def update_context(agent_name: str, status_update: str) -> str:
    """
    Append a status update from an agent to the shared global_state.md.
    This update is instantly visible to all other IDEs watching the file.

    Parameters
    ----------
    agent_name : str
        Name of the calling agent — e.g. "Cursor AI", "Antigravity",
        "GitHub Copilot", "ClawSync-Init".
    status_update : str
        A concise one-line summary of what the agent just did or decided.

    Returns
    -------
    str
        Confirmation that the state file was updated.

    Notes
    -----
    The update is appended as a new row in the Markdown table under
    "Agent History" in global_state.md.  File-watching tools (e.g. VS Code's
    built-in watcher, Cursor's file-watcher, or `watchfiles`) will surface
    the change automatically.
    """
    state_path = _resolve_state_path()

    if state_path is None:
        return (
            "⚠️  No active ClawSync project found.\n"
            "   Run `set_global_context(path)` first to register a project."
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = f"| {timestamp} | {agent_name} | {status_update} |"

    content = state_path.read_text(encoding="utf-8")

    # Locate the agent history table and append the new row
    marker = "<!-- ClawSync appends entries below this line. Most recent = bottom. -->"
    if marker in content:
        content = content.replace(
            marker,
            f"{marker}\n{new_row}",
        )
    else:
        # Fallback: just append to end of file
        content = content.rstrip() + f"\n\n{new_row}\n"

    state_path.write_text(content, encoding="utf-8")

    # Also update active_task.md "Last Sync" timestamp
    task_path = state_path.parent / ACTIVE_TASK_FILE
    if task_path.exists():
        task_content = task_path.read_text(encoding="utf-8")
        # Replace the last-sync line
        lines = task_content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("`") and "· initialised by" in line or "· updated by" in line:
                lines[i] = f"`{timestamp}` · updated by {agent_name}"
                break
            elif line.startswith("`") and "· initialised by" not in line and "Last Sync" in lines[i - 1] if i > 0 else False:
                lines[i] = f"`{timestamp}` · updated by {agent_name}"
                break
        task_path.write_text("\n".join(lines), encoding="utf-8")

    return (
        f"✅ Context updated in '{state_path}'.\n"
        f"   Agent  : {agent_name}\n"
        f"   Update : {status_update}\n"
        f"   Time   : {timestamp}\n\n"
        f"All IDEs watching this file will see the update immediately."
    )


# ────────────────────────────────────────────────────────────────────────────
# Resource — clawsync://current-brain
# ────────────────────────────────────────────────────────────────────────────

@mcp.resource("clawsync://current-brain")
def current_brain() -> str:
    """
    Dynamic resource that returns the latest 10 lines of global_state.md.

    This gives any connected MCP client (Cursor, VS Code extension, etc.)
    an instant snapshot of the current project brain without reading the
    full file.

    URI: clawsync://current-brain
    """
    state_path = _resolve_state_path()

    if state_path is None:
        return (
            "⚠️  No active ClawSync project.\n"
            "Call the `set_global_context` tool to register one."
        )

    lines = state_path.read_text(encoding="utf-8").splitlines()
    tail = lines[-10:] if len(lines) >= 10 else lines

    header = (
        f"# ClawSync — Current Brain (last 10 lines)\n"
        f"# Source: {state_path}\n"
        f"# Snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"# ─────────────────────────────────────────\n\n"
    )

    return header + "\n".join(tail)


# ────────────────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ClawSync MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode (default: stdio for Cursor/VS Code; sse for HTTP)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for SSE transport (default: 8765)",
    )
    args = parser.parse_args()

    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║  ClawSync MCP Server v1.0.0                      ║")
    print(f"║  Global Context Bridge — One Memory. Every IDE.  ║")
    print(f"╚══════════════════════════════════════════════════╝")
    print(f"  Transport : {args.transport}")
    if args.transport == "sse":
        print(f"  Endpoint  : http://{args.host}:{args.port}/sse")
    print(f"  Registry  : {GLOBAL_REGISTRY}")
    print(f"  Platform  : {platform.system()}\n")

    if args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run()  # stdio — default for Cursor / VS Code MCP config
