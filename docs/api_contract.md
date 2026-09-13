# API contract

## Health

GET /api/health

Response:
{
  "status": "ok",
  "service": "antarctic-navigation-dss",
  "version": "0.1.0"
}

## Voyage analysis

POST /api/voyage/analyze

Request:
{
  "vessel": "RV Aurora",
  "origin": "Cape Town",
  "destination": "Bharati Station",
  "departure_time": "2026-01-15T06:00:00Z",
  "forecast_horizon_days": 10
}

Response:
{
  "voyage": {},
  "sea_ice": {},
  "icebergs": {},
  "environment": {},
  "routes": {}
}

## Sea-ice forecast

GET /api/sea-ice

Returns sea-ice concentration fields and forecast metadata.

## Iceberg observations

GET /api/icebergs

Returns iceberg positions and risk summary.

## Iceberg prediction

POST /api/icebergs/predict

Returns future positions and uncertainty metrics.

## Route optimization

POST /api/routes/optimize

Returns recommended, shortest, and low-risk alternatives.

## Environmental state

GET /api/environment

Returns weather, ocean, and sea-ice environmental state.

## Wind field

GET /api/wind

Optional query parameters: `south`, `north`, `west`, `east`, `spacing`, and
`refresh`. The endpoint returns a two-record GRIB-style U/V vector field for
the Leaflet particle renderer plus provenance metadata. Rows are always ordered
north to south; both component arrays have exactly `nx * ny` values.

The current provider is Open-Meteo's no-key numerical weather forecast. It is
kept separate from the deterministic voyage environment until the two fields
have been validated for shared scientific use. A cached response may be marked
`stale` if a provider refresh fails; no replacement field is invented.

## Contract notes

- The trip endpoints are the canonical source for the voyage simulation state.
- Several legacy single-purpose endpoints still return prototype examples and
  should not be used as the state source for an active trip.
