"""
Application configuration loaded from environment variables.
Supports Redis, LLM provider selection, and API keys.
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # LLM
    LLM_PROVIDER: str = "openai"  # openai | claude
    OPENAI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None

    # App
    API_PREFIX: str = "/api"
    WORKER_POLL_INTERVAL_SEC: int = 5
    WORKER_MAX_RETRIES: int = 3
    WORKER_BACKOFF_BASE_SEC: float = 2.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    """Return application settings singleton."""
    return Settings()
