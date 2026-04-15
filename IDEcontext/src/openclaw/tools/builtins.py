"""Built-in tools that ship with OpenClaw."""

from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path

from openclaw.models import ToolParameter, ToolResult
from openclaw.tools.registry import tool


# ─── exec: run a shell command ──────────────────────────────────────

@tool(
    name="exec",
    description="Execute a shell command in the workspace directory and return stdout/stderr.",
    parameters={
        "command": ToolParameter(type="string", description="The shell command to run"),
        "cwd": ToolParameter(
            type="string",
            description="Working directory (defaults to workspace root)",
            required=False,
        ),
        "timeout": ToolParameter(
            type="number",
            description="Timeout in seconds (default 30)",
            required=False,
            default=30,
        ),
    },
)
async def exec_tool(
    command: str,
    cwd: str | None = None,
    timeout: int = 30,
    workspace_dir: str = ".",
    **_: object,
) -> ToolResult:
    work_dir = cwd or workspace_dir
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=work_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        output = (stdout.decode() + "\n" + stderr.decode()).strip()
        return ToolResult(success=proc.returncode == 0, output=output)
    except asyncio.TimeoutError:
        return ToolResult(success=False, output="Command timed out")
    except Exception as exc:
        return ToolResult(success=False, output=str(exc))


# ─── read_file ──────────────────────────────────────────────────────

@tool(
    name="read_file",
    description="Read the contents of a file. Returns the text content.",
    parameters={
        "path": ToolParameter(type="string", description="Path to the file (absolute or relative to workspace)"),
        "start_line": ToolParameter(type="number", description="Start line (1-based, optional)", required=False),
        "end_line": ToolParameter(type="number", description="End line (1-based, optional)", required=False),
    },
)
async def read_file_tool(
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    workspace_dir: str = ".",
    **_: object,
) -> ToolResult:
    try:
        fpath = Path(path) if Path(path).is_absolute() else Path(workspace_dir) / path
        text = fpath.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        if start_line or end_line:
            s = (start_line or 1) - 1
            e = end_line or len(lines)
            lines = lines[s:e]
        return ToolResult(success=True, output="".join(lines))
    except Exception as exc:
        return ToolResult(success=False, output=str(exc))


# ─── write_file ─────────────────────────────────────────────────────

@tool(
    name="write_file",
    description="Write content to a file. Creates parent directories if needed.",
    parameters={
        "path": ToolParameter(type="string", description="Path to the file"),
        "content": ToolParameter(type="string", description="Content to write"),
    },
)
async def write_file_tool(
    path: str,
    content: str,
    workspace_dir: str = ".",
    **_: object,
) -> ToolResult:
    try:
        fpath = Path(path) if Path(path).is_absolute() else Path(workspace_dir) / path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
        return ToolResult(success=True, output=f"Wrote {len(content)} bytes to {fpath}")
    except Exception as exc:
        return ToolResult(success=False, output=str(exc))


# ─── list_dir ───────────────────────────────────────────────────────

@tool(
    name="list_dir",
    description="List files and directories under a given path.",
    parameters={
        "path": ToolParameter(
            type="string",
            description="Directory path (defaults to workspace root)",
            required=False,
        ),
    },
)
async def list_dir_tool(
    path: str | None = None,
    workspace_dir: str = ".",
    **_: object,
) -> ToolResult:
    try:
        target = Path(path) if path and Path(path).is_absolute() else Path(workspace_dir) / (path or ".")
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        lines = [f"{'📁 ' if e.is_dir() else '📄 '}{e.name}" for e in entries]
        return ToolResult(success=True, output="\n".join(lines) or "(empty directory)")
    except Exception as exc:
        return ToolResult(success=False, output=str(exc))


# ─── web_search (via DuckDuckGo HTML — no API key needed) ──────────

@tool(
    name="web_search",
    description="Search the web using DuckDuckGo and return top results.",
    parameters={
        "query": ToolParameter(type="string", description="Search query"),
        "max_results": ToolParameter(type="number", description="Max results (default 5)", required=False, default=5),
    },
)
async def web_search_tool(
    query: str,
    max_results: int = 5,
    **_: object,
) -> ToolResult:
    import httpx

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (OpenClaw Agent)"},
            )
            resp.raise_for_status()
            # Basic extraction of result snippets
            text = resp.text
            results: list[str] = []
            parts = text.split('class="result__snippet"')
            for part in parts[1 : max_results + 1]:
                snippet_end = part.find("</a>")
                snippet = part[:snippet_end] if snippet_end != -1 else part[:300]
                # Strip HTML tags crudely
                import re
                clean = re.sub(r"<[^>]+>", "", snippet).strip()
                if clean:
                    results.append(clean)
            return ToolResult(success=True, output="\n---\n".join(results) or "No results found.")
    except Exception as exc:
        return ToolResult(success=False, output=str(exc))


# ─── append_file ────────────────────────────────────────────────────

@tool(
    name="append_file",
    description="Append content to the end of an existing file.",
    parameters={
        "path": ToolParameter(type="string", description="Path to the file"),
        "content": ToolParameter(type="string", description="Content to append"),
    },
)
async def append_file_tool(
    path: str,
    content: str,
    workspace_dir: str = ".",
    **_: object,
) -> ToolResult:
    try:
        fpath = Path(path) if Path(path).is_absolute() else Path(workspace_dir) / path
        with fpath.open("a", encoding="utf-8") as f:
            f.write(content)
        return ToolResult(success=True, output=f"Appended {len(content)} bytes to {fpath}")
    except Exception as exc:
        return ToolResult(success=False, output=str(exc))
