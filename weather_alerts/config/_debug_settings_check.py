from weather_alerts.config.settings import settings

def main() -> None:
    print("App name:", settings.app_name)
    print("Debug:", settings.debug)
    print("OpenWeather key set:", bool(settings.openweather_api_key))


if __name__ == "__main__":
    main()