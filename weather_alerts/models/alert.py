from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional


class AlertType(str, Enum):
    """Types of weather alerts"""
    TEMP_HIGH = "temp_high"
    TEMP_LOW = "temp_low"
    SEVERE_WEATHER = "severe_weather"
    RAIN = "rain"


class Alert(BaseModel):
    """Weather alert model"""
    alert_id: str
    user_id: str
    alert_type: AlertType
    message: str
    temperature: Optional[float] = None
    weather_condition: str
    created_at: datetime
    location: str
