
from fastapi import FastAPI
from weather_alerts.config.settings import settings
from weather_alerts.api import users as users, alerts as alerts

app = FastAPI(
    title=settings.app_name,
    description="Weather alert notification system - monitors weather and sends alerts",
    version="1.0.0",
    debug=settings.debug,
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