"""Launcher script for the Weather Alert API"""

if __name__ == "__main__":
    import uvicorn
    from weather_alerts.main import app
    from weather_alerts.config.settings import settings

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)
