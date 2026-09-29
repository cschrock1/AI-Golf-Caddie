import json
from urllib.parse import urlencode
from urllib.request import urlopen


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_current_weather(latitude: float, longitude: float) -> dict:
    params = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "timezone": "auto",
    })
    with urlopen(f"{OPEN_METEO_URL}?{params}", timeout=8.0) as response:
        payload = json.loads(response.read())
    current = payload.get("current")
    if not current:
        raise ValueError("Weather provider returned no current conditions")
    return {
        "temperature_f": current.get("temperature_2m"),
        "wind_speed_mph": current.get("wind_speed_10m"),
        "wind_direction_degrees": current.get("wind_direction_10m"),
        "observed_at": current.get("time"),
        "timezone": payload.get("timezone"),
        "source": "Open-Meteo",
    }
