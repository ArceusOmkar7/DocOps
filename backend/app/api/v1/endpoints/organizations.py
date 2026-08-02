"""API endpoints for Organization management."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....models.organization import Organization
from ....schemas.domain import OrganizationCreate, OrganizationRead
from ...deps import get_db

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    # Check if slug exists
    stmt = select(Organization).where(Organization.slug == data.slug)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with slug '{data.slug}' already exists",
        )

    org = Organization(
        name=data.name,
        slug=data.slug,
        plan=data.plan,
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.get("", response_model=list[OrganizationRead])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
) -> list[Organization]:
    stmt = select(Organization).order_by(Organization.created_at.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    stmt = select(Organization).where(Organization.id == org_id)
    res = await db.execute(stmt)
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
