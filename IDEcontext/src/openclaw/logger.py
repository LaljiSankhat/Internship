"""Structured logging for OpenClaw."""

from __future__ import annotations

import logging
import sys

from rich.logging import RichHandler


def get_logger(name: str = "openclaw", level: str | None = None) -> logging.Logger:
    """Return a configured logger. Call once at startup; cached thereafter."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    effective_level = (level or "INFO").upper()
    logger.setLevel(effective_level)

    # Console (rich)
    console = RichHandler(rich_tracebacks=True, show_path=False)
    console.setLevel(effective_level)
    logger.addHandler(console)

    # File
    fh = logging.FileHandler("openclaw.log", encoding="utf-8")
    fh.setLevel(effective_level)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(fh)

    return logger
