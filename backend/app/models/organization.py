"""Organization model — the SaaS tenant (accounting/services firm)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Organization(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="free")

    # Relationships
    clients: Mapped[list["Client"]] = relationship(  # noqa: F821
        back_populates="organization", lazy="selectin",
    )
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        back_populates="organization", lazy="selectin",
    )
    workflows: Mapped[list["Workflow"]] = relationship(  # noqa: F821
        back_populates="organization", lazy="selectin",
    )
