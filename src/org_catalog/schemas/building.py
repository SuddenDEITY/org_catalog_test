"""Pydantic schemas for building resources."""

from pydantic import BaseModel, ConfigDict


class Building(BaseModel):
    """Building description returned by the API."""

    id: int
    name: str
    address: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)
