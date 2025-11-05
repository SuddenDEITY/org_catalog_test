"""Domain services for organization related operations."""


from typing import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from org_catalog.models.building import Building
from org_catalog.models.organization import Organization, organization_activities
from org_catalog.services.geolocation import bounding_box, haversine_distance_km


class OrganizationService:
    """Service class encapsulating organization queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, organization_id: int) -> Organization | None:
        """Return organization by id with related data."""

        statement = (
            select(Organization)
            .where(Organization.id == organization_id)
            .options(
                joinedload(Organization.building),
                joinedload(Organization.activities),
                joinedload(Organization.phones),
            )
        )
        result = await self._session.execute(statement)
        return result.unique().scalars().first()

    async def by_building(self, building_id: int) -> list[Organization]:
        """Return organizations located in the specified building."""

        statement = (
            select(Organization)
            .where(Organization.building_id == building_id)
            .options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
        )
        result = await self._session.execute(statement)
        return result.unique().scalars().all()

    async def by_activity_ids(self, activity_ids: Sequence[int]) -> list[Organization]:
        """Return organizations linked to any of the provided activities."""

        if not activity_ids:
            return []
        statement = (
            select(Organization)
            .join(organization_activities)
            .where(organization_activities.c.activity_id.in_(activity_ids))
            .options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
            .distinct()
        )
        result = await self._session.execute(statement)
        return result.unique().scalars().all()

    async def search_by_name(self, query: str) -> list[Organization]:
        """Perform a case-insensitive search by organization name."""

        if not query:
            return []

        pattern = f"%{query.lower()}%"
        statement = (
            select(Organization)
            .where(func.lower(Organization.name).like(pattern))
            .options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
        )
        result = await self._session.execute(statement)
        return result.unique().scalars().all()

    async def in_radius(self, latitude: float, longitude: float, radius_km: float) -> list[Organization]:
        """Return organizations within the given radius (km) from the point."""

        min_lat, max_lat, min_lon, max_lon = bounding_box(latitude, longitude, radius_km)
        candidates = await self.in_rectangle(min_lat, max_lat, min_lon, max_lon)

        return [
            org
            for org in candidates
            if org.building
            and haversine_distance_km(
                latitude,
                longitude,
                org.building.latitude,
                org.building.longitude,
            )
            <= radius_km
        ]

    async def in_rectangle(
        self,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
    ) -> list[Organization]:
        """Return organizations within the bounding box defined by coordinates."""

        statement = (
            select(Organization)
            .join(Building)
            .where(
                and_(
                    Building.latitude >= min_latitude,
                    Building.latitude <= max_latitude,
                    Building.longitude >= min_longitude,
                    Building.longitude <= max_longitude,
                )
            )
            .options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
        )
        result = await self._session.execute(statement)
        return result.unique().scalars().all()


class BuildingService:
    """Service for building related queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self) -> list[Building]:
        """Return all buildings."""

        statement = select(Building)
        result = await self._session.scalars(statement)
        return list(result)

    async def get(self, building_id: int) -> Building | None:
        """Return building by id."""

        statement = select(Building).where(Building.id == building_id)
        result = await self._session.scalars(statement)
        return result.first()
