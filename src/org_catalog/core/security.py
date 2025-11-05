"""Security utilities for API key validation."""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from org_catalog.core.config import Settings, get_settings

API_KEY_HEADER_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def validate_api_key(
    provided_key: str | None = Depends(_api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    """Validate the provided API key against application settings."""

    if provided_key is None or provided_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return provided_key
