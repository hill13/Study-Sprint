"""
Configuration Management
------------------------
This file loads settings from environment variables (or .env file).

WHY THIS MATTERS:
- Never hardcode secrets (passwords, API keys) in your code
- Different environments (dev, prod) need different settings
- pydantic-settings validates that required vars exist at startup
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./studysprint.db"

    # JWT Authentication
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Google Gemini API (for AI Insights feature)
    gemini_api_key: str = ""

    class Config:
        # This tells pydantic to read from a .env file
        env_file = ".env"
        env_file_encoding = "utf-8"


# lru_cache ensures we only create Settings once (singleton pattern)
# This is more efficient than creating it on every request
@lru_cache
def get_settings() -> Settings:
    return Settings()
