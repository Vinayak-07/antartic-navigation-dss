# Wind particle layer

The map receives an animated U/V wind field from `GET /api/wind`. The browser
only renders this field with `leaflet-velocity`; it never calls the provider or
converts direction values itself.

## Data pipeline

`OpenMeteoWindProvider` → `meteorological_to_uv` → `WindFieldService` →
`/api/wind` → Leaflet velocity layer

Open-Meteo supplies 10 m wind speed and meteorological direction. The backend
converts the "from" direction to east/north velocity components. Grid rows are
assembled north to south, and both arrays are checked against `nx * ny`.

The service batches grid coordinates, uses a bounded in-memory cache, and
labels every response with source, valid time, grid dimensions, attribution,
and cache/staleness state. If a refresh fails, the most recent cached field is
returned only with `stale: true`; if none exists, the endpoint reports data
unavailable and the map continues without the particle layer.

The animated wind layer is numerical-weather-model forecast data, not a direct
observation. It is currently distinct from the deterministic environmental
field used by the vessel and iceberg simulation.

## Projection

The prototype uses Leaflet's EPSG:3857 base map, constrained to a Southern
Ocean operational view. This is a practical demo choice and introduces visible
polar distortion; no latitude or longitude values are altered to compensate.
A future EPSG:3031 migration requires a compatible tile source and validation
of all route, coastline, and interaction geometry.
