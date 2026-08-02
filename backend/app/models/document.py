"""Document model — one uploaded file, its OCR result, and extracted data."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, UUIDPrimaryKeyMixin
from .enums import DocumentStatus, DocumentType


class Document(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "documents"

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
    source_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_result_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, unique=True,
        comment="Maps to existing backend/data/results/{id}/",
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type", native_enum=True),
        nullable=False,
        default=DocumentType.unknown,
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status", native_enum=True),
        nullable=False,
        default=DocumentStatus.uploaded,
    )

    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    needs_human_review: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSONB columns — extracted_data must be non-null once status reaches
    # extracted/needs_review/validated (enforced at the application layer).
    extracted_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True,
        comment="Technical pipeline metadata: page_count, ocr_engine, model, timing",
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        back_populates="documents",
    )
    client: Mapped["Client"] = relationship(  # noqa: F821
        back_populates="documents",
    )
    workflow_links: Mapped[list["WorkflowDocument"]] = relationship(  # noqa: F821
        back_populates="document", lazy="selectin",
    )
