"""WorkflowDocumentRequirement — what documents are needed for a workflow."""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, UUIDPrimaryKeyMixin
from .enums import DocumentType


class WorkflowDocumentRequirement(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "workflow_document_requirements"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type", native_enum=True, create_type=False),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Human-readable label, e.g. 'Purchase Invoices'",
    )
    required_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="How many are needed; NULL = open-ended (any number)",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    workflow: Mapped["Workflow"] = relationship(  # noqa: F821
        back_populates="requirements",
    )
    fulfilled_by: Mapped[list["WorkflowDocument"]] = relationship(  # noqa: F821
        back_populates="requirement", lazy="selectin",
    )
