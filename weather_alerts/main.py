from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import asyncio

from weather_alerts.config.settings import settings
from weather_alerts.api import users as users, alerts as alerts
from weather_alerts.services.weather_check_service import WeatherCheckService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_periodic_weather_checks():
    """Background task to check weather periodically"""
    service = WeatherCheckService()

    while True:
        if settings.enable_background_checks:
            logger.info("Running background weather check...")
            await service.check_all_users()

        # Wait for next cycle
        await asyncio.sleep(settings.weather_check_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch background task
    task = asyncio.create_task(run_periodic_weather_checks())
    yield
    # Shutdown: Cancel task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.app_name,
    description="Weather alert notification system - monitors weather and sends alerts",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "Weather Alert System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.app_name,
    }


# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)