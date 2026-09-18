"""Real-time temperature adapter — Open-Meteo current weather, no API key."""
from urllib.request import urlopen
import json

def fetch_current_temperature(latitude=-60.0, longitude=20.0):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&timezone=UTC"
    try:
        with urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        return {
            "temperature_c": data.get("current", {}).get("temperature_2m"),
            "source": "open-meteo-current",
            "status": "real",
            "data_mode": "REAL OPEN DATA (no key)",
            "lat": latitude, "lon": longitude,
        }
    except Exception as e:
        return {
            "temperature_c": None,
            "source": "open-meteo-current-failed",
            "status": "fallback",
            "data_mode": "SYNTHETIC FALLBACK (503 or network failure)",
            "error": str(e),
        }
