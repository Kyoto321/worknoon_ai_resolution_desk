"""
Application configuration using pydantic-settings.
All settings are loaded from environment variables (or .env file).
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────
    app_name: str = "WorkNoon AI Support Assistant"
    app_env: str = "development"
    debug: bool = True

    # ── AI ────────────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./support_assistant.db"

    # ── CORS ──────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ── Rate Limiting ─────────────────────────────────────────────────────
    rate_limit_requests: int = 20
    rate_limit_window: int = 60

    # ── Logging ───────────────────────────────────────────────────────────
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — instantiated once per process."""
    return Settings()
