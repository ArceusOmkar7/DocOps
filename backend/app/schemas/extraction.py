"""Business extraction schemas — Phase 1 (Invoice only).

Design principle: model the BUSINESS ENTITY, not the OCR layout. Every invoice
has different positioning, but the same underlying concepts (seller, buyer,
line items, tax, total). These models capture those concepts and stay the same
regardless of how the source invoice looked.

Layering:
  Document           -> generic envelope every uploaded file gets (any doc type)
  Invoice            -> business schema, only populated when document_type == "invoice"

When BankStatement, Receipt, GSTReturn etc. are added later, they become new
sibling models next to Invoice. The Document envelope doesn't change.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared building blocks
# ---------------------------------------------------------------------------


class DocumentType(str, Enum):
    invoice = "invoice"
    receipt = "receipt"
    bank_statement = "bank_statement"
    purchase_order = "purchase_order"
    gst_return = "gst_return"
    unknown = "unknown"


class Address(BaseModel):
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class Company(BaseModel):
    """A seller or buyer on an invoice. Generic enough for any invoice format."""

    name: str | None = None
    address: Address | None = None
    tax_id: str | None = None  # GSTIN, VAT number, EIN, ABN — whatever the country uses
    email: str | None = None
    phone: str | None = None


class InvoiceItem(BaseModel):
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    tax_rate: float | None = None  # percentage, e.g. 18.0 for 18% GST
    line_total: float | None = None


class TaxBreakdown(BaseModel):
    """Country-specific tax fields, all optional. An Indian invoice fills
    CGST/SGST/IGST; a US invoice fills none and just uses `total_tax`; a
    European invoice fills `vat`."""

    cgst: float | None = None
    sgst: float | None = None
    igst: float | None = None
    vat: float | None = None
    other_tax_label: str | None = None  # e.g. "Sales Tax", "GST"
    other_tax_amount: float | None = None


# ---------------------------------------------------------------------------
# Layer 1 — generic envelope (every uploaded document gets one of these)
# ---------------------------------------------------------------------------


class Document(BaseModel):
    id: str
    source_filename: str
    document_type: DocumentType = DocumentType.unknown
    ocr_confidence: float | None = None  # average PaddleOCR block confidence
    raw_markdown: str  # what PaddleOCR produced — kept for debugging
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Downstream processing status
    extraction_status: str = "pending"  # pending | success | failed | needs_review
    needs_human_review: bool = False
    review_reason: str | None = None


# ---------------------------------------------------------------------------
# Layer 2 — business schema for invoices specifically
# ---------------------------------------------------------------------------


class Invoice(BaseModel):
    document_id: str  # foreign key back to Document.id

    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    purchase_order_ref: str | None = None

    seller: Company = Field(default_factory=Company)
    buyer: Company = Field(default_factory=Company)

    currency: str | None = None
    items: list[InvoiceItem] = Field(default_factory=list)

    subtotal: float | None = None
    tax: TaxBreakdown = Field(default_factory=TaxBreakdown)
    total_tax: float | None = None
    total: float | None = None
    amount_paid: float | None = None
    balance_due: float | None = None

    payment_terms: str | None = None
    notes: str | None = None

    # Set by the LLM extraction step, not the OCR step
    extraction_confidence: float | None = None


# ---------------------------------------------------------------------------
# Extraction result — envelope + optional business object
# ---------------------------------------------------------------------------


class DocumentExtraction(BaseModel):
    """What the LLM parse step returns for one uploaded document.

    `invoice` is None whenever `document.document_type` is not "invoice".
    """

    document: Document
    invoice: Invoice | None = None
