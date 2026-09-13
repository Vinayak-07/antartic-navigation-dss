# Data sources and development plan

## Planned scientific sources

- NOAA/NSIDC sea-ice concentration products
- Copernicus Marine Antarctic sea-ice products
- ECMWF weather reanalysis and forecast products
- U.S. National Ice Center iceberg observations

## Current repository state

- TODO: Define dataset-specific adapters.
- TODO: Add credential and API-key handling for external services.
- PLACEHOLDER: The project uses mock JSON compliant with eventual schemas.

## Development principle

Data ingestion is kept separate from prediction and routing logic to preserve modularity.
