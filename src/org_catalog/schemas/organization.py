"""Pydantic schemas for organization resources."""

from pydantic import BaseModel, ConfigDict

from org_catalog.schemas.activity import ActivityBase
from org_catalog.schemas.building import Building


class OrganizationPhone(BaseModel):
    """Single organization phone entry."""

    id: int
    number: str
    label: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationBase(BaseModel):
    """Minimal representation of an organization."""

    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationSummary(OrganizationBase):
    """Organization summary including building reference."""

    building_id: int


class OrganizationDetailed(OrganizationBase):
    """Detailed organization representation with relations."""

    building: Building
    activities: list[ActivityBase]
    phones: list[OrganizationPhone]
