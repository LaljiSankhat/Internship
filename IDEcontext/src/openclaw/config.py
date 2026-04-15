"""Centralised configuration loaded from environment / .env file."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENCLAW_")

    llm_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    llm_model: str = "gpt-4o"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_url: str = "http://localhost:11434"


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")

    bot_token: str = ""
    allowed_users: str = ""  # comma-separated IDs

    @property
    def allowed_user_list(self) -> list[str]:
        return [u.strip() for u in self.allowed_users.split(",") if u.strip()]


class SlackSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SLACK_")

    bot_token: str = ""
    signing_secret: str = ""
    app_token: str = ""


class WhatsAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WHATSAPP_")

    verify_token: str = ""
    api_token: str = ""
    phone_number_id: str = ""


class OpenClawConfig(BaseSettings):
    """Root configuration – reads from env vars / .env automatically."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    workspace_dir: Path = Field(default=Path("."))
    port: int = Field(default=3100, alias="PORT")
    heartbeat_interval_minutes: int = Field(default=5, alias="HEARTBEAT_INTERVAL_MINUTES")
    heartbeat_file: str = Field(default="HEARTBEAT.md", alias="HEARTBEAT_FILE")

    # Sub-configs
    llm: LLMSettings = Field(default_factory=LLMSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    slack: SlackSettings = Field(default_factory=SlackSettings)
    whatsapp: WhatsAppSettings = Field(default_factory=WhatsAppSettings)

    @property
    def heartbeat_enabled(self) -> bool:
        return self.heartbeat_interval_minutes > 0

    @property
    def resolved_workspace(self) -> Path:
        return self.workspace_dir.resolve()


def load_config() -> OpenClawConfig:
    """Load config from env / .env, validating via pydantic."""
    return OpenClawConfig()
