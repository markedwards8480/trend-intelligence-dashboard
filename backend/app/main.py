import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.models.database import create_tables
from app.api import trends, moodboards, monitoring, dashboard, sources

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup and shutdown."""
    # Startup
    create_tables()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for tracking fashion trends for junior customers",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(trends.router)
app.include_router(moodboards.router)
app.include_router(monitoring.router)
app.include_router(dashboard.router)
app.include_router(sources.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Serve React frontend as static files
STATIC_DIR = Path(__file__).parent.parent / "static"

if STATIC_DIR.exists():
    # Mount static assets (JS, CSS) at /assets
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static-assets")

    # Catch-all route: serve index.html for any non-API route (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve the React SPA for any non-API route."""
        # If the path starts with 'api', let it 404 naturally
        if full_path.startswith("api"):
            return {"detail": "Not Found"}

        # Check if the file exists in static directory
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # Default: serve index.html for SPA client-side routing
        return FileResponse(str(STATIC_DIR / "index.html"))
else:
    # No frontend built — show API info at root
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
