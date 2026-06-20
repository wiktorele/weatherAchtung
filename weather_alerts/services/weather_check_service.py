import uuid
import logging
from datetime import datetime
from typing import List

from weather_alerts.models.alert import Alert, AlertType
from weather_alerts.models.user import User
from weather_alerts.services.weather_service import WeatherService


from weather_alerts.api.users import users_db
from weather_alerts.api.alerts import alerts_db

logger = logging.getLogger(__name__)


class WeatherCheckService:
    def __init__(self):
        self.weather_service = WeatherService()

    async def check_all_users(self):
        """
        Iterates over all users in the database and checks their weather conditions.
        """
        if not users_db:
            logger.info("No users to check.")
            return

        logger.info(f"Starting weather check cycle for {len(users_db)} users...")

        for user in users_db.values():
            try:
                await self._process_user(user)
            except Exception as e:
                logger.error(f"Error checking weather for user {user.user_id}: {e}")

    async def _process_user(self, user: User):
        # 1. Fetch Weather
        raw_weather = await self.weather_service.get_current_weather(user.location)
        if not raw_weather:
            return

        data = self.weather_service.parse_weather_data(raw_weather)
        if not data:
            return

        current_temp = data.get("temperature")
        condition = data.get("condition", "")

        # 2. Check Preferences & Generate Alerts
        new_alerts: List[Alert] = []

        # Check Min Temp
        if user.preferences.min_temp is not None and current_temp is not None:
            if current_temp < user.preferences.min_temp:
                new_alerts.append(self._create_alert(
                    user, AlertType.TEMP_LOW,
                    f"It's cold! {current_temp}°C is below your threshold of {user.preferences.min_temp}°C.",
                    current_temp, condition
                ))

        # Check Max Temp
        if user.preferences.max_temp is not None and current_temp is not None:
            if current_temp > user.preferences.max_temp:
                new_alerts.append(self._create_alert(
                    user, AlertType.TEMP_HIGH,
                    f"It's hot! {current_temp}°C is above your threshold of {user.preferences.max_temp}°C.",
                    current_temp, condition
                ))

        # Check Rain
        if user.preferences.rain_alerts:
            # Simple keyword check; OpenWeather returns "Rain", "Drizzle", "Thunderstorm" in main condition
            if condition in ["Rain", "Drizzle", "Thunderstorm"]:
                new_alerts.append(self._create_alert(
                    user, AlertType.RAIN,
                    f"Precipitation detected: {condition}.",
                    current_temp, condition
                ))

        # 3. Persist Alerts
        if new_alerts:
            logger.info(f"Generated {len(new_alerts)} alerts for user {user.email}")
            alerts_db.extend(new_alerts)

            # Update user metadata
            user.last_alert = datetime.utcnow()

    def _create_alert(self, user: User, type_: AlertType, msg: str, temp: float, condition: str) -> Alert:
        return Alert(
            alert_id=str(uuid.uuid4()),
            user_id=user.user_id,
            alert_type=type_,
            message=msg,
            temperature=temp,
            weather_condition=condition,
            created_at=datetime.utcnow(),
            location=user.location
        )