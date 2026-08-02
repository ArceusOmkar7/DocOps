"""Domain API schemas for Organizations, Clients, Workflows, and Documents."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..models.enums import (
    ClientStatus,
    DocumentStatus,
    DocumentType,
    WorkflowStatus,
    WorkflowType,
)


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    plan: str = Field("free", max_length=50)


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    plan: str
    created_at: datetime
    updated_at: datetime | None = None


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class ClientCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    tax_id: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    contact_person: str | None = Field(None, max_length=255)
    status: ClientStatus = ClientStatus.on_track


class ClientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    tax_id: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    contact_person: str | None = Field(None, max_length=255)
    status: ClientStatus | None = None


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    tax_id: str | None = None
    email: str | None = None
    phone: str | None = None
    contact_person: str | None = None
    status: ClientStatus
    created_at: datetime
    updated_at: datetime | None = None


# ---------------------------------------------------------------------------
# Workflow & Requirement
# ---------------------------------------------------------------------------


class WorkflowRequirementCreate(BaseModel):
    document_type: DocumentType
    label: str = Field(..., min_length=1, max_length=255)
    required_count: int | None = Field(None, ge=1)
    notes: str | None = None


class WorkflowRequirementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workflow_id: uuid.UUID
    document_type: DocumentType
    label: str
    required_count: int | None = None
    notes: str | None = None


class WorkflowCreate(BaseModel):
    organization_id: uuid.UUID
    client_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    workflow_type: WorkflowType
    period_start: date
    period_end: date
    requirements: list[WorkflowRequirementCreate] = []


class WorkflowUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    status: WorkflowStatus | None = None
    closed_at: datetime | None = None


class WorkflowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    name: str
    workflow_type: WorkflowType
    period_start: date
    period_end: date
    status: WorkflowStatus
    created_at: datetime
    closed_at: datetime | None = None
    requirements: list[WorkflowRequirementRead] = []


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------


class DocumentCreate(BaseModel):
    organization_id: uuid.UUID
    client_id: uuid.UUID
    source_filename: str
    file_path: str | None = None
    ocr_result_id: str | None = None
    document_type: DocumentType = DocumentType.unknown


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID
    source_filename: str
    file_path: str | None = None
    ocr_result_id: str | None = None
    document_type: DocumentType
    status: DocumentStatus
    ocr_confidence: float | None = None
    extraction_confidence: float | None = None
    needs_human_review: bool
    review_reason: str | None = None
    extracted_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = Field(None, alias="metadata_")
    uploaded_at: datetime
    processed_at: datetime | None = None


class DocumentAttachToWorkflow(BaseModel):
    workflow_id: uuid.UUID
    requirement_id: uuid.UUID | None = None
