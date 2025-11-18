"""Tests for weather service"""
import pytest
from unittest.mock import AsyncMock, Mock
import httpx

from weather_alerts.services.weather_service import WeatherService


@pytest.fixture
def mock_weather_response():
    """Sample OpenWeather API response"""
    return {
        "name": "Berlin",
        "main": {
            "temp": 15.5,
            "feels_like": 14.2,
            "humidity": 65
        },
        "weather": [
            {
                "main": "Clouds",
                "description": "scattered clouds"
            }
        ]
    }


@pytest.mark.asyncio
async def test_weather_service_initialization():
    """Test WeatherService can be initialized"""
    service = WeatherService(api_key="test_key")
    assert service.api_key == "test_key"
    assert service.base_url == "https://api.openweathermap.org/data/2.5"


@pytest.mark.asyncio
async def test_weather_service_no_api_key():
    """Test that missing API key raises error"""
    with pytest.raises(ValueError, match="API key not configured"):
        WeatherService(api_key="")


@pytest.mark.asyncio
async def test_get_current_weather_success(mock_weather_response):
    """Test successful weather fetch"""
    # Create mock HTTP client
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = Mock()
    mock_response.json.return_value = mock_weather_response
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    mock_client.aclose = AsyncMock()

    # Create service with mock client
    service = WeatherService(api_key="test_key", client=mock_client)

    # Get weather
    result = await service.get_current_weather("Berlin,DE")

    assert result is not None
    assert result["name"] == "Berlin"
    assert result["main"]["temp"] == 15.5

    # Verify API was called correctly
    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args
    assert "weather" in call_args[0][0]
    assert call_args[1]["params"]["q"] == "Berlin,DE"
    assert call_args[1]["params"]["units"] == "metric"


@pytest.mark.asyncio
async def test_get_current_weather_http_error():
    """Test weather fetch with HTTP error"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "City not found"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404", request=Mock(), response=mock_response
    )
    mock_client.get.return_value = mock_response
    mock_client.aclose = AsyncMock()

    service = WeatherService(api_key="test_key", client=mock_client)
    result = await service.get_current_weather("InvalidCity")

    assert result is None


@pytest.mark.asyncio
async def test_get_current_weather_with_coordinates():
    """Test weather fetch using coordinates"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = Mock()
    mock_response.json.return_value = {"name": "Location"}
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    mock_client.aclose = AsyncMock()

    service = WeatherService(api_key="test_key", client=mock_client)
    await service.get_current_weather("52.52,13.40")

    # Verify coordinates were used
    call_args = mock_client.get.call_args
    params = call_args[1]["params"]
    assert "lat" in params
    assert "lon" in params
    assert params["lat"] == "52.52"
    assert params["lon"] == "13.40"


def test_parse_weather_data(mock_weather_response):
    """Test parsing weather API response"""
    parsed = WeatherService.parse_weather_data(mock_weather_response)

    assert parsed["temperature"] == 15.5
    assert parsed["feels_like"] == 14.2
    assert parsed["humidity"] == 65
    assert parsed["condition"] == "Clouds"
    assert parsed["description"] == "scattered clouds"
    assert parsed["location"] == "Berlin"


def test_parse_weather_data_invalid():
    """Test parsing invalid data returns empty dict"""
    assert WeatherService.parse_weather_data(None) == {}
    assert WeatherService.parse_weather_data({}) == {}
    assert WeatherService.parse_weather_data({"main": {}}) == {}


def test_is_number():
    """Test number detection helper"""
    assert WeatherService._is_number("123") is True
    assert WeatherService._is_number("123.45") is True
    assert WeatherService._is_number("-123.45") is True
    assert WeatherService._is_number("abc") is False
    assert WeatherService._is_number("") is False