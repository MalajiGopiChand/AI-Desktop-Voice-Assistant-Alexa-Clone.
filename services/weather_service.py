"""Weather via OpenWeatherMap (free tier)."""
import requests
from config import OPENWEATHER_API_KEY, ASSISTANT_CITY
from database import get_setting


def get_api_key():
    return (
        __import__("os").environ.get("OPENWEATHER_API_KEY")
        or get_setting("openweather_api_key")
        or OPENWEATHER_API_KEY
    )


def get_weather(city=None):
    city = city or get_setting("user_city", ASSISTANT_CITY)
    key = get_api_key()
    if not key:
        return None, "OpenWeatherMap API key not configured. Add OPENWEATHER_API_KEY in Settings."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": key, "units": "metric"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        msg = (
            f"Weather in {city}: {desc}, {temp:.0f}°C, feels like {feels:.0f}°C. "
            f"Humidity {humidity}%, wind {wind} m/s."
        )
        return data, msg
    except Exception as e:
        return None, f"Could not fetch weather: {e}"
