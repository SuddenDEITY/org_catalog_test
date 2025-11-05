"""Organization related API routes."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, status

from org_catalog.api.deps import (
    get_activity_service,
    get_building_service,
    get_organization_service,
)
from org_catalog.schemas.organization import OrganizationDetailed
from org_catalog.services.activity import ActivityService
from org_catalog.services.organization import BuildingService, OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _convert(organization):
    """Convert ORM organization to schema."""

    return OrganizationDetailed.model_validate(organization)


@router.get(
    "/{organization_id}",
    response_model=OrganizationDetailed,
    summary="Get organization by id",
    description="Возвращает подробную информацию об организации.",
    responses={404: {"description": "Organization not found"}},
)
async def get_organization(
    organization_id: int,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationDetailed:
    """Return organization by id."""

    organization = await service.get(organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization #{organization_id} not found.",
        )
    return _convert(organization)


@router.get(
    "/by-building/{building_id}",
    response_model=list[OrganizationDetailed],
    summary="Organizations in building",
    description="Возвращает все организации, расположенные в указанном здании.",
    responses={404: {"description": "Building not found"}},
)
async def organizations_by_building(
    building_id: int,
    organization_service: OrganizationService = Depends(get_organization_service),
    building_service: BuildingService = Depends(get_building_service),
) -> list[OrganizationDetailed]:
    """Return organizations for the provided building."""

    if await building_service.get(building_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building #{building_id} not found.",
        )
    organizations = await organization_service.by_building(building_id)
    return [_convert(org) for org in organizations]


@router.get(
    "/by-activity/{activity_id}",
    response_model=list[OrganizationDetailed],
    summary="Organizations by activity id",
    description=(
        "Возвращает организации, связанные с видом деятельности и его потомками."
    ),
    responses={404: {"description": "Activity not found"}},
)
async def organizations_by_activity(
    activity_id: int,
    organization_service: OrganizationService = Depends(get_organization_service),
    activity_service: ActivityService = Depends(get_activity_service),
) -> list[OrganizationDetailed]:
    """Return organizations for the activity including descendants."""

    activity = await activity_service.get(activity_id)
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity #{activity_id} not found.",
        )
    descendant_ids = await activity_service.descendant_ids(activity_id)
    organizations = await organization_service.by_activity_ids(descendant_ids)
    return [_convert(org) for org in organizations]


@router.get(
    "/search/by-activity",
    response_model=list[OrganizationDetailed],
    summary="Search organizations by activity name",
    description=(
        "Ищет организации по названию вида деятельности, учитывая вложенные уровни."
    ),
)
async def organizations_by_activity_name(
    name: str = Query(..., description="Activity name to search for. Partial matches allowed."),
    organization_service: OrganizationService = Depends(get_organization_service),
    activity_service: ActivityService = Depends(get_activity_service),
) -> list[OrganizationDetailed]:
    """Return organizations that match the activity name tree search."""

    activities = await activity_service.find_by_name(name)
    activity_ids: set[int] = set()
    for activity in activities:
        descendants = await activity_service.descendant_ids(activity.id)
        activity_ids.update(descendants)
    organizations = await organization_service.by_activity_ids(sorted(activity_ids))
    return [_convert(org) for org in organizations]


@router.get(
    "/search/by-name",
    response_model=list[OrganizationDetailed],
    summary="Search organizations by name",
    description="Ищет организации по названию (регистр игнорируется).",
)
async def organizations_by_name(
    query: str = Query(..., min_length=2, description="Organization search query."),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationDetailed]:
    """Return organizations filtered by name."""

    organizations = await organization_service.search_by_name(query)
    return [_convert(org) for org in organizations]


@router.get(
    "/geo",
    response_model=list[OrganizationDetailed],
    summary="Search organizations by geo",
    description=(
        "Возвращает организации по координатам: в радиусе или прямоугольной области."
    ),
)
async def organizations_by_geo(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Center latitude."),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Center longitude."),
    radius_km: float | None = Query(
        None,
        gt=0,
        description="Radius in kilometers. Provide either radius or bounding box.",
    ),
    min_latitude: float | None = Query(None, ge=-90.0, le=90.0),
    max_latitude: float | None = Query(None, ge=-90.0, le=90.0),
    min_longitude: float | None = Query(None, ge=-180.0, le=180.0),
    max_longitude: float | None = Query(None, ge=-180.0, le=180.0),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationDetailed]:
    """Return organizations by geographic filters."""

    if radius_km is not None:
        organizations = await organization_service.in_radius(latitude, longitude, radius_km)
        return [_convert(org) for org in organizations]

    if None in {min_latitude, max_latitude, min_longitude, max_longitude}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either radius_km or all bounding box parameters.",
        )
    if min_latitude > max_latitude or min_longitude > max_longitude:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Minimum coordinates must be less than maximum coordinates.",
        )
    organizations = await organization_service.in_rectangle(
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
    )
    return [_convert(org) for org in organizations]
