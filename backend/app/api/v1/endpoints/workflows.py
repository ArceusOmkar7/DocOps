"""API endpoints for Workflow and Requirement management."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....models.client import Client
from ....models.enums import WorkflowStatus
from ....models.workflow import Workflow
from ....models.workflow_document_requirement import WorkflowDocumentRequirement
from ....schemas.domain import WorkflowCreate, WorkflowRead, WorkflowUpdate
from ...deps import get_db

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
) -> Workflow:
    # Verify client exists
    client_stmt = select(Client).where(Client.id == data.client_id)
    client_res = await db.execute(client_stmt)
    if not client_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")

    workflow = Workflow(
        organization_id=data.organization_id,
        client_id=data.client_id,
        name=data.name,
        workflow_type=data.workflow_type,
        period_start=data.period_start,
        period_end=data.period_end,
        status=WorkflowStatus.collecting_documents,
    )
    db.add(workflow)
    await db.flush()  # assign workflow.id

    for req_data in data.requirements:
        req = WorkflowDocumentRequirement(
            workflow_id=workflow.id,
            document_type=req_data.document_type,
            label=req_data.label,
            required_count=req_data.required_count,
            notes=req_data.notes,
        )
        db.add(req)

    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.get("", response_model=list[WorkflowRead])
async def list_workflows(
    client_id: uuid.UUID | None = Query(None),
    organization_id: uuid.UUID | None = Query(None),
    status_filter: WorkflowStatus | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
) -> list[Workflow]:
    stmt = select(Workflow)
    if client_id:
        stmt = stmt.where(Workflow.client_id == client_id)
    if organization_id:
        stmt = stmt.where(Workflow.organization_id == organization_id)
    if status_filter:
        stmt = stmt.where(Workflow.status == status_filter)
    stmt = stmt.order_by(Workflow.created_at.desc())

    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Workflow:
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    res = await db.execute(stmt)
    workflow = res.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowRead)
async def update_workflow(
    workflow_id: uuid.UUID,
    data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
) -> Workflow:
    stmt = select(Workflow).where(Workflow.id == workflow_id)
    res = await db.execute(stmt)
    workflow = res.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workflow, key, value)

    await db.commit()
    await db.refresh(workflow)
    return workflow
