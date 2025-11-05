"""seed initial data

Revision ID: 601c81d00882
Revises: ef9196e388d2
Create Date: 2025-11-05 15:36:40.224824

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "601c81d00882"
down_revision: Union[str, Sequence[str], None] = "ef9196e388d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    activities = sa.table(
        "activities",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("parent_id", sa.Integer),
    )
    buildings = sa.table(
        "buildings",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("address", sa.String),
        sa.column("latitude", sa.Float),
        sa.column("longitude", sa.Float),
    )
    organizations = sa.table(
        "organizations",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("building_id", sa.Integer),
    )
    organization_phones = sa.table(
        "organization_phones",
        sa.column("id", sa.Integer),
        sa.column("organization_id", sa.Integer),
        sa.column("number", sa.String),
        sa.column("label", sa.String),
    )
    organization_activities = sa.table(
        "organization_activities",
        sa.column("organization_id", sa.Integer),
        sa.column("activity_id", sa.Integer),
    )

    op.bulk_insert(
        activities,
        [
            {"id": 1, "name": "Еда", "parent_id": None},
            {"id": 2, "name": "Мясная продукция", "parent_id": 1},
            {"id": 3, "name": "Молочная продукция", "parent_id": 1},
            {"id": 4, "name": "Автомобили", "parent_id": None},
            {"id": 5, "name": "Грузовые автомобили", "parent_id": 4},
            {"id": 6, "name": "Легковые автомобили", "parent_id": 4},
            {"id": 7, "name": "Запчасти", "parent_id": 6},
            {"id": 8, "name": "Аксессуары", "parent_id": 6},
        ],
    )

    op.bulk_insert(
        buildings,
        [
            {
                "id": 1,
                "name": "БЦ Ленина",
                "address": "г. Москва, ул. Ленина 1, офис 3",
                "latitude": 55.7522,
                "longitude": 37.6156,
            },
            {
                "id": 2,
                "name": "БЦ Аврора",
                "address": "г. Санкт-Петербург, Невский проспект 12",
                "latitude": 59.9316,
                "longitude": 30.3609,
            },
            {
                "id": 3,
                "name": "БЦ Сибирь",
                "address": "г. Новосибирск, ул. Блюхера 32/1",
                "latitude": 55.0415,
                "longitude": 82.9346,
            },
        ],
    )

    op.bulk_insert(
        organizations,
        [
            {
                "id": 1,
                "name": "ООО «Рога и Копыта»",
                "description": "Традиционные мясные и молочные продукты региона.",
                "building_id": 3,
            },
            {
                "id": 2,
                "name": "ООО «Молочная ферма»",
                "description": "Фермерская молочная продукция.",
                "building_id": 1,
            },
            {
                "id": 3,
                "name": "ООО «Мясная лавка»",
                "description": "Мясная продукция собственного производства.",
                "building_id": 1,
            },
            {
                "id": 4,
                "name": "ООО «АвтоМир»",
                "description": "Продажа и обслуживание легковых автомобилей.",
                "building_id": 2,
            },
            {
                "id": 5,
                "name": "ООО «ТракСервис»",
                "description": "Сервис и продажа грузовых автомобилей.",
                "building_id": 2,
            },
        ],
    )

    op.bulk_insert(
        organization_phones,
        [
            {"id": 1, "organization_id": 1, "number": "2-222-222", "label": "Приемная"},
            {"id": 2, "organization_id": 1, "number": "8-923-666-13-13", "label": "Партнеры"},
            {"id": 3, "organization_id": 2, "number": "3-333-333", "label": "Клиенты"},
            {"id": 4, "organization_id": 2, "number": "+7-913-111-22-33", "label": "Оптовый отдел"},
            {"id": 5, "organization_id": 3, "number": "+7-913-222-33-44", "label": "Магазин"},
            {"id": 6, "organization_id": 3, "number": "+7-913-333-44-55", "label": "Доставка"},
            {"id": 7, "organization_id": 4, "number": "+7-921-444-55-66", "label": "Продажи"},
            {"id": 8, "organization_id": 4, "number": "+7-921-555-66-77", "label": "Сервис"},
            {"id": 9, "organization_id": 5, "number": "+7-812-777-88-99", "label": "Приемка"},
            {"id": 10, "organization_id": 5, "number": "+7-812-999-00-11", "label": "24/7"},
        ],
    )

    op.bulk_insert(
        organization_activities,
        [
            {"organization_id": 1, "activity_id": 2},
            {"organization_id": 1, "activity_id": 3},
            {"organization_id": 2, "activity_id": 3},
            {"organization_id": 3, "activity_id": 2},
            {"organization_id": 4, "activity_id": 6},
            {"organization_id": 4, "activity_id": 7},
            {"organization_id": 4, "activity_id": 8},
            {"organization_id": 5, "activity_id": 5},
            {"organization_id": 5, "activity_id": 7},
        ],
    )

    op.execute(sa.text("SELECT setval('activities_id_seq', 8, true)"))
    op.execute(sa.text("SELECT setval('buildings_id_seq', 3, true)"))
    op.execute(sa.text("SELECT setval('organizations_id_seq', 5, true)"))
    op.execute(sa.text("SELECT setval('organization_phones_id_seq', 10, true)"))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text(
            "DELETE FROM organization_activities WHERE organization_id BETWEEN 1 AND 5"
        )
    )
    op.execute(
        sa.text("DELETE FROM organization_phones WHERE organization_id BETWEEN 1 AND 5")
    )
    op.execute(sa.text("DELETE FROM organizations WHERE id BETWEEN 1 AND 5"))
    op.execute(sa.text("DELETE FROM buildings WHERE id BETWEEN 1 AND 3"))
    op.execute(sa.text("DELETE FROM activities WHERE id BETWEEN 1 AND 8"))
    op.execute(sa.text("SELECT setval('activities_id_seq', 1, false)"))
    op.execute(sa.text("SELECT setval('buildings_id_seq', 1, false)"))
    op.execute(sa.text("SELECT setval('organizations_id_seq', 1, false)"))
    op.execute(sa.text("SELECT setval('organization_phones_id_seq', 1, false)"))
