# monitoring/owm_ingest.py
import requests
from typing import Dict, Any, Optional

# -----------------------
# Replace with env var for production
OWM_API_KEY = "89f0a2e8c0b0a840fcd9f4c04d54c3fd"
# -----------------------

BASE_URL_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"


def fetch_current_weather(lat: Optional[float] = None,
                          lon: Optional[float] = None,
                          city: Optional[str] = None) -> Dict[str, Any]:
    """
    Uses OpenWeatherMap Current Weather Data endpoint to get current weather.
    Can query by (lat, lon) OR city name.
    """
    params = {"appid": OWM_API_KEY, "units": "metric"}

    if city:
        params["q"] = city
    elif lat is not None and lon is not None:
        params["lat"] = lat
        params["lon"] = lon
    else:
        raise ValueError("Provide either city name or lat/lon")

    resp = requests.get(BASE_URL_CURRENT, params=params, timeout=10)
    resp.raise_for_status()
    j = resp.json()

    main = j.get("main", {})
    wind = j.get("wind", {})
    clouds = j.get("clouds", {})
    rain = j.get("rain", {})  # e.g., {"1h": 0.25}
    precip_1h = rain.get("1h", 0.0)

    return {
        "temp": main.get("temp"),
        "humidity": main.get("humidity"),
        "wind_speed": wind.get("speed"),
        "clouds": clouds.get("all"),
        "precip_1h": precip_1h,
    }


def fetch_forecast_precip_sum(lat: Optional[float] = None,
                              lon: Optional[float] = None,
                              city: Optional[str] = None,
                              hours: int = 24) -> float:
    """
    Get forecast precipitation sum for next `hours` hours using 5-day/3-hour forecast.
    Works with (lat, lon) OR city.
    """
    params = {"appid": OWM_API_KEY, "units": "metric"}

    if city:
        params["q"] = city
    elif lat is not None and lon is not None:
        params["lat"] = lat
        params["lon"] = lon
    else:
        raise ValueError("Provide either city name or lat/lon")

    resp = requests.get(BASE_URL_FORECAST, params=params, timeout=10)
    resp.raise_for_status()
    j = resp.json()

    items = j.get("list", [])
    total_precip = 0.0
    hours_covered = 0
    for item in items:
        if hours_covered >= hours:
            break
        rain = item.get("rain", {})
        total_precip += rain.get("3h", 0.0)
        hours_covered += 3
    return total_precip


def get_features(lat: Optional[float] = None,
                 lon: Optional[float] = None,
                 city: Optional[str] = None,
                 station_sim: bool = True) -> Dict[str, float]:
    """
    Build a feature dict:
    - avg_temp
    - max_temp
    - avg_wind
    - avg_cloud
    - total_precip (forecast + current 1h)
    - avg_humidity
    - water_level (simulated or None)
    - flow_rate (simulated or None)
    Works with either (lat, lon) OR city.
    """
    cur = fetch_current_weather(lat=lat, lon=lon, city=city)
    forecast_precip = fetch_forecast_precip_sum(lat=lat, lon=lon, city=city, hours=24)

    total_precip = forecast_precip + (cur.get("precip_1h", 0.0) or 0.0)
    avg_temp = cur.get("temp", 0.0)
    max_temp = avg_temp + 3.0  # simple heuristic
    avg_wind = cur.get("wind_speed", 0.0)
    avg_cloud = cur.get("clouds", 0.0)
    avg_humidity = cur.get("humidity", 0.0)

    # Simulated river sensor readings (replace with real sensor ingestion)
    water_level = None
    flow_rate = None
    if station_sim:
        water_level = round(0.5 + total_precip * 0.05, 3)  # meters
        flow_rate = round(30 + total_precip * 4.0, 2)      # cubic m/s

    return {
        "avg_temp": avg_temp,
        "max_temp": max_temp,
        "avg_wind": avg_wind,
        "avg_cloud": avg_cloud,
        "total_precip": total_precip,
        "avg_humidity": avg_humidity,
        "water_level": water_level,
        "flow_rate": flow_rate
    }


if __name__ == "__main__":
    # Test with city
    print("City -> Bangalore,IN")
    print(get_features(city="Bangalore,IN"))

    # Test with coordinates
    print("\nCoordinates -> lat=12.9716, lon=77.5946")
    print(get_features(lat=12.9716, lon=77.5946))
