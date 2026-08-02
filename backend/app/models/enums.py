"""Database-level enum definitions shared across SQLAlchemy models.

These are PostgreSQL native ENUMs created via Alembic migrations.
They mirror the business-level enums from the implementation plan.
"""

from __future__ import annotations

import enum


# ---------------------------------------------------------------------------
# Document enums
# ---------------------------------------------------------------------------


class DocumentType(str, enum.Enum):
    """The kind of business document (used for classification + extraction)."""

    invoice = "invoice"
    receipt = "receipt"
    bank_statement = "bank_statement"
    purchase_order = "purchase_order"
    gst_return = "gst_return"
    unknown = "unknown"


class DocumentStatus(str, enum.Enum):
    """Lifecycle of one uploaded document through the processing pipeline."""

    uploaded = "uploaded"
    processing = "processing"
    extracted = "extracted"
    needs_review = "needs_review"
    validated = "validated"
    rejected = "rejected"
    failed = "failed"


# ---------------------------------------------------------------------------
# Workflow enums
# ---------------------------------------------------------------------------


class WorkflowType(str, enum.Enum):
    """The kind of business workflow (extensible as new verticals are added)."""

    gst_filing = "gst_filing"
    bookkeeping = "bookkeeping"
    tds_filing = "tds_filing"
    audit = "audit"
    payroll = "payroll"
    custom = "custom"


class WorkflowStatus(str, enum.Enum):
    """Progress of one business workflow."""

    collecting_documents = "collecting_documents"
    ready_for_review = "ready_for_review"
    in_review = "in_review"
    ready_for_filing = "ready_for_filing"
    completed = "completed"
    blocked = "blocked"


# ---------------------------------------------------------------------------
# Client enums
# ---------------------------------------------------------------------------


class ClientStatus(str, enum.Enum):
    """Operational state of a client (denormalized, recomputed on writes)."""

    on_track = "on_track"
    awaiting_documents = "awaiting_documents"
    review_required = "review_required"
    action_required = "action_required"
    completed = "completed"
