"""Database models for organizations and related entities."""


from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from org_catalog.db.base import Base

if TYPE_CHECKING:
    from org_catalog.models.activity import Activity
    from org_catalog.models.building import Building


organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Organization(Base):
    """Represents an organization stored in the catalog."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    building: Mapped["Building"] = relationship(back_populates="organizations")
    phones: Mapped[list["OrganizationPhone"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        secondary=organization_activities,
        back_populates="organizations",
    )


class OrganizationPhone(Base):
    """Stores organization phone numbers."""

    __tablename__ = "organization_phones"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "number",
            name="uq_organization_phone_number",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    number: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str | None] = mapped_column(String(64), nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="phones")
