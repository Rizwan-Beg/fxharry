"""
Application configuration management for the institutional trading backend.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(slots=True)
class Settings:
    """Runtime configuration sourced from environment variables."""

    app_name: str = os.getenv("APP_NAME", "AI Forex Trading Dashboard")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/tradingdb"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    broker: str = os.getenv("BROKER", "IBKR")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_json: bool = os.getenv("LOG_JSON", "false").lower() == "true"
    enable_uvicorn_access_log: bool = (
        os.getenv("ENABLE_UVICORN_ACCESS_LOG", "false").lower() == "true"
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()

