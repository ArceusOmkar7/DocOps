"""LLM-based extraction: OCR markdown -> business objects (Document + Invoice).

The service asks an OpenAI-compatible chat endpoint for strict JSON, validates it
against the extraction schemas, and on failure feeds the validation error back to
the model and retries (up to `llm_max_retries` attempts). Business-level checks
(totals balancing, qty*unit == line_total) are separate from Pydantic's structural
validation and only flag the document for human review.
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from ..core.config import Settings
from ..schemas.extraction import (
    Document,
    DocumentExtraction,
    DocumentType,
    Invoice,
)

SYSTEM_PROMPT = """You extract structured business data from OCR markdown of a document.

Rules:
- Return ONLY a single valid JSON object. No prose, no code fences.
- Use null for any value you cannot determine. Never invent data.
- Numbers are plain numbers (e.g. 18.0, not "18%"). Dates are ISO 8601 (YYYY-MM-DD).
- Identify the seller (issuer) and buyer (recipient) companies from header/footer blocks.
- Split table rows into one entry per line in "items".

JSON schema:
{
  "document_type": "invoice|receipt|bank_statement|purchase_order|gst_return|unknown",
  "invoice": {
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
  }
}

If the document is not an invoice, set document_type accordingly and make "invoice"
null (do not try to fill invoice fields). Unknown values inside invoice fields are null."""


class ExtractionError(Exception):
    """Raised when business extraction fails."""


class JSONResponseError(ExtractionError):
    """Raised when the LLM reply is not a JSON object."""


class _LLMPayload(BaseModel):
    """The JSON envelope the model returns; drives the retry loop's validation."""

    document_type: DocumentType = DocumentType.unknown
    invoice: dict[str, Any] | None = None


class LLMClient:
    """Minimal OpenAI-compatible chat client built on httpx (no SDK dependency)."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def chat_json(self, messages: list[dict[str, str]]) -> str:
        s = self._settings
        url = f"{s.llm_base_url.rstrip('/')}/chat/completions"
        headers = {}
        if s.llm_api_key:
            headers["Authorization"] = f"Bearer {s.llm_api_key}"
        payload: dict[str, Any] = {
            "model": s.llm_model,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": s.llm_max_tokens,
        }
        if s.llm_use_json_mode:
            payload["response_format"] = {"type": "json_object"}
        with httpx.Client(timeout=s.llm_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
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


class ExtractionService:
    """Converts OCR markdown into a Document (+ Invoice) with LLM retry."""

    def __init__(self, settings: Settings, llm_client: LLMClient | None = None):
        self._settings = settings
        self._client = llm_client or LLMClient(settings)

    def extract(
        self,
        markdown: str,
        *,
        document_id: str,
        source_filename: str,
        ocr_confidence: float | None = None,
    ) -> DocumentExtraction:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        last_error: str | None = None
        for _ in range(self._settings.llm_max_retries):
            user_prompt = _build_user_prompt(markdown, last_error)
            try:
                content = self._client.chat_json(
                    messages + [{"role": "user", "content": user_prompt}]
                )
                payload = parse_llm_json(content)
                return self._build_result(
                    payload,
                    markdown=markdown,
                    document_id=document_id,
                    source_filename=source_filename,
                    ocr_confidence=ocr_confidence,
                )
            except httpx.HTTPError as exc:
                raise ExtractionError(f"LLM request failed: {exc}") from exc
            except ValidationError as exc:
                last_error = _format_validation_error(exc)
            except JSONResponseError as exc:
                last_error = str(exc)
        raise ExtractionError(
            f"LLM extraction failed after {self._settings.llm_max_retries} attempts. "
            f"Last error: {last_error}"
        )

    def _build_result(
        self,
        payload: dict[str, Any],
        *,
        markdown: str,
        document_id: str,
        source_filename: str,
        ocr_confidence: float | None,
    ) -> DocumentExtraction:
        llm = _LLMPayload.model_validate(payload)
        invoice: Invoice | None = None
        if llm.document_type == DocumentType.invoice:
            invoice = Invoice.model_validate(
                {"document_id": document_id, **(llm.invoice or {})}
            )

        document = Document(
            id=document_id,
            source_filename=source_filename,
            document_type=llm.document_type,
            ocr_confidence=ocr_confidence,
            raw_markdown=markdown,
            extraction_status="success",
        )
        reasons = apply_business_review(invoice)
        if reasons:
            document.extraction_status = "needs_review"
            document.needs_human_review = True
            document.review_reason = "; ".join(reasons)

        return DocumentExtraction(document=document, invoice=invoice)
