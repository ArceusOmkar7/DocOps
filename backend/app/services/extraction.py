"""LLM-based document extraction: OCR markdown -> Document (+ typed business object).

Two decoupled steps (separate LLM calls, so a mis-classified document can never be
force-molded into a wrong schema):

1. Classification — a cheap, fast call that only picks the document type ("unknown"
   when unclear). Runs before any schema is chosen.
2. Extraction — routes to a type-specific extractor via a capability registry
   (invoice, bank_statement, gst_return, tds_form, investment_proof). Registered-but
   unimplemented types return a clean "unsupported" Document instead of a fake-but-valid
   business object.

Each step validates against Pydantic and may retry by feeding the validation error
back to the model (up to `llm_max_retries` attempts).
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)

import httpx
from pydantic import BaseModel, Field, ValidationError

from ..core.config import Settings
from ..schemas.extraction import (
    BankStatement,
    Document,
    DocumentExtraction,
    DocumentType,
    GSTReturn,
    Invoice,
    InvestmentProof,
    TDSForm,
)

CLASSIFY_PROMPT = """You classify the type of a business document from its OCR output.
Return ONLY a single JSON object:
{"document_type": "invoice|receipt|bank_statement|purchase_order|gst_return|tds_form|investment_proof|unknown",
 "confidence": 0.9, "reason": "one short phrase"}
- "document_type":
  - "bank_statement": bank account statements with transaction tables (date, narration,
    debit, credit, balance).
  - "gst_return": GST portal returns such as GSTR-1, GSTR-3B, GSTR-2B (GSTIN,
    return period, outward supplies / ITC tables).
  - "tds_form": Indian TDS documents — Form 16, Form 16A, Form 26AS, AIS or TIS
    (PAN/TAN, assessment year, TDS deducted/deposited).
  - "investment_proof": Chapter VI-A investment proofs — LIC premium receipts, PPF,
    ELSS, health insurance premiums, home loan interest certificates (80C/80D/24b...).
  - "unknown" when the document does not clearly match any listed type
    (extraction will be skipped for it).
- "confidence": 0-1; how sure you are of the classification.
Keep the response small and fast."""

INVOICE_PROMPT = """You extract invoice data from OCR markdown. Return ONLY a single
valid JSON object matching the invoice schema below. Never invent values; use null when
any field is missing or unreadable. Numbers are plain numbers (e.g. 18.0, not "18%");
dates are ISO 8601 (YYYY-MM-DD). The seller is the issuer; the buyer is the recipient.
Split each table row into one entry under "items".

JSON schema:
{
  "invoice_number": "string or null",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "purchase_order_ref": "string or null",
  "seller": {"name": "...", "address": {"line1": "...", "line2": null, "city": "...",
             "state": "...", "postal_code": "...", "country": "..."},
             "tax_id": "...", "email": "...", "phone": "..."},
  "buyer": {"name": "...", "address": {...}, "tax_id": "...", "email": "...", "phone": "..."},
  "currency": "ISO code or null",
  "items": [{"description": "...", "quantity": 1, "unit_price": 1.0,
             "tax_rate": 18.0, "line_total": 1.0}],
  "subtotal": 1.0,
  "tax": {"cgst": 1.0, "sgst": 1.0, "igst": 1.0, "vat": 1.0,
          "other_tax_label": "...", "other_tax_amount": 1.0},
  "total_tax": 1.0,
  "total": 1.0,
  "amount_paid": 1.0,
  "balance_due": 1.0,
  "payment_terms": "string or null",
  "notes": "string or null"
}"""

BANK_STATEMENT_PROMPT = """You extract bank statement data from OCR markdown.
Return ONLY a single valid JSON object matching the schema below. Never invent
values; use null when any field is missing or unreadable. Numbers are plain
numbers without separators (e.g. 12500.75, never "12,500.75"); debit and credit
are positive amounts in their own column; dates are ISO 8601 (YYYY-MM-DD).
Split each transaction row into one entry under "transactions" in statement order.

JSON schema:
{
  "account_number": "string or null",
  "bank_name": "string or null",
  "ifsc_code": "string or null",
  "account_holder": "string or null",
  "period_start": "YYYY-MM-DD or null",
  "period_end": "YYYY-MM-DD or null",
  "opening_balance": 1.0,
  "closing_balance": 1.0,
  "currency": "ISO code or null (INR for Indian statements)",
  "transactions": [{"date": "YYYY-MM-DD", "description": "...", "cheque_ref_no": "...",
                    "debit": 1.0, "credit": 1.0, "balance": 1.0, "category": "..."}]
}"""

GST_RETURN_PROMPT = """You extract GST return data from OCR markdown of Indian GST
portal returns (GSTR-1, GSTR-3B, GSTR-2B, GSTR-9/9C). Return ONLY a single valid JSON
object matching the schema below. Never invent values; use null when missing.
Numbers are plain numbers without separators; return_period is MM-YYYY;
filing_date is ISO 8601 (YYYY-MM-DD).

JSON schema:
{
  "return_type": "GSTR-1 | GSTR-3B | GSTR-2B | GSTR-9 | GSTR-9C or null",
  "gstin": "15-char GSTIN or null",
  "return_period": "MM-YYYY or null",
  "filing_date": "YYYY-MM-DD or null",
  "arn_number": "string or null",
  "legal_name": "string or null",
  "trade_name": "string or null",
  "taxable_turnover": 1.0,
  "outward_tax_summary": {"igst": 1.0, "cgst": 1.0, "sgst": 1.0, "cess": 1.0},
  "itc_available": {"igst": 1.0, "cgst": 1.0, "sgst": 1.0, "cess": 1.0, "total": 1.0},
  "itc_reversed": {"igst": 1.0, "cgst": 1.0, "sgst": 1.0, "cess": 1.0, "total": 1.0},
  "net_itc": {"igst": 1.0, "cgst": 1.0, "sgst": 1.0, "cess": 1.0, "total": 1.0}
}"""

TDS_FORM_PROMPT = """You extract Indian TDS form data from OCR markdown — Form 16,
Form 16A, Form 26AS, AIS (Annual Information Statement) or TIS (Taxpayer Information
Summary). Return ONLY a single valid JSON object matching the schema below. Never
invent values; use null when missing. Numbers are plain numbers without separators;
years use FY notation like "2025-26" and AY notation like "2026-27".

JSON schema:
{
  "form_type": "Form 16 | Form 16A | Form 26AS | AIS | TIS or null",
  "pan": "10-char PAN of the deductee or null",
  "tan_of_deductor": "TAN or null",
  "deductor_name": "employer/bank/payer name or null",
  "assessment_year": "YYYY-YY or null",
  "financial_year": "YYYY-YY or null",
  "gross_salary": 1.0,
  "total_amount_credited": 1.0,
  "total_tds_deducted": 1.0,
  "total_tds_deposited": 1.0,
  "section_deductions": [{"section_code": "194C", "amount_paid_credited": 1.0,
                          "tds_deducted": 1.0, "tds_deposited": 1.0}]
}"""

INVESTMENT_PROOF_PROMPT = """You extract Chapter VI-A investment proof data from OCR
markdown — LIC premium receipts, PPF passbook entries, ELSS statements, health
insurance premium receipts, home loan interest certificates etc. Return ONLY a single
valid JSON object matching the schema below. Never invent values; use null when
missing. Numbers are plain numbers; date is ISO 8601 (YYYY-MM-DD); section uses the
standard label (80C, 80D, 80CCD, 80CCD(1B), 24b...). If the document contains several
investments, extract only the primary/most prominent one.

JSON schema:
{
  "pan": "10-char PAN or null",
  "taxpayer_name": "string or null",
  "policy_account_no": "string or null",
  "institution_name": "string or null",
  "section": "80C | 80D | 80CCD | ... | 24b or null",
  "amount_paid": 1.0,
  "date_of_payment": "YYYY-MM-DD or null",
  "mode_of_payment": "string or null",
  "financial_year": "YYYY-YY or null",
  "notes": "string or null"
}"""


class ExtractionError(Exception):
    """Raised when LLM-driven classification or extraction fails."""


class JSONResponseError(ExtractionError):
    """Raised when the LLM reply is not a JSON object."""


class _ClassifyPayload(BaseModel):
    """The classification envelope; drives the classication retry-loop validation."""

    document_type: DocumentType = DocumentType.unknown
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    reason: str | None = None


class LLMClient:
    """Minimal OpenAI-compatible chat client built on httpx (no SDK dependency)."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def chat_json(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        s = self._settings
        url = f"{s.llm_base_url.rstrip('/')}/chat/completions"
        headers = {}
        if s.llm_api_key:
            headers["Authorization"] = f"Bearer {s.llm_api_key}"
        payload: dict[str, Any] = {
            "model": model or s.llm_model,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": max_tokens or s.llm_max_tokens,
        }
        if s.llm_use_json_mode:
            payload["response_format"] = {"type": "json_object"}

        max_http_attempts = 6
        data = None
        for attempt in range(max_http_attempts):
            try:
                with httpx.Client(timeout=s.llm_timeout_seconds) as client:
                    response = client.post(url, headers=headers, json=payload)
                    if response.status_code == 429:
                        retry_after = response.headers.get("retry-after")
                        delay = float(retry_after) if retry_after else (2.0 ** attempt * 1.5)
                        try:
                            err_body = response.json()
                            msg = err_body.get("error", {}).get("message", "")
                            m = re.search(r"try again in ([0-9.]+)\s*s", msg)
                            if m:
                                delay = max(delay, float(m.group(1)) + 1.0)
                        except Exception:
                            pass
                        logger.warning(
                            "Rate limited (429) on LLM call. Backing off for %.2fs (attempt %d/%d)...",
                            delay, attempt + 1, max_http_attempts
                        )
                        time.sleep(delay)
                        continue
                    elif response.status_code in (500, 502, 503, 504) and attempt < max_http_attempts - 1:
                        delay = 1.5 * (attempt + 1)
                        logger.warning(
                            "Server error (%d) from LLM. Retrying in %.2fs (attempt %d/%d)...",
                            response.status_code, delay, attempt + 1, max_http_attempts
                        )
                        time.sleep(delay)
                        continue
                    response.raise_for_status()
                    data = response.json()
                    break
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt < max_http_attempts - 1:
                    delay = 2.0 * (attempt + 1)
                    logger.warning("Network/timeout error (%s). Retrying in %.2fs...", exc, delay)
                    time.sleep(delay)
                    continue
                raise ExtractionError(f"LLM request network/timeout failure: {exc}") from exc

        if data is None:
            raise ExtractionError("LLM call failed after retries")

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ExtractionError(f"Unexpected LLM response shape: {data}") from exc
        if not isinstance(content, str) or not content.strip():
            raise JSONResponseError("LLM returned empty content")
        return content


def parse_llm_json(content: str) -> dict[str, Any]:
    """Extract the first JSON object from an LLM reply (tolerates code fences)."""
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise JSONResponseError("LLM returned no JSON object")
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise JSONResponseError(f"LLM returned invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise JSONResponseError("LLM JSON was not an object")
    return data


def _build_user_prompt(markdown: str, last_error: str | None = None) -> str:
    parts = [f"OCR markdown:\n\n{markdown}"]
    if last_error:
        parts.append(
            "Your previous response failed validation. Fix ONLY the reported issues "
            "and return the full JSON object again.\n"
            f"Errors:\n{last_error}"
        )
    return "\n\n".join(parts)


def _format_validation_error(exc: ValidationError) -> str:
    errors = [
        {
            "loc": ".".join(str(part) for part in entry.get("loc", [])),
            "msg": entry.get("msg", ""),
            "type": entry.get("type", ""),
        }
        for entry in exc.errors()
    ]
    return "Validation errors: " + json.dumps(errors)


def _chat_with_retry(
    settings: Settings,
    client: LLMClient,
    system_prompt: str,
    markdown: str,
    validate: Callable[[dict[str, Any]], Any],
    model: str | None = None,
    max_tokens: int | None = None,
) -> Any:
    """Call the LLM, validate the JSON reply, and retry with error feedback."""
    messages = [{"role": "system", "content": system_prompt}]
    last_error: str | None = None
    for _ in range(settings.llm_max_retries):
        try:
            content = client.chat_json(
                messages + [{"role": "user", "content": _build_user_prompt(markdown, last_error)}],
                model=model,
                max_tokens=max_tokens,
            )
            return validate(parse_llm_json(content))
        except httpx.HTTPError as exc:
            raise ExtractionError(f"LLM request failed: {exc}") from exc
        except ValidationError as exc:
            last_error = _format_validation_error(exc)
        except JSONResponseError as exc:
            last_error = str(exc)
    raise ExtractionError(
        f"LLM call failed after {settings.llm_max_retries} attempts. Last error: {last_error}"
    )


def apply_business_review(invoice: Invoice | None) -> list[str]:
    """Business-sanity checks that Pydantic types can't enforce.

    Returns human-review reasons (empty when the numbers add up). Missing values
    are skipped, never flagged.
    """
    if invoice is None:
        return []
    reasons: list[str] = []

    items_total = sum(item.line_total or 0.0 for item in invoice.items)
    if invoice.items and invoice.subtotal is not None:
        if abs(items_total - invoice.subtotal) > 0.01:
            reasons.append(f"line totals ({items_total:.2f}) != subtotal ({invoice.subtotal:.2f})")

    for idx, item in enumerate(invoice.items, start=1):
        if None not in (item.quantity, item.unit_price, item.line_total):
            calculated = item.quantity * item.unit_price
            if abs(calculated - item.line_total) > 0.01:
                reasons.append(
                    f"item {idx} qty*unit ({calculated:.2f}) != line_total ({item.line_total:.2f})"
                )

    if invoice.subtotal is not None and invoice.total is not None:
        tax = invoice.total_tax if invoice.total_tax is not None else 0.0
        if abs(invoice.subtotal + tax - invoice.total) > 0.01:
            reasons.append(
                f"subtotal+tax ({invoice.subtotal + tax:.2f}) != total ({invoice.total:.2f})"
            )

    return reasons


def _review_bank_statement(statement: BankStatement) -> list[str]:
    """Light structural checks (statutory validation arrives in Phase 2).

    Verifies the running balance: balance[i] ≈ balance[i-1] - debit + credit.
    """
    reasons: list[str] = []
    previous_balance = statement.opening_balance
    for idx, txn in enumerate(statement.transactions, start=1):
        if txn.balance is None:
            continue
        if previous_balance is not None:
            debit = txn.debit or 0.0
            credit = txn.credit or 0.0
            expected = previous_balance - debit + credit
            if abs(expected - txn.balance) > 0.05:
                reasons.append(
                    f"transaction {idx} running balance mismatch: "
                    f"expected {expected:.2f}, got {txn.balance:.2f}"
                )
        previous_balance = txn.balance

    if (
        statement.opening_balance is not None
        and statement.closing_balance is not None
        and statement.transactions
        and statement.transactions[-1].balance is not None
    ):
        last = statement.transactions[-1].balance
        if abs(last - statement.closing_balance) > 0.05:
            reasons.append(
                f"last transaction balance ({last:.2f}) != closing balance "
                f"({statement.closing_balance:.2f})"
            )
    return reasons


def _review_gst_return(gst_return: GSTReturn) -> list[str]:
    """Light structural checks (statutory validation arrives in Phase 2)."""
    reasons: list[str] = []

    def total(breakdown) -> float | None:
        if breakdown.total is not None:
            return breakdown.total
        parts = [breakdown.igst, breakdown.cgst, breakdown.sgst, breakdown.cess]
        if any(part is not None for part in parts):
            return sum(part or 0.0 for part in parts)
        return None

    available, reversed_, net = total(gst_return.itc_available), total(gst_return.itc_reversed), total(gst_return.net_itc)
    if None not in (available, reversed_, net):
        expected = available - reversed_
        if abs(expected - net) > 0.05:
            reasons.append(
                f"net ITC ({net:.2f}) != itc_available - itc_reversed ({expected:.2f})"
            )
    return reasons


def apply_structural_review(
    document_type: DocumentType,
    business_object: Invoice | BankStatement | GSTReturn | TDSForm | InvestmentProof | None,
) -> list[str]:
    """Dispatch business-sanity checks for whichever schema was extracted."""
    if isinstance(business_object, Invoice):
        return apply_business_review(business_object)
    if isinstance(business_object, BankStatement):
        return _review_bank_statement(business_object)
    if isinstance(business_object, GSTReturn):
        return _review_gst_return(business_object)
    return []


class ClassificationService:
    """Picks the document type with a cheap, separate LLM call."""

    def __init__(self, settings: Settings, llm_client: LLMClient | None = None):
        self._settings = settings
        self._client = llm_client or LLMClient(settings)

    def classify(self, markdown: str) -> _ClassifyPayload:
        s = self._settings
        return _chat_with_retry(
            s,
            self._client,
            CLASSIFY_PROMPT,
            markdown,
            lambda payload: _ClassifyPayload.model_validate(payload),
            model=s.llm_classify_model or None,
            max_tokens=s.llm_classify_max_tokens or None,
        )


class ExtractionService:
    """Orchestrates classification, then dispatches to the matching extractor."""

    # Document type -> (method that extracts its business object,
    #                   attribute name on DocumentExtraction).
    EXTRACTORS: dict[DocumentType, tuple[str, str]] = {
        DocumentType.invoice: ("_extract_invoice", "invoice"),
        DocumentType.bank_statement: ("_extract_bank_statement", "bank_statement"),
        DocumentType.gst_return: ("_extract_gst_return", "gst_return"),
        DocumentType.tds_form: ("_extract_tds_form", "tds_form"),
        DocumentType.investment_proof: ("_extract_investment_proof", "investment_proof"),
    }

    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient | None = None,
        classifier: ClassificationService | None = None,
    ):
        self._settings = settings
        self._client = llm_client or LLMClient(settings)
        self._classifier = classifier or ClassificationService(settings, llm_client=self._client)

    def extract(
        self,
        markdown: str,
        *,
        document_id: str,
        source_filename: str,
        ocr_confidence: float | None = None,
    ) -> DocumentExtraction:
        classified = self._classifier.classify(markdown)

        document_type = classified.document_type
        if (
            classified.confidence is not None
            and classified.confidence < self._settings.llm_classify_min_confidence
        ):
            document_type = DocumentType.unknown

        business_object = None
        if document_type == DocumentType.unknown:
            status, review_reason = "needs_review", "Could not determine document type"
        elif document_type not in self.EXTRACTORS:
            status, review_reason = "unsupported", (
                f"Document type '{document_type.value}' is not supported for extraction yet"
            )
        else:
            extractor_name, field_name = self.EXTRACTORS[document_type]
            business_object = getattr(self, extractor_name)(markdown, document_id)
            reasons = apply_structural_review(document_type, business_object)
            status = "needs_review" if reasons else "success"
            review_reason = "; ".join(reasons) if reasons else None

        extraction = DocumentExtraction(
            document=Document(
                id=document_id,
                source_filename=source_filename,
                document_type=document_type,
                ocr_confidence=ocr_confidence,
                raw_markdown=markdown,
                extraction_status=status,
                needs_human_review=bool(review_reason),
                review_reason=review_reason,
            ),
        )
        if business_object is not None:
            setattr(extraction, field_name, business_object)
        return extraction

    def _extract_invoice(self, markdown: str, document_id: str) -> Invoice:
        return _chat_with_retry(
            self._settings,
            self._client,
            INVOICE_PROMPT,
            markdown,
            lambda payload: Invoice.model_validate({"document_id": document_id, **payload}),
        )

    def _extract_bank_statement(self, markdown: str, document_id: str) -> BankStatement:
        return _chat_with_retry(
            self._settings,
            self._client,
            BANK_STATEMENT_PROMPT,
            markdown,
            lambda payload: BankStatement.model_validate({"document_id": document_id, **payload}),
        )

    def _extract_gst_return(self, markdown: str, document_id: str) -> GSTReturn:
        return _chat_with_retry(
            self._settings,
            self._client,
            GST_RETURN_PROMPT,
            markdown,
            lambda payload: GSTReturn.model_validate({"document_id": document_id, **payload}),
        )

    def _extract_tds_form(self, markdown: str, document_id: str) -> TDSForm:
        return _chat_with_retry(
            self._settings,
            self._client,
            TDS_FORM_PROMPT,
            markdown,
            lambda payload: TDSForm.model_validate({"document_id": document_id, **payload}),
        )

    def _extract_investment_proof(self, markdown: str, document_id: str) -> InvestmentProof:
        return _chat_with_retry(
            self._settings,
            self._client,
            INVESTMENT_PROOF_PROMPT,
            markdown,
            lambda payload: InvestmentProof.model_validate({"document_id": document_id, **payload}),
        )