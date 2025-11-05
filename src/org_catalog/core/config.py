"""Application configuration utilities."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Container for application configuration sourced from environment variables."""

    project_name: str = "Organization Catalog API"
    api_key: str = "local-dev-key"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/org_catalog"
    test_database_url: str | None = None
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="ORG_CATALOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()
