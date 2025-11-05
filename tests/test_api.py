"""Integration tests for the Organization Catalog API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_health_check(api_client: AsyncClient) -> None:
    """Health endpoint should respond with status OK."""

    response = await api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_buildings_list(api_client: AsyncClient, api_key_header: dict[str, str]) -> None:
    """Buildings endpoint returns seeded buildings."""

    response = await api_client.get("/api/v1/buildings", headers=api_key_header)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    names = {item["name"] for item in payload}
    assert {"БЦ Ленина", "БЦ Аврора", "БЦ Сибирь"} <= names


async def test_organizations_by_activity(
    api_client: AsyncClient, api_key_header: dict[str, str]
) -> None:
    """Fetching organizations by root activity should include descendants."""

    response = await api_client.get(
        "/api/v1/organizations/by-activity/1",
        headers=api_key_header,
    )
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {
        "ООО «Рога и Копыта»",
        "ООО «Молочная ферма»",
        "ООО «Мясная лавка»",
    }


async def test_search_organization_by_name(
    api_client: AsyncClient, api_key_header: dict[str, str]
) -> None:
    """Search endpoint should be case-insensitive."""

    response = await api_client.get(
        "/api/v1/organizations/search/by-name",
        params={"query": "рога"},
        headers=api_key_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "ООО «Рога и Копыта»"


async def test_activity_tree(api_client: AsyncClient, api_key_header: dict[str, str]) -> None:
    """Activity tree endpoint returns expected hierarchy depth."""

    response = await api_client.get(
        "/api/v1/activities/tree",
        headers=api_key_header,
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2  # Еда, Автомобили
    food = next(item for item in payload if item["name"] == "Еда")
    assert len(food["children"]) == 2
