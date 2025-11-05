"""Building related API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from org_catalog.api.deps import get_building_service
from org_catalog.schemas.building import Building
from org_catalog.services.organization import BuildingService

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get(
    "",
    response_model=list[Building],
    summary="List catalog buildings",
    description="Возвращает все здания, доступные в справочнике.",
)
async def list_buildings(
    service: BuildingService = Depends(get_building_service),
) -> list[Building]:
    """Return catalog buildings."""

    return await service.list()


@router.get(
    "/{building_id}",
    response_model=Building,
    summary="Get building by id",
    description="Возвращает информацию о конкретном здании.",
    responses={404: {"description": "Building not found"}},
)
async def get_building(
    building_id: int,
    service: BuildingService = Depends(get_building_service),
) -> Building:
    """Return single building by identifier."""

    building = await service.get(building_id)
    if building is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building #{building_id} not found.",
        )
    return building
