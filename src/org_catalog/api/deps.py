"""Common dependencies for FastAPI routes."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from org_catalog.db.session import SessionLocal
from org_catalog.services.activity import ActivityService
from org_catalog.services.organization import BuildingService, OrganizationService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session."""

    async with SessionLocal() as session:
        yield session


def get_organization_service(
    db: AsyncSession = Depends(get_db_session),
) -> OrganizationService:
    """Return configured organization service instance."""

    return OrganizationService(db)


def get_building_service(
    db: AsyncSession = Depends(get_db_session),
) -> BuildingService:
    """Return configured building service instance."""

    return BuildingService(db)


def get_activity_service(
    db: AsyncSession = Depends(get_db_session),
) -> ActivityService:
    """Return configured activity service instance."""

    return ActivityService(db)
