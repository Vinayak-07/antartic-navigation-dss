"""Application entry point for the backend service."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import environment, icebergs, routes, sea_ice, trips, voyage, wind

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Antarctic Navigation Decision Support System",
    version="0.1.0",
    description="Synthetic scientific Antarctic voyage simulation prototype for sea-ice, iceberg, environment, and route decision support.",
)

app.include_router(voyage.router, prefix="/api", tags=["voyage"])
app.include_router(sea_ice.router, prefix="/api", tags=["sea-ice"])
app.include_router(icebergs.router, prefix="/api", tags=["icebergs"])
app.include_router(routes.router, prefix="/api", tags=["routes"])
app.include_router(environment.router, prefix="/api", tags=["environment"])
app.include_router(wind.router, prefix="/api", tags=["wind"])
app.include_router(trips.router, prefix="/api", tags=["trips"])


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the dashboard entry page for the browser."""
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="frontend_css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="frontend_js")


@app.get("/api/health")
def health_check():
    """Simple health endpoint for startup verification."""
    return {
        "status": "ok",
        "service": "antarctic-navigation-dss",
        "version": "0.1.0",
        "notes": "Synthetic scientific simulation prototype",
    }
