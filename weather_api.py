import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime

def get_current_weather():
    """Get current weather for Warsaw and return dictionary."""
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=300)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Parameters for Warsaw
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 52.2298,
        "longitude": 21.0118,
        "current": ["temperature_2m", "apparent_temperature", "wind_speed_10m"],
        "timezone": "Europe/Warsaw"
    }

    # Process current data
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()

    # Create dictionary
    weather_data = {
        "timestamp": datetime.fromtimestamp(current.Time()).strftime('%Y-%m-%d %H:%M:%S'),
        "temperature": round(current.Variables(0).Value(), 1),
        "apparent_temperature": round(current.Variables(1).Value(), 1),
        "wind_speed": round(current.Variables(2).Value(), 1)
    }
    
    return weather_data