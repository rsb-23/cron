#!/usr/bin/env python3
"""
Daily weather fetcher for cities in Chhattisgarh.
Uses Open-Meteo API — free, no API key needed.
Output: data/weather.json
Run via: python scripts/fetch_weather.py

To change cities, edit the CITIES list below.
"""

import json
import urllib.parse
import urllib.request

from utils import formatted_now, save_as_json

CITIES = [
    {"name": "Raipur", "lat": 21.2514, "lon": 81.6296},
    {"name": "Bilaspur", "lat": 22.0796, "lon": 82.1391},
    {"name": "Kachna", "lat": 21.2657, "lon": 81.7094},
]

# WMO Weather Code → human label + emoji
WMO = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Icy Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Dense Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    71: ("Slight Snow", "🌨️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Slight Showers", "🌦️"),
    81: ("Moderate Showers", "🌧️"),
    82: ("Violent Showers", "⛈️"),
    85: ("Slight Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm + Hail", "⛈️"),
    99: ("Severe Thunderstorm", "⛈️"),
}

BASE_URL = "https://api.open-meteo.com/v1/forecast"

DAILY_VARS = ",".join(
    [
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "weathercode",
        "precipitation_sum",
        "precipitation_probability_max",
        "windspeed_10m_max",
        "uv_index_max",
        "sunrise",
        "sunset",
    ]
)


def fetch_city(city: dict) -> dict:
    params = urllib.parse.urlencode(
        {
            "latitude": city["lat"],
            "longitude": city["lon"],
            "daily": DAILY_VARS,
            "timezone": "Asia/Kolkata",
            "forecast_days": 4,
        }
    )
    url = f"{BASE_URL}?{params}"
    with urllib.request.urlopen(url, timeout=20) as resp:
        raw = json.loads(resp.read())

    daily = raw["daily"]
    n = len(daily["time"])

    forecast = []
    for i in range(n):
        code = daily["weathercode"][i] or 0
        label, emoji = WMO.get(code, (f"Code {code}", "🌡️"))

        # Format sunrise/sunset as HH:MM
        def hhmm(iso_dt):
            if iso_dt and "T" in iso_dt:
                return iso_dt.split("T")[1][:5]
            return ""

        forecast.append(
            {
                "date": daily["time"][i],
                "max_temp": daily["temperature_2m_max"][i],
                "min_temp": daily["temperature_2m_min"][i],
                "feels_like_max": daily["apparent_temperature_max"][i],
                "wmo_code": code,
                "condition": label,
                "emoji": emoji,
                "precipitation_mm": daily["precipitation_sum"][i],
                "precip_probability": daily["precipitation_probability_max"][i],
                "wind_kmh": daily["windspeed_10m_max"][i],
                "uv_index": daily["uv_index_max"][i],
                "sunrise": hhmm(daily["sunrise"][i]),
                "sunset": hhmm(daily["sunset"][i]),
            }
        )

    return {"name": city["name"], "lat": city["lat"], "lon": city["lon"], "forecast": forecast}


def main():
    results = []
    errors = []

    for city in CITIES:
        print(f"  Fetching {city['name']} ...", end=" ", flush=True)
        try:
            results.append(fetch_city(city))
            print("✓")
        except Exception as exc:
            print(f"✗  {exc}")
            errors.append({"city": city["name"], "error": str(exc)})

    out = {"updated": formatted_now(), "timezone": "Asia/Kolkata", "cities": results, "errors": errors}
    save_as_json("weather.json", data=out)

    print(f"\n✓ Saved weather for {len(results)} cities → data/weather.json")
    if errors:
        print(f"  {len(errors)} error(s): {[e['city'] for e in errors]}")


if __name__ == "__main__":
    main()
