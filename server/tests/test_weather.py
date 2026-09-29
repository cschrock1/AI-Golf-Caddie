import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from app.services.weather import get_current_weather


class WeatherServiceTests(unittest.TestCase):
    @patch("app.services.weather.urlopen")
    def test_requests_current_weather_in_golf_friendly_units(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self):
                import json
                return json.dumps({
                    "timezone": "America/Indiana/Indianapolis",
                    "current": {
                        "temperature_2m": 68.4,
                        "wind_speed_10m": 7.2,
                        "wind_direction_10m": 225,
                        "time": "2026-09-28T14:00",
                    },
                }).encode()

        urlopen.return_value = Response()

        result = get_current_weather(41.0, -86.0)

        self.assertEqual(result["temperature_f"], 68.4)
        self.assertEqual(result["wind_speed_mph"], 7.2)
        self.assertEqual(result["wind_direction_degrees"], 225)
        self.assertEqual(result["source"], "Open-Meteo")
        query = parse_qs(urlparse(urlopen.call_args.args[0]).query)
        self.assertEqual(query["temperature_unit"], ["fahrenheit"])
        self.assertEqual(query["wind_speed_unit"], ["mph"])


if __name__ == "__main__":
    unittest.main()
