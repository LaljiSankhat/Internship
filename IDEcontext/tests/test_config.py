"""Tests for config loading."""

from openclaw.config import load_config, OpenClawConfig


def test_config_loads_defaults() -> None:
    cfg = load_config()
    assert isinstance(cfg, OpenClawConfig)
    assert cfg.port == 3100
    assert cfg.heartbeat_file == "HEARTBEAT.md"
    assert cfg.llm.llm_provider in ("openai", "anthropic", "ollama")
