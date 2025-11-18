# Python
from typing import Any, Dict, Optional

import httpx

from weather_alerts.config.settings import settings


class WeatherService:
    """Service to fetch weather data from OpenWeather API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.api_key = api_key or settings.openweather_api_key
        self.base_url = (base_url or settings.openweather_base_url).rstrip("/")
        self.timeout = timeout_seconds
        self._client = client  # for testing/mocking

        if not self.api_key:
            raise ValueError("OpenWeather API key not configured")

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client:
            return self._client
        return httpx.AsyncClient(timeout=self.timeout)

    async def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather for a location.
        Location can be a city string like 'Berlin,DE' or coordinates 'lat,lon'.
        """
        url = f"{self.base_url}/weather"

        params: Dict[str, Any] = {
            "appid": self.api_key,
            "units": "metric",
        }

        # Simple heuristic: if it contains a comma and both parts are numeric, treat as lat/lon
        if "," in location:
            left, right = [p.strip() for p in location.split(",", 1)]
            if self._is_number(left) and self._is_number(right):
                params.update({"lat": left, "lon": right})
            else:
                params["q"] = location
        else:
            params["q"] = location

        client = await self._get_client()
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error {e.response.status_code}: {e.response.text}")
            return None
        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            return None
        finally:
            if self._client is None:
                await client.aclose()

    @staticmethod
    def parse_weather_data(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract a compact payload from OpenWeather response.
        Returns empty dict on invalid input.
        """
        if not data or "main" not in data or "weather" not in data or not data["weather"]:
            return {}

        weather = data["weather"][0]
        main = data["main"]

        return {
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "condition": weather.get("main"),
            "description": weather.get("description"),
            "location": data.get("name"),
        }

    @staticmethod
    def _is_number(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False