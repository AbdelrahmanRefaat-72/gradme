"""
Configuration management using pydantic-settings.
Enforces strict environment variable loading, validation, and typing.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Smart Email Guardian"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "smart-email-guardian-dev-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./email_guardian.db"

    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # AI Provider (Gemini API / OpenAI API)
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Frontend URL (for CORS and OAuth redirect)
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
