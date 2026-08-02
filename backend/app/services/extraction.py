"""LLM-based document extraction: OCR markdown -> Document (+ typed business object).

Two decoupled steps (separate LLM calls, so a mis-classified document can never be
force-molded into a wrong schema):

1. Classification — a cheap, fast call that only picks the document type ("unknown"
   when unclear). Runs before any schema is chosen.
2. Extraction — routes to a type-specific extractor via a capability registry. Today
   only "invoice" has an extractor; other supported types return a clean
   "unsupported" Document instead of a fake-but-valid Invoice (all invoice fields are
   optional, so forcing a wrong type through would "validate" garbage).

Each step validates against Pydantic and may retry by feeding the validation error
back to the model (up to `llm_max_retries` attempts).
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

import httpx
from pydantic import BaseModel, Field, ValidationError

from ..core.config import Settings
from ..schemas.extraction import (
    Document,
    DocumentExtraction,
    DocumentType,
    Invoice,
)

CLASSIFY_PROMPT = """You classify the type of a business document from its OCR output.
Return ONLY a single JSON object:
{"document_type": "invoice|receipt|bank_statement|purchase_order|gst_return|unknown",
 "confidence": 0.9, "reason": "one short phrase"}
- "document_type": "unknown" when the document does not clearly match any listed type
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

    # Document type -> method that extracts its business object.
    EXTRACTORS: dict[DocumentType, str] = {
        DocumentType.invoice: "_extract_invoice",
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

        invoice: Invoice | None = None
        if document_type == DocumentType.unknown:
            status, review_reason = "needs_review", "Could not determine document type"
        elif document_type not in self.EXTRACTORS:
            status, review_reason = "unsupported", (
                f"Document type '{document_type.value}' is not supported for extraction yet"
            )
        else:
            invoice = getattr(self, self.EXTRACTORS[document_type])(markdown, document_id)
            reasons = apply_business_review(invoice)
            status = "needs_review" if reasons else "success"
            review_reason = "; ".join(reasons) if reasons else None

        return DocumentExtraction(
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
            invoice=invoice,
        )

    def _extract_invoice(self, markdown: str, document_id: str) -> Invoice:
        return _chat_with_retry(
            self._settings,
            self._client,
            INVOICE_PROMPT,
            markdown,
            lambda payload: Invoice.model_validate({"document_id": document_id, **payload}),
        )