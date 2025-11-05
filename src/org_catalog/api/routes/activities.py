"""Activity related API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from org_catalog.api.deps import get_activity_service
from org_catalog.schemas.activity import ActivityTree
from org_catalog.services.activity import ActivityService, MAX_ACTIVITY_DEPTH

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get(
    "/tree",
    response_model=list[ActivityTree],
    summary="Full activity tree",
    description="Возвращает дерево видов деятельности с ограничением по глубине.",
)
async def list_activity_tree(
    service: ActivityService = Depends(get_activity_service),
    max_depth: int = Query(MAX_ACTIVITY_DEPTH, ge=1, le=MAX_ACTIVITY_DEPTH),
) -> list[ActivityTree]:
    """Return full activity tree limited to the allowed depth."""

    return await service.build_tree(max_depth=max_depth)


@router.get(
    "/{activity_id}/tree",
    response_model=list[ActivityTree],
    summary="Subtree by activity",
    description="Возвращает поддерево видов деятельности, начиная с указанного узла.",
    responses={404: {"description": "Activity not found"}},
)
async def single_activity_tree(
    activity_id: int,
    service: ActivityService = Depends(get_activity_service),
    max_depth: int = Query(MAX_ACTIVITY_DEPTH, ge=1, le=MAX_ACTIVITY_DEPTH),
) -> list[ActivityTree]:
    """Return activity subtree for provided activity id."""

    if await service.get(activity_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity #{activity_id} not found.",
        )
    return await service.build_tree(root_id=activity_id, max_depth=max_depth)
