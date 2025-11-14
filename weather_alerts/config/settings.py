from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]  # project root (folder with pyproject.toml)
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    # App
    app_name: str = "Weather Alert System"
    debug: bool = True

    # OpenWeather API
    openweather_api_key: str = ""
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"

    # AWS (we'll use these later)
    aws_region: str = "eu-central-1"
    dynamodb_table_users: str = "weather-alert-users"
    dynamodb_table_alerts: str = "weather-alert-alerts"

    # Local development flags
    use_local_dynamodb: bool = False
    local_dynamodb_endpoint: Optional[str] = None

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8")

settings = Settings()