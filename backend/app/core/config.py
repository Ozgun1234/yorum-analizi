"""
Application configuration.
All settings are read from environment variables via .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
