"""Skill loader — reads markdown 'textbook' files from the skills directory."""

from __future__ import annotations

import logging
from pathlib import Path

import frontmatter  # python-frontmatter

from openclaw.models import SkillMeta

logger = logging.getLogger("openclaw.skills")


class Skill:
    """A loaded skill: metadata + textbook body."""

    def __init__(self, meta: SkillMeta, textbook: str) -> None:
        self.meta = meta
        self.textbook = textbook

    @property
    def name(self) -> str:
        return self.meta.name


class SkillRegistry:
    """Discovers and loads skill files from <workspace>/.openclaw/skills/ and bundled skills."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    @property
    def names(self) -> list[str]:
        return list(self._skills.keys())

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def all(self) -> list[Skill]:
        return list(self._skills.values())

    def load_directory(self, directory: Path) -> int:
        """Load all .md files in *directory* as skills. Returns count loaded."""
        if not directory.is_dir():
            return 0
        count = 0
        for md_file in sorted(directory.glob("*.md")):
            try:
                self._load_file(md_file)
                count += 1
            except Exception:
                logger.exception("Failed to load skill from %s", md_file)
        return count

    def load_bundled(self) -> int:
        """Load the skills bundled with OpenClaw."""
        bundled = Path(__file__).parent / "skills_bundled"
        return self.load_directory(bundled)

    def load_workspace(self, workspace_dir: Path) -> int:
        """Load skills from <workspace>/.openclaw/skills/"""
        return self.load_directory(workspace_dir / ".openclaw" / "skills")

    # ── internal ─────────────────────────────────────────────────

    def _load_file(self, path: Path) -> None:
        post = frontmatter.load(str(path))
        meta = SkillMeta(
            name=post.metadata.get("name", path.stem),
            description=post.metadata.get("description", ""),
            required_tools=post.metadata.get("required_tools", []),
            examples=post.metadata.get("examples", []),
        )
        self._skills[meta.name] = Skill(meta=meta, textbook=post.content)
        logger.debug("Loaded skill: %s", meta.name)
