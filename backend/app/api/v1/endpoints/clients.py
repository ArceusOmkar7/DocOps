"""API endpoints for Client management."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....models.client import Client
from ....models.enums import ClientStatus
from ....models.organization import Organization
from ....schemas.domain import ClientCreate, ClientRead, ClientUpdate
from ...deps import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
) -> Client:
    # Verify organization exists
    org_stmt = select(Organization).where(Organization.id == data.organization_id)
    org_res = await db.execute(org_stmt)
    if not org_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Organization not found")

    client = Client(
        organization_id=data.organization_id,
        name=data.name,
        tax_id=data.tax_id,
        email=data.email,
        phone=data.phone,
        contact_person=data.contact_person,
        status=data.status,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("", response_model=list[ClientRead])
async def list_clients(
    organization_id: uuid.UUID | None = Query(None),
    status_filter: ClientStatus | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
) -> list[Client]:
    stmt = select(Client)
    if organization_id:
        stmt = stmt.where(Client.organization_id == organization_id)
    if status_filter:
        stmt = stmt.where(Client.status == status_filter)
    stmt = stmt.order_by(Client.created_at.desc())

    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Client:
    stmt = select(Client).where(Client.id == client_id)
    res = await db.execute(stmt)
    client = res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: uuid.UUID,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
) -> Client:
    stmt = select(Client).where(Client.id == client_id)
    res = await db.execute(stmt)
    client = res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)

    await db.commit()
    await db.refresh(client)
    return client
