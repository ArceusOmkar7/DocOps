"""Business extraction schemas — Phase 1 (multi-document family).

Design principle: model the BUSINESS ENTITY, not the OCR layout. Every invoice
has different positioning, but the same underlying concepts (seller, buyer,
line items, tax, total). These models capture those concepts and stay the same
regardless of how the source invoice looked.

Layering:
  Document           -> generic envelope every uploaded file gets (any doc type)
  Invoice            -> business schema, only populated when document_type == "invoice"
  BankStatement      -> business schema for bank statements ("bank_statement")
  GSTReturn          -> business schema for GSTR-1 / GSTR-3B / GSTR-2B ("gst_return")
  TDSForm            -> business schema for Form 16/16A/26AS/AIS/TIS ("tds_form")
  InvestmentProof    -> business schema for Chapter VI-A proofs ("investment_proof")

The Document envelope doesn't change; each new document family adds a sibling
business model next to Invoice.
"""

from __future__ import annotations

import datetime as dt
from datetime import date, datetime, timezone
from enum import Enum
from typing import Literal

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
    tds_form = "tds_form"
    investment_proof = "investment_proof"
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
    # pending | success | failed | needs_review | unsupported
    extraction_status: str = "pending"
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
# Layer 2 — business schema for bank statements
# ---------------------------------------------------------------------------


class BankTransaction(BaseModel):
    # NOTE: annotated via the datetime module alias because a plain `date`
    # annotation would be shadowed by this field's own name (`date`) when
    # Pydantic resolves the stringified hint.
    date: dt.date | None = None
    description: str | None = None
    cheque_ref_no: str | None = None
    debit: float | None = None
    credit: float | None = None
    balance: float | None = None
    category: str | None = None  # e.g. "vendor_payment", "salary", "utility"


class BankStatement(BaseModel):
    document_id: str  # foreign key back to Document.id

    account_number: str | None = None
    bank_name: str | None = None
    ifsc_code: str | None = None
    account_holder: str | None = None

    period_start: date | None = None
    period_end: date | None = None

    opening_balance: float | None = None
    closing_balance: float | None = None
    currency: str | None = None

    transactions: list[BankTransaction] = Field(default_factory=list)

    # Set by the LLM extraction step, not the OCR step
    extraction_confidence: float | None = None


# ---------------------------------------------------------------------------
# Layer 2 — business schema for GST returns (GSTR-1 / GSTR-3B / GSTR-2B)
# ---------------------------------------------------------------------------


class TaxAmountSummary(BaseModel):
    """IGST/CGST/SGST/Cess amounts in rupees (all optional)."""

    igst: float | None = None
    cgst: float | None = None
    sgst: float | None = None
    cess: float | None = None


class ITCBreakdown(BaseModel):
    """Input Tax Credit as reported on the return."""

    igst: float | None = None
    cgst: float | None = None
    sgst: float | None = None
    cess: float | None = None
    total: float | None = None


class GSTReturn(BaseModel):
    document_id: str  # foreign key back to Document.id

    return_type: Literal["GSTR-1", "GSTR-3B", "GSTR-2B", "GSTR-9", "GSTR-9C"] | None = None
    gstin: str | None = None
    return_period: str | None = None  # MM-YYYY, e.g. "08-2026"
    filing_date: date | None = None
    arn_number: str | None = None  # ARN from the GST portal

    legal_name: str | None = None
    trade_name: str | None = None

    taxable_turnover: float | None = None
    outward_tax_summary: TaxAmountSummary = Field(default_factory=TaxAmountSummary)

    itc_available: ITCBreakdown = Field(default_factory=ITCBreakdown)
    itc_reversed: ITCBreakdown = Field(default_factory=ITCBreakdown)
    net_itc: ITCBreakdown = Field(default_factory=ITCBreakdown)

    # Set by the LLM extraction step, not the OCR step
    extraction_confidence: float | None = None


# ---------------------------------------------------------------------------
# Layer 2 — business schema for TDS forms (16 / 16A / 26AS / AIS / TIS)
# ---------------------------------------------------------------------------


class TDSSectionDeduction(BaseModel):
    """One TDS deduction row keyed by section code (e.g. 194C, 194J, 192)."""

    section_code: str | None = None
    amount_paid_credited: float | None = None
    tds_deducted: float | None = None
    tds_deposited: float | None = None


TDSFormKind = Literal["Form 16", "Form 16A", "Form 26AS", "AIS", "TIS"]


class TDSForm(BaseModel):
    document_id: str  # foreign key back to Document.id

    form_type: TDSFormKind | None = None
    pan: str | None = None  # deductee PAN
    tan_of_deductor: str | None = None
    deductor_name: str | None = None
    assessment_year: str | None = None  # e.g. "2026-27"
    financial_year: str | None = None  # e.g. "2025-26"

    gross_salary: float | None = None  # Form 16 (salaried)
    total_amount_credited: float | None = None  # non-salary forms
    total_tds_deducted: float | None = None
    total_tds_deposited: float | None = None

    section_deductions: list[TDSSectionDeduction] = Field(default_factory=list)

    # Set by the LLM extraction step, not the OCR step
    extraction_confidence: float | None = None


# ---------------------------------------------------------------------------
# Layer 2 — business schema for Chapter VI-A investment proofs
# ---------------------------------------------------------------------------


InvestmentSection = Literal["80C", "80CCC", "80CCD", "80CCD(1B)", "80D", "80DD", "80DDB", "80E", "80G", "80TTA", "80TTB", "24b"]


class InvestmentProof(BaseModel):
    document_id: str  # foreign key back to Document.id

    pan: str | None = None
    taxpayer_name: str | None = None

    policy_account_no: str | None = None
    institution_name: str | None = None
    section: InvestmentSection | None = None

    amount_paid: float | None = None
    date_of_payment: date | None = None
    mode_of_payment: str | None = None

    financial_year: str | None = None
    notes: str | None = None

    # Set by the LLM extraction step, not the OCR step
    extraction_confidence: float | None = None


# ---------------------------------------------------------------------------
# Extraction result — envelope + optional business objects
# ---------------------------------------------------------------------------


class DocumentExtraction(BaseModel):
    """What the LLM parse step returns for one uploaded document.

    At most one business object is populated, matching `document.document_type`;
    all others stay None.
    """

    document: Document
    invoice: Invoice | None = None
    bank_statement: BankStatement | None = None
    gst_return: GSTReturn | None = None
    tds_form: TDSForm | None = None
    investment_proof: InvestmentProof | None = None

    def business_objects(self) -> dict[str, BaseModel]:
        """Map of field name -> populated business object (usually 0 or 1 entries)."""
        return {
            name: obj
            for name in (
                "invoice",
                "bank_statement",
                "gst_return",
                "tds_form",
                "investment_proof",
            )
            if (obj := getattr(self, name)) is not None
        }
