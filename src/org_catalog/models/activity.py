"""Database model for organization activities."""


from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from org_catalog.db.base import Base

if TYPE_CHECKING:
    from org_catalog.models.organization import Organization


class Activity(Base):
    """Represents a hierarchical activity classification."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
    )

    parent: Mapped[Optional["Activity"]] = relationship(
        remote_side="Activity.id",
        back_populates="children",
    )
    children: Mapped[list["Activity"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        secondary="organization_activities",
        back_populates="activities",
    )
