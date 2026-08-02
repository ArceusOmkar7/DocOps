"""WorkflowDocument — junction table linking documents to workflows."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, UUIDPrimaryKeyMixin


class WorkflowDocument(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "workflow_documents"

    __table_args__ = (
        UniqueConstraint("workflow_id", "document_id", name="uq_workflow_document"),
    )

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_document_requirements.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    workflow: Mapped["Workflow"] = relationship(  # noqa: F821
        back_populates="document_links",
    )
    document: Mapped["Document"] = relationship(  # noqa: F821
        back_populates="workflow_links",
    )
    requirement: Mapped["WorkflowDocumentRequirement | None"] = relationship(  # noqa: F821
        back_populates="fulfilled_by",
    )
