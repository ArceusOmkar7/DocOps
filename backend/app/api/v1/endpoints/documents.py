"""API endpoints for Document database operations and workflow linking."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....models.document import Document
from ....models.enums import DocumentStatus, DocumentType
from ....models.workflow import Workflow
from ....models.workflow_document import WorkflowDocument
from ....schemas.domain import DocumentAttachToWorkflow, DocumentRead
from ...deps import get_db

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    client_id: uuid.UUID | None = Query(None),
    organization_id: uuid.UUID | None = Query(None),
    document_type: DocumentType | None = Query(None),
    status_filter: DocumentStatus | None = Query(None, alias="status"),
    needs_review: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    stmt = select(Document)
    if client_id:
        stmt = stmt.where(Document.client_id == client_id)
    if organization_id:
        stmt = stmt.where(Document.organization_id == organization_id)
    if document_type:
        stmt = stmt.where(Document.document_type == document_type)
    if status_filter:
        stmt = stmt.where(Document.status == status_filter)
    if needs_review is not None:
        stmt = stmt.where(Document.needs_human_review == needs_review)

    stmt = stmt.order_by(Document.uploaded_at.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Document:
    stmt = select(Document).where(Document.id == document_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{document_id}/attach", status_code=status.HTTP_201_CREATED)
async def attach_document_to_workflow(
    document_id: uuid.UUID,
    data: DocumentAttachToWorkflow,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    # Check document exists
    doc_stmt = select(Document).where(Document.id == document_id)
    doc_res = await db.execute(doc_stmt)
    if not doc_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")

    # Check workflow exists
    wf_stmt = select(Workflow).where(Workflow.id == data.workflow_id)
    wf_res = await db.execute(wf_stmt)
    if not wf_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check if link already exists
    link_stmt = select(WorkflowDocument).where(
        WorkflowDocument.workflow_id == data.workflow_id,
        WorkflowDocument.document_id == document_id,
    )
    link_res = await db.execute(link_stmt)
    if link_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is already attached to this workflow",
        )

    link = WorkflowDocument(
        workflow_id=data.workflow_id,
        document_id=document_id,
        requirement_id=data.requirement_id,
    )
    db.add(link)
    await db.commit()
    return {"message": "Document attached to workflow successfully"}
