"""File-backed in-memory conversation store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from openclaw.models import MemoryEntry


class MemoryStore(Protocol):
    """Abstract memory interface."""

    def append(self, conversation_id: str, entry: MemoryEntry) -> None: ...
    def get_history(self, conversation_id: str, limit: int = 50) -> list[MemoryEntry]: ...
    def clear(self, conversation_id: str) -> None: ...
    async def save(self) -> None: ...


class FileMemoryStore:
    """Keeps conversations in RAM and persists to <workspace>/.openclaw/memory/."""

    def __init__(self, workspace_dir: Path) -> None:
        self._dir = workspace_dir / ".openclaw" / "memory"
        self._conversations: dict[str, list[MemoryEntry]] = {}

    # ── public API ───────────────────────────────────────────────

    def append(self, conversation_id: str, entry: MemoryEntry) -> None:
        self._conversations.setdefault(conversation_id, []).append(entry)

    def get_history(self, conversation_id: str, limit: int = 50) -> list[MemoryEntry]:
        return self._conversations.get(conversation_id, [])[-limit:]

    def clear(self, conversation_id: str) -> None:
        self._conversations.pop(conversation_id, None)

    async def load(self, conversation_id: str) -> None:
        path = self._dir / f"{conversation_id}.json"
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            self._conversations[conversation_id] = [MemoryEntry(**e) for e in raw]

    async def save(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        for cid, entries in self._conversations.items():
            path = self._dir / f"{cid}.json"
            path.write_text(
                json.dumps([e.model_dump() for e in entries], indent=2, default=str),
                encoding="utf-8",
            )
