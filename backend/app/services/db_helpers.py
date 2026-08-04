"""Database helper utilities for auto-provisioning default tenant/client and syncing documents."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.client import Client
from ..models.document import Document
from ..models.enums import ClientStatus, DocumentStatus, DocumentType
from ..models.organization import Organization


async def get_or_create_default_organization(db: AsyncSession) -> Organization:
    """Fetch or create a default organization for tenant fallback."""
    stmt = select(Organization).where(Organization.slug == "default-org")
    res = await db.execute(stmt)
    org = res.scalar_one_or_none()
    if not org:
        org = Organization(
            name="Acme Accounting & Tax Advisory",
            slug="default-org",
            plan="pro",
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)
    return org


async def get_or_create_default_client(db: AsyncSession, organization_id: uuid.UUID) -> Client:
    """Fetch the primary existing client for this organization, or create one if none exists."""
    stmt = select(Client).where(Client.organization_id == organization_id).order_by(Client.created_at.asc())
    res = await db.execute(stmt)
    client = res.scalars().first()
    if not client:
        client = Client(
            organization_id=organization_id,
            name="General Client",
            tax_id="27ABCDE1234F1Z5",
            email="client@example.com",
            status=ClientStatus.on_track,
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)
    return client


async def save_extracted_document_to_db(
    db: AsyncSession,
    *,
    result_id: str,
    source_filename: str,
    document_type: str,
    extraction_status: str,
    needs_human_review: bool,
    review_reason: str | None,
    ocr_confidence: float | None,
    extracted_data: dict[str, Any] | None,
    metadata: dict[str, Any] | None,
    organization_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
) -> Document:
    """Create or update a Document row in PostgreSQL from an extraction result."""
    if not organization_id:
        org = await get_or_create_default_organization(db)
        organization_id = org.id
    if not client_id:
        client = await get_or_create_default_client(db, organization_id)
        client_id = client.id

    # Convert status string to enum
    status_map = {
        "success": DocumentStatus.extracted,
        "pending": DocumentStatus.processing,
        "needs_review": DocumentStatus.needs_review,
        "unsupported": DocumentStatus.needs_review,
        "failed": DocumentStatus.failed,
    }
    doc_status = status_map.get(extraction_status, DocumentStatus.extracted)
    if needs_human_review:
        doc_status = DocumentStatus.needs_review

    try:
        doc_type_enum = DocumentType(document_type)
    except ValueError:
        doc_type_enum = DocumentType.unknown

    # Check if document with this ocr_result_id already exists
    stmt = select(Document).where(Document.ocr_result_id == result_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if doc:
        doc.status = doc_status
        doc.document_type = doc_type_enum
        doc.ocr_confidence = ocr_confidence
        doc.needs_human_review = needs_human_review
        doc.review_reason = review_reason
        doc.extracted_data = extracted_data
        doc.metadata_ = metadata
        doc.processed_at = now
    else:
        doc = Document(
            organization_id=organization_id,
            client_id=client_id,
            source_filename=source_filename,
            ocr_result_id=result_id,
            document_type=doc_type_enum,
            status=doc_status,
            ocr_confidence=ocr_confidence,
            needs_human_review=needs_human_review,
            review_reason=review_reason,
            extracted_data=extracted_data,
            metadata_=metadata,
            uploaded_at=now,
            processed_at=now,
        )
        db.add(doc)

    await db.commit()
    await db.refresh(doc)
    return doc
