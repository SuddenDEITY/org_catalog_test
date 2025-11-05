"""Domain services for activity operations."""


from collections import defaultdict
from typing import Iterable

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from org_catalog.models.activity import Activity
from org_catalog.schemas.activity import ActivityTree

MAX_ACTIVITY_DEPTH = 3


class ActivityService:
    """Service layer for manipulating activities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def descendant_ids(self, activity_id: int) -> list[int]:
        """Return ids for the activity and all descendants."""

        base_query: Select[tuple[int]] = select(Activity.id).where(Activity.id == activity_id)
        cte = base_query.cte(name="activity_tree", recursive=True)
        cte = cte.union_all(
            select(Activity.id).where(Activity.parent_id == cte.c.id),
        )
        ids_result = await self._session.scalars(select(cte.c.id))
        return list(ids_result)

    async def build_tree(
        self,
        root_id: int | None = None,
        max_depth: int = MAX_ACTIVITY_DEPTH,
    ) -> list[ActivityTree]:
        """Return activity tree up to the specified depth."""

        result = await self._session.scalars(select(Activity))
        activities = list(result)
        adjacency: dict[int | None, list[Activity]] = defaultdict(list)
        activity_map: dict[int, Activity] = {}

        for activity in activities:
            adjacency[activity.parent_id].append(activity)
            activity_map[activity.id] = activity

        roots: Iterable[Activity]
        if root_id is None:
            roots = adjacency[None]
        else:
            activity = activity_map.get(root_id)
            if activity is None:
                return []
            roots = [activity]

        def build_node(node: Activity, current_depth: int) -> ActivityTree:
            if current_depth > max_depth:
                msg = f"Maximum activity depth of {max_depth} exceeded."
                raise ValueError(msg)
            children = [
                build_node(child, current_depth + 1) for child in adjacency.get(node.id, [])
            ]
            return ActivityTree.model_validate(
                {
                    "id": node.id,
                    "name": node.name,
                    "parent_id": node.parent_id,
                    "children": children,
                }
            )

        return [build_node(root, 1) for root in roots]

    async def get(self, activity_id: int) -> Activity | None:
        """Return a single activity by identifier."""

        statement = select(Activity).where(Activity.id == activity_id)
        result = await self._session.scalars(statement)
        return result.first()

    async def find_by_name(self, name: str) -> list[Activity]:
        """Return activities matching name case-insensitively."""

        if not name:
            return []
        pattern = f"%{name.lower()}%"
        statement = select(Activity).where(func.lower(Activity.name).like(pattern))
        result = await self._session.scalars(statement)
        return list(result)
