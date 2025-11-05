"""Shared pytest fixtures for API tests."""

import asyncio
import os
import uuid
from dataclasses import dataclass
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import URL
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from org_catalog.api.deps import get_db_session
from org_catalog.main import create_app

try:
    from testcontainers.postgres import PostgresContainer
except ImportError:  # pragma: no cover - guard for optional dependency
    PostgresContainer = None  # type: ignore[assignment]


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a dedicated event loop for the test session."""

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@dataclass
class DatabaseContext:
    """Holds information about database connection under test."""

    async_url: str
    admin_url: str
    managed: bool


def _ensure_async_url(url: str) -> str:
    sa_url = make_url(url)
    if sa_url.drivername.startswith("postgresql+asyncpg"):
        return url
    return URL.create(
        drivername="postgresql+asyncpg",
        username=sa_url.username,
        password=sa_url.password,
        host=sa_url.host,
        port=sa_url.port,
        database=sa_url.database,
    ).render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def api_key() -> str:
    """Return API key used for authenticated requests."""

    return os.getenv("ORG_CATALOG_API_KEY", "local-dev-key")


@pytest.fixture(scope="session")
def api_key_header(api_key: str) -> dict[str, str]:
    """Return HTTP header map with API key."""

    return {"X-API-Key": api_key}


def _admin_url(database_url: str) -> str:
    """Return admin connection URL targeting the postgres database."""

    url = make_url(database_url)
    admin_url = URL.create(
        drivername="postgresql",
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database="postgres",
    )
    return admin_url.render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def postgres_service() -> Generator[DatabaseContext, None, None]:
    """Provide database context, starting a container when needed."""

    env_url = os.getenv("ORG_CATALOG_TEST_DATABASE_URL")
    if env_url:
        async_url = _ensure_async_url(env_url)
        os.environ["ORG_CATALOG_TEST_DATABASE_URL"] = async_url
        yield DatabaseContext(async_url=async_url, admin_url=_admin_url(async_url), managed=False)
        return

    if PostgresContainer is None:  # pragma: no cover - safety net when dependency missing
        pytest.skip("testcontainers is not installed and no ORG_CATALOG_TEST_DATABASE_URL provided")

    container_name = f"test-db-{uuid.uuid4().hex[:8]}"
    with PostgresContainer("postgres:16-alpine", name=container_name) as container:
        sync_url = container.get_connection_url()
        async_url = _ensure_async_url(sync_url)
        os.environ["ORG_CATALOG_TEST_DATABASE_URL"] = async_url
        yield DatabaseContext(async_url=async_url, admin_url=_admin_url(async_url), managed=True)


@pytest.fixture(scope="session")
def test_database_url(postgres_service: DatabaseContext) -> str:
    """Return database URL for tests."""

    return postgres_service.async_url


@pytest.fixture(scope="session")
def alembic_config(test_database_url: str) -> Config:
    """Configure Alembic for the test database."""

    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", test_database_url)
    return config


@pytest.fixture(scope="session", autouse=True)
async def setup_database(
    postgres_service: DatabaseContext, test_database_url: str, alembic_config: Config
) -> AsyncGenerator[None, None]:
    """Create a fresh test database, run migrations, and tear it down afterwards."""

    url = make_url(test_database_url)
    database_name = url.database
    admin_dsn = postgres_service.admin_url

    conn = await asyncpg.connect(admin_dsn)
    try:
        await conn.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = $1",
            database_name,
        )
        await conn.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
        await conn.execute(f'CREATE DATABASE "{database_name}" TEMPLATE template0')
    finally:
        await conn.close()

    await asyncio.to_thread(command.upgrade, alembic_config, "head")

    try:
        yield
    finally:
        await asyncio.to_thread(command.downgrade, alembic_config, "base")
        if postgres_service.managed:
            conn = await asyncpg.connect(admin_dsn)
            try:
                await conn.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = $1",
                    database_name,
                )
                await conn.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
            finally:
                await conn.close()


@pytest.fixture(scope="session")
async def async_engine(test_database_url: str) -> AsyncGenerator[AsyncEngine, None]:
    """Provide an async SQLAlchemy engine for tests."""

    engine = create_async_engine(test_database_url, poolclass=NullPool)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def session_factory(async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Return an async session factory bound to the test engine."""

    return async_sessionmaker(async_engine, expire_on_commit=False)


@pytest.fixture
def app(session_factory: async_sessionmaker[AsyncSession]):
    """Create a FastAPI application with overridden DB dependency."""

    app = create_app()

    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = _get_session
    return app


@pytest.fixture
async def api_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Return an HTTPX async client with lifespan management."""

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
