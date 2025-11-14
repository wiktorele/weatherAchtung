import asyncio
from weather_alerts.services.weather_service import WeatherService
from weather_alerts.config.settings import settings


async def main():
    print("API Key loaded:",
          settings.openweather_api_key[:10] + "..." if settings.openweather_api_key else "NOT LOADED")

    svc = WeatherService()
    raw = await svc.get_current_weather("Warsaw,PL")

    if raw is None:
        print("❌ Raw loaded: False (API call failed)")
    else:
        print("✅ Raw loaded: True")
        parsed = svc.parse_weather_data(raw)
        print("Parsed:", parsed)


if __name__ == "__main__":
    asyncio.run(main())