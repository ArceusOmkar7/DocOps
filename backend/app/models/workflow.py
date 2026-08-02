"""Workflow model — one business workflow for a client."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, UUIDPrimaryKeyMixin
from .enums import WorkflowStatus, WorkflowType


class Workflow(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "workflows"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    workflow_type: Mapped[WorkflowType] = mapped_column(
        Enum(WorkflowType, name="workflow_type", native_enum=True),
        nullable=False,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus, name="workflow_status", native_enum=True),
        nullable=False,
        default=WorkflowStatus.collecting_documents,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        back_populates="workflows",
    )
    client: Mapped["Client"] = relationship(  # noqa: F821
        back_populates="workflows",
    )
    requirements: Mapped[list["WorkflowDocumentRequirement"]] = relationship(  # noqa: F821
        back_populates="workflow", lazy="selectin", cascade="all, delete-orphan",
    )
    document_links: Mapped[list["WorkflowDocument"]] = relationship(  # noqa: F821
        back_populates="workflow", lazy="selectin", cascade="all, delete-orphan",
    )
