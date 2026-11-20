"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-based configuration with safe defaults for local development."""

    # Application
    app_name: str = "CareerPilot AI"
    app_env: str = "development"
    app_debug: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Security
    jwt_secret_key: str = "change-me-to-a-strong-random-secret-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Database
    database_url: str = (
        "postgresql+asyncpg://careerpilot:careerpilot@localhost:5432/careerpilot"
    )

    # AI / Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"

    # Vector store (ChromaDB)
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
