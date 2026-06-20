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

    # AWS
    aws_region: str = "eu-central-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    dynamodb_table_users: str = "weather-alert-users"
    dynamodb_table_alerts: str = "weather-alert-alerts"
    sns_topic_arn: Optional[str] = None

    # Local development flags
    use_local_dynamodb: bool = False
    local_dynamodb_endpoint: Optional[str] = "http://localhost:4566"

    # Background Task Settings
    enable_background_checks: bool = False
    weather_check_interval_seconds: int = 600  # Default to 10 minutes

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8")

settings = Settings()