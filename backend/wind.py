"""Backend wind-field adapter for the Leaflet particle renderer.

The voyage model continues to use its deterministic environmental field.  This
module is deliberately separate: it supplies clearly labelled numerical
weather-model wind data for map visualization without changing iceberg forces.
"""

from __future__ import annotations

import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Mapping, Sequence, Tuple
from urllib.parse import urlencode
from urllib.request import urlopen


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_BOUNDS = {"south": -75.0, "north": -28.0, "west": 10.0, "east": 90.0}
DEFAULT_SPACING_DEG = 2.0
# Open-Meteo counts every grid location as one API call against a free-tier
# budget of 600 calls/minute, so one full field build must stay below it.
MAX_GRID_POINTS = 550
REQUEST_BATCH_SIZE = 64
PROVIDER_WORKERS = 4
PROVIDER_RETRIES = 1
PROVIDER_RETRY_DELAY = 15.0
CACHE_TTL_SECONDS = 30 * 60


class WindProviderError(RuntimeError):
    """Raised when a provider cannot return a complete, usable wind field."""


@dataclass(frozen=True)
class WindGridRequest:
    south: float = DEFAULT_BOUNDS["south"]
    north: float = DEFAULT_BOUNDS["north"]
    west: float = DEFAULT_BOUNDS["west"]
    east: float = DEFAULT_BOUNDS["east"]
    spacing: float = DEFAULT_SPACING_DEG

    def validate(self) -> "WindGridRequest":
        if not (-89.0 <= self.south < self.north <= -20.0):
            raise ValueError("Wind latitude bounds must be ordered Antarctic latitudes.")
        if not (-180.0 <= self.west < self.east <= 180.0):
            raise ValueError("Wind longitude bounds must be ordered between -180 and 180.")
        if not (1.0 <= self.spacing <= 8.0):
            raise ValueError("Wind grid spacing must be between 1 and 8 degrees.")
        return self

    def effective_spacing(self) -> float:
        """Raise the spacing just enough that the grid stays within the call budget.

        Large visible map extents and fine spacing would otherwise burst past the
        provider's per-minute limit.  The coarsening is a pure function of the
        request, so caching stays sound.
        """
        spacing = self.spacing
        while spacing < 32.0 and self._point_count(spacing) > MAX_GRID_POINTS:
            spacing = round(spacing + 0.25, 2)
        return spacing

    def _point_count(self, spacing: float) -> int:
        latitude_intervals, longitude_intervals = self._interval_counts(spacing)
        return (latitude_intervals + 1) * (longitude_intervals + 1)

    def _interval_counts(self, spacing: float) -> Tuple[int, int]:
        latitude_intervals = math.ceil(round(self.north - self.south, 9) / spacing)
        longitude_intervals = math.ceil(round(self.east - self.west, 9) / spacing)
        return max(1, latitude_intervals), max(1, longitude_intervals)

    def grid_axes(self) -> Tuple[List[float], List[float], float, float]:
        """Uniform latitude/longitude axes covering exactly the requested bounds.

        The renderer (leaflet-velocity) derives every row as ``la1 - j*dy`` with a
        single uniform ``dy`` and never reads ``la2``/``lo2``.  Uneven final rows
        would distort interpolation, so rows are distributed evenly and the last
        one lands exactly on the south/west bound.
        """
        spacing = self.effective_spacing()
        latitude_intervals, longitude_intervals = self._interval_counts(spacing)
        dy = (self.north - self.south) / latitude_intervals
        dx = (self.east - self.west) / longitude_intervals
        latitudes = [round(self.north - index * dy, 6) for index in range(latitude_intervals + 1)]
        longitudes = [round(self.west + index * dx, 6) for index in range(longitude_intervals + 1)]
        return latitudes, longitudes, dx, dy

    def cache_key(self) -> Tuple[float, float, float, float, float]:
        return tuple(round(value, 4) for value in (self.south, self.north, self.west, self.east, self.spacing))


def meteorological_to_uv(speed_m_s: float, direction_deg: float) -> Tuple[float, float]:
    """Convert a meteorological *from* direction into east/north components."""
    radians = math.radians(direction_deg)
    return (-speed_m_s * math.sin(radians), -speed_m_s * math.cos(radians))


class OpenMeteoWindProvider:
    """Small no-key adapter around the Open-Meteo forecast API."""

    name = "Open-Meteo"
    model = "numerical weather forecast"

    def fetch(self, points: Sequence[Tuple[float, float]]) -> List[Mapping[str, object]]:
        batches = [points[index:index + REQUEST_BATCH_SIZE] for index in range(0, len(points), REQUEST_BATCH_SIZE)]
        records: List[Mapping[str, object]] = []
        # Batches run concurrently; executor.map keeps the grid row order intact.
        with ThreadPoolExecutor(max_workers=PROVIDER_WORKERS) as executor:
            for batch_records in executor.map(self._fetch_batch, batches):
                records.extend(batch_records)
        return records

    def _fetch_batch(self, batch: Sequence[Tuple[float, float]]) -> List[Mapping[str, object]]:
        query = urlencode({
            "latitude": ",".join(_format_coordinate(lat) for lat, _ in batch),
            "longitude": ",".join(_format_coordinate(lon) for _, lon in batch),
            "current": "wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "ms",
            "timezone": "UTC",
        })
        last_error: Exception | None = None
        for attempt in range(PROVIDER_RETRIES + 1):
            if attempt:
                # A single long backoff lets a tripped per-minute window clear;
                # rapid retries would only feed the provider's rate limiter.
                time.sleep(PROVIDER_RETRY_DELAY)
            try:
                with urlopen(f"{OPEN_METEO_URL}?{query}", timeout=20) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception as exc:  # Transient limits must not break the layer; retry, then degrade.
                last_error = exc
                continue
            response_records = payload if isinstance(payload, list) else [payload]
            if len(response_records) != len(batch):
                raise WindProviderError("Open-Meteo returned an incomplete coordinate batch.")
            return response_records
        raise WindProviderError(f"Open-Meteo request failed: {last_error}")


def _format_coordinate(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


class WindFieldService:
    """Normalizes provider records, creates the renderer contract, and caches it."""

    def __init__(self, provider: OpenMeteoWindProvider | None = None, cache_ttl_seconds: int = CACHE_TTL_SECONDS):
        self.provider = provider or OpenMeteoWindProvider()
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[Tuple[float, float, float, float, float], Tuple[float, Dict[str, object]]] = {}
        self._lock = threading.Lock()

    def get_field(self, request: WindGridRequest, refresh: bool = False) -> Dict[str, object]:
        request = request.validate()
        key = request.cache_key()
        now = time.time()
        with self._lock:
            cached = self._cache.get(key)
        if cached and not refresh and now - cached[0] < self.cache_ttl_seconds:
            return self._with_cache_metadata(cached[1], cached_at=cached[0], cached=True, stale=False)

        try:
            field = self._build_field(request)
        except WindProviderError:
            if cached:
                return self._with_cache_metadata(cached[1], cached_at=cached[0], cached=True, stale=True)
            raise
        with self._lock:
            self._cache[key] = (now, field)
        return self._with_cache_metadata(field, cached_at=now, cached=False, stale=False)

    def _build_field(self, request: WindGridRequest) -> Dict[str, object]:
        latitudes, longitudes, dx, dy = request.grid_axes()
        points = [(latitude, longitude) for latitude in latitudes for longitude in longitudes]
        records = self.provider.fetch(points)
        u_values: List[float] = []
        v_values: List[float] = []
        valid_times: List[str] = []
        for record in records:
            current = record.get("current") if isinstance(record, Mapping) else None
            if not isinstance(current, Mapping):
                raise WindProviderError("Open-Meteo response omitted current wind values.")
            try:
                speed = float(current["wind_speed_10m"])
                direction = float(current["wind_direction_10m"])
            except (KeyError, TypeError, ValueError) as exc:
                raise WindProviderError("Open-Meteo returned invalid wind values.") from exc
            u_value, v_value = meteorological_to_uv(speed, direction)
            u_values.append(round(u_value, 5))
            v_values.append(round(v_value, 5))
            valid_time = current.get("time")
            if isinstance(valid_time, str):
                valid_times.append(valid_time)
        expected_count = len(latitudes) * len(longitudes)
        if len(u_values) != expected_count or len(v_values) != expected_count:
            raise WindProviderError("Wind field array length does not match its declared grid.")
        valid_time = valid_times[0] if valid_times else None
        reference_time = _as_iso_timestamp(valid_time)
        common_header = {
            "la1": latitudes[0], "lo1": longitudes[0],
            "la2": latitudes[-1], "lo2": longitudes[-1],
            "dx": round(dx, 6), "dy": round(dy, 6),
            "nx": len(longitudes), "ny": len(latitudes),
            "refTime": reference_time, "forecastTime": 0,
        }
        return {
            "field": [
                {"header": {**common_header, "parameterCategory": 2, "parameterNumber": 2}, "data": u_values},
                {"header": {**common_header, "parameterCategory": 2, "parameterNumber": 3}, "data": v_values},
            ],
            "metadata": {
                "source": self.provider.name,
                "model": self.provider.model,
                "variable": "10 m wind speed and meteorological direction",
                "data_kind": "forecast-model",
                "valid_time": reference_time,
                "bounds": {"south": request.south, "north": request.north, "west": request.west, "east": request.east},
                "grid_spacing_deg": {"lat": round(dy, 3), "lon": round(dx, 3)},
                "requested_spacing_deg": request.spacing,
                "nx": len(longitudes), "ny": len(latitudes),
                "row_order": "north_to_south",
                "units": "m/s",
                "attribution": "Weather data by Open-Meteo.com (CC BY 4.0)",
            },
        }

    @staticmethod
    def _with_cache_metadata(field: Mapping[str, object], cached_at: float, cached: bool, stale: bool) -> Dict[str, object]:
        response = {**field, "metadata": {**dict(field["metadata"]), "fetched_at": datetime.fromtimestamp(cached_at, timezone.utc).isoformat(), "cached": cached, "stale": stale}}
        return response


def _as_iso_timestamp(value: str | None) -> str:
    if not value:
        return datetime.now(timezone.utc).isoformat()
    if value.endswith("Z"):
        return value
    return f"{value}Z"
