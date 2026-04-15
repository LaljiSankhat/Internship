#!/usr/bin/env python3
"""
clawsync_watcher.py — ClawSync Auto-Sync File Watcher
=======================================================
Runs as a background daemon and automatically appends an entry to
global_state.md every time a source file is saved in the project.

NO agent prompting needed. Start it once; it runs silently forever.

Dependencies
------------
  pip install watchfiles

Usage
-----
  Foreground    :  python3 clawsync_watcher.py /path/to/project
  Background    :  nohup python3 clawsync_watcher.py /path/to/project > ~/.openclaw/watcher.log 2>&1 &
  Active project:  python3 clawsync_watcher.py   (auto-detects from ~/.openclaw/registry.json)
"""

from __future__ import annotations

import json
import os
import platform
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Dependency check ─────────────────────────────────────────────────────────
try:
    from watchfiles import watch, Change
except ImportError:
    print("[ClawSync Watcher] 'watchfiles' not found. Install it:")
    print("  pip install watchfiles")
    sys.exit(1)

# ────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────

GLOBAL_REGISTRY = Path.home() / ".openclaw" / "registry.json"
OPENCLAW_DIR = ".openclaw"
GLOBAL_STATE_FILE = "global_state.md"

# Files/dirs to ignore (changes in these won't be logged)
IGNORED_DIRS = {
    ".git", ".openclaw", "__pycache__", "node_modules",
    ".venv", "venv", ".env", "dist", "build", ".next",
    ".cache", "coverage", ".pytest_cache", ".mypy_cache",
}
IGNORED_EXTENSIONS = {
    ".pyc", ".pyo", ".log", ".lock", ".tmp", ".swp", ".swo",
    ".DS_Store", ".db", ".sqlite3",
}

# Debounce: batch changes within this window (seconds) into one log entry
DEBOUNCE_SECONDS = 2.5

# Detect the IDE that saved the file (heuristic based on temp file patterns)
def _detect_ide(path: str) -> str:
    p = path.lower()
    if ".cursor" in p or "cursor" in p:
        return "Cursor AI"
    if ".vscode" in p:
        return "VS Code / Copilot"
    return "IDE"


# ────────────────────────────────────────────────────────────────────────────
# Registry helpers (shared with clawsync_mcp.py)
# ────────────────────────────────────────────────────────────────────────────

def _get_active_project() -> Optional[Path]:
    if not GLOBAL_REGISTRY.exists():
        return None
    try:
        registry = json.loads(GLOBAL_REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for entry in registry.values():
        if entry.get("status") == "active":
            return Path(entry["path"])
    return None


def _resolve_project_root(path_arg: Optional[str]) -> Path:
    if path_arg:
        p = Path(path_arg).resolve()
        if not p.is_dir():
            print(f"[ERROR] '{p}' is not a directory.")
            sys.exit(1)
        return p
    active = _get_active_project()
    if active:
        print(f"[ClawSync Watcher] Auto-detected active project: {active}")
        return active
    # Last resort: CWD
    return Path.cwd()


# ────────────────────────────────────────────────────────────────────────────
# State-file writer
# ────────────────────────────────────────────────────────────────────────────

def _append_to_state(state_path: Path, agent: str, message: str) -> None:
    """Append one row to the Agent History table in global_state.md."""
    if not state_path.exists():
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = f"| {timestamp} | {agent} | {message} |"
    marker = "<!-- ClawSync appends entries below this line. Most recent = bottom. -->"
    content = state_path.read_text(encoding="utf-8")
    if marker in content:
        content = content.replace(marker, f"{marker}\n{new_row}")
    else:
        content = content.rstrip() + f"\n\n{new_row}\n"
    state_path.write_text(content, encoding="utf-8")


# ────────────────────────────────────────────────────────────────────────────
# Change filter
# ────────────────────────────────────────────────────────────────────────────

def _should_ignore(path: str, project_root: Path) -> bool:
    rel = Path(path)
    # Check every path component against ignored dirs
    for part in rel.parts:
        if part in IGNORED_DIRS:
            return True
    # Check extension
    if rel.suffix.lower() in IGNORED_EXTENSIONS:
        return True
    # Ignore the state files themselves (avoid feedback loop)
    try:
        full = Path(path).resolve()
        openclaw = (project_root / OPENCLAW_DIR).resolve()
        if str(full).startswith(str(openclaw)):
            return True
    except Exception:
        pass
    return False


def _describe_changes(batch: dict[str, set[str]]) -> str:
    """
    batch = { "modified": {"a.py", "b.py"}, "added": {"c.py"}, "deleted": {"d.py"} }
    Returns a concise one-line summary.
    """
    parts = []
    for change_type, files in batch.items():
        names = ", ".join(sorted(Path(f).name for f in files)[:4])
        if len(files) > 4:
            names += f" +{len(files) - 4} more"
        parts.append(f"{change_type}: {names}")
    return " | ".join(parts)


# ────────────────────────────────────────────────────────────────────────────
# Main watcher loop
# ────────────────────────────────────────────────────────────────────────────

CHANGE_TYPE_MAP = {
    Change.added: "added",
    Change.modified: "modified",
    Change.deleted: "deleted",
}


def run_watcher(project_root: Path) -> None:
    import threading

    state_path = project_root / OPENCLAW_DIR / GLOBAL_STATE_FILE

    if not state_path.exists():
        print(f"[ERROR] global_state.md not found at {state_path}")
        print(f"  Run clawsync_init.py first:  python3 clawsync_init.py {project_root}")
        sys.exit(1)

    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║  ClawSync Watcher — Auto-Sync Daemon             ║")
    print(f"╚══════════════════════════════════════════════════╝")
    print(f"  Watching : {project_root}")
    print(f"  State    : {state_path}")
    print(f"  Platform : {platform.system()}")
    print(f"  Debounce : {DEBOUNCE_SECONDS}s")
    print(f"\n  Ctrl+C to stop.\n")

    # Log startup
    _append_to_state(state_path, "ClawSync-Watcher", "Auto-sync daemon started")

    # Debounce state (shared across the callback and main loop)
    pending: dict[str, set[str]] = defaultdict(set)
    lock = threading.Lock()
    flush_timer: list[threading.Timer | None] = [None]

    def _flush():
        """Flush pending changes to state file."""
        with lock:
            if not pending:
                return
            snapshot = {k: set(v) for k, v in pending.items()}
            pending.clear()
        summary = _describe_changes(snapshot)
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Auto-sync: {summary}")
        _append_to_state(state_path, "Auto-Watcher", summary)

    try:
        for changes in watch(str(project_root), recursive=True):
            for change_type, path in changes:
                if _should_ignore(path, project_root):
                    continue
                change_name = CHANGE_TYPE_MAP.get(change_type, "changed")
                with lock:
                    pending[change_name].add(path)

                # Reset the debounce timer on every change
                if flush_timer[0] is not None:
                    flush_timer[0].cancel()
                flush_timer[0] = threading.Timer(DEBOUNCE_SECONDS, _flush)
                flush_timer[0].daemon = True
                flush_timer[0].start()

    except KeyboardInterrupt:
        # Flush any remaining changes
        _flush()
        print("\n\n[ClawSync Watcher] Stopped by user.")
        _append_to_state(state_path, "ClawSync-Watcher", "Auto-sync daemon stopped")


# ────────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ClawSync Watcher — Automatic context sync daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Project root to watch (default: active project from registry)",
    )
    args = parser.parse_args()

    root = _resolve_project_root(args.path)
    run_watcher(root)
