"""FastAPI application entrypoint."""

from fastapi import APIRouter, Depends, FastAPI

from org_catalog.api.routes import activities, buildings, organizations
from org_catalog.core.config import get_settings
from org_catalog.core.security import validate_api_key
from org_catalog.schemas import HealthStatus


def create_app() -> FastAPI:
    """Application factory for FastAPI."""

    settings = get_settings()
    app = FastAPI(
        title=settings.project_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    api_router = APIRouter(
        prefix="/api/v1",
        dependencies=[Depends(validate_api_key)],
    )
    api_router.include_router(buildings.router)
    api_router.include_router(activities.router)
    api_router.include_router(organizations.router)

    @app.get(
        "/health",
        response_model=HealthStatus,
        summary="Service health status",
        tags=["health"],
    )
    async def health_check() -> HealthStatus:
        """Return service health status."""

        return HealthStatus(status="ok")

    app.include_router(api_router)
    return app


app = create_app()
