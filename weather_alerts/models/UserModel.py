from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlertPreferences(BaseModel):
    """User's weather alert preferences"""
    min_temp: Optional[float] = Field(None, description="Alert if temp drops below this (Celsius)")
    max_temp: Optional[float] = Field(None, description="Alert if temp rises above this (Celsius)")
    severe_weather: bool = Field(True, description="Alert on severe weather warnings")
    rain_alerts: bool = Field(False, description="Alert when rain is expected")


class UserBase(BaseModel):
    """Base user model"""
    email: str
    location: str = Field(..., description="City name or coordinates")
    preferences: AlertPreferences


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Model for updating user preferences"""
    location: Optional[str] = None
    preferences: Optional[AlertPreferences] = None


class User(UserBase):
    """Full user model with ID and metadata"""
    user_id: str
    created_at: datetime
    last_alert: Optional[datetime] = None

    class Config:
        from_attributes = True
