"""Shared Pydantic schemas used across the API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthStatus(BaseModel):
    """Service health information."""

    status: Literal["ok"] = Field(description="Current health state of the API service.")

    model_config = ConfigDict(json_schema_extra={"example": {"status": "ok"}})
