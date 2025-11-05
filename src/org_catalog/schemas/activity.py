"""Pydantic schemas for activity resources."""


from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    """Base representation of an activity."""

    id: int
    name: str
    parent_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ActivityTree(ActivityBase):
    """Activity with nested children for tree representation."""

    children: list["ActivityTree"] = Field(default_factory=list)
