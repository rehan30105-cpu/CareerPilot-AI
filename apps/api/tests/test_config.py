"""Tests for application configuration loading."""

from app.core.config import settings


def test_settings_load():
    """Settings should load from environment with defaults."""
    assert settings.app_name == "CareerPilot AI"
    assert settings.app_env == "development"
    assert settings.api_port == 8000
    assert settings.ollama_model == "qwen3:4b"


def test_settings_app_debug_true():
    """Debug should be True in development."""
    assert settings.app_debug is True
