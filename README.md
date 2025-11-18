# WeatherAchtung – Weather Alert API

WeatherAchtung is a FastAPI-based service for managing weather alerts, integrated with OpenWeather API to fetch current conditions. It’s designed as a foundation for a weather notification system (email/SMS/push can be added later).

---

## Features

- FastAPI application with automatic interactive docs (Swagger UI / Redoc)
- User management:
  - Create, read, update, delete users
  - Store per-user weather alert preferences
- Weather integration service (OpenWeather):
  - Fetch current weather by city (`"Berlin,DE"`) or coordinates (`"52.52,13.40"`)
  - Parse raw API responses into a compact structured payload
- Health check endpoint for monitoring
- Fully typed models using Pydantic v2
- Test suite with pytest, pytest-asyncio, and coverage

---

## Requirements

- Python 3.11
- [uv](https://github.com/astral-sh/uv) for dependency and environment management
- An OpenWeather API key

---

## Setup

### 1. Clone the repository
```bash
  git clone <your-repo-url> weatherAchtung cd weatherAchtung
```


### 2. Create and sync the environment

This will create a virtual environment (if needed) and install all dependencies declared in `pyproject.toml`.

---

## Configuration

Configuration is handled via environment variables using `pydantic-settings`. For local development, create a `.env` file in the project root (same directory as `pyproject.toml`):

### Replace with your real OpenWeather API key
OPENWEATHER_API_KEY="YOUR_OPENWEATHER_API_KEY"
### Debug mode (enables FastAPI debug & uvicorn reload)
DEBUG=true
### AWS region (for later, not required for local dev)
AWS_REGION="eu-central-1"


If `OPENWEATHER_API_KEY` is not set or empty, the weather service will raise an error on initialization.

---

## Running the Application

bash uv run uvicorn weather_alerts.main:app --host 0.0.0.0 --port 8000 --reload

## API Overview

When the server is running, you can explore the API via:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`