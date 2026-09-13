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

### Grid geometry and map alignment

The frontend derives the request bounds from the map's **actual visible
extent** at its locked view (`map.getBounds()` with a small margin), clamped to
the documented Antarctic window (latitude −89…−20, longitude −180…180). The
wind field therefore covers the whole visible map, not only the operational
rectangle, and particles reach the screen edges.

The backend builds a **uniform** grid covering exactly the requested bounds:
`ceil(span / spacing)` intervals per axis, the first row at the northern bound
and the last row landing exactly on the southern bound. This matters because
`leaflet-velocity` derives every row as `la1 − j·dy` with a single uniform
`dy` and never reads `la2`/`lo2`; an uneven final row would distort all
interpolation in that band. The declared `dx`/`dy` are the actual uniform
spacings, which may differ slightly per axis.

### Provider call budget

Open-Meteo counts every grid location as one API call against a free-tier
budget of 600 calls/minute (no key, no payment). One full field build must
stay below that budget, so the grid is capped at 550 points: if the requested
spacing would exceed it, the effective spacing is raised just enough to fit
(a pure function of the request, so caching stays sound). For the default
operational view this yields roughly a 3° grid (~476 points); smaller visible
extents resolve at the requested 2°. Batches of 64 locations are fetched by
four workers with one retry after a long backoff; rapid retries would only
feed the provider's rate limiter.

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
