import datetime
import json
import pathlib

import requests

LOCATIONS = [
    {"location_id": 1, "city": "Richmond",     "latitude": 37.55, "longitude": -77.46},
    {"location_id": 2, "city": "Williamsburg", "latitude": 37.27, "longitude": -76.71},
]
DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Today's date goes in the filename, not inside the file.
today = datetime.date.today().strftime("%Y-%m-%d")

for loc in LOCATIONS:
    city = loc["city"]

    # 1. Weather: one call, one file, untouched.
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": loc["latitude"], "longitude": loc["longitude"],
                "hourly": "temperature_2m", "forecast_days": 1},
    ).json()
    with open(DATA_DIR / f"weather-{city}-{today}.json", "w") as f:
        json.dump(weather, f, indent=2, sort_keys=True)

    # 2. Air quality: different host, exact same pattern.
    air = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={"latitude": loc["latitude"], "longitude": loc["longitude"],
                "hourly": "pm2_5", "forecast_days": 1},
    ).json()
    with open(DATA_DIR / f"air_quality-{city}-{today}.json", "w") as f:
        json.dump(air, f, indent=2, sort_keys=True)

    print(f"Saved {city}")