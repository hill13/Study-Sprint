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

    # Password reset
    # Short window on purpose - a reset token is a temporary key to an account
    password_reset_token_expire_minutes: int = 15
    # No email provider is wired up, so the reset token is written to the server
    # log. Set this to true in development to ALSO return it in the API response
    # so the flow can be exercised without email. Never enable in production.
    expose_reset_token: bool = False

    # Email delivery (Brevo)
    # brevo_api_key empty => reset emails are logged instead of sent, so local
    # development works with no account and no network calls.
    brevo_api_key: str = ""
    mail_from_email: str = ""        # must be a VERIFIED sender in Brevo
    mail_from_name: str = "StudySprint"

    # Where the reset link points. Must match the deployed frontend origin.
    frontend_url: str = "http://localhost:5173"

    # OpenAI API (for AI Insights feature)
    openai_api_key: str = ""
    class Config:
        # This tells pydantic to read from a .env file
        env_file = ".env"
        env_file_encoding = "utf-8"


# lru_cache ensures we only create Settings once (singleton pattern)
# This is more efficient than creating it on every request
@lru_cache
def get_settings() -> Settings:
    return Settings()
