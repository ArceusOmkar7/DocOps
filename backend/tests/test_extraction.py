"""Unit tests for the LLM classification + extraction pipeline (no real LLM calls)."""

import json

import pytest

from app.core.config import Settings, get_settings
from app.schemas.extraction import DocumentType, Invoice
from app.services.extraction import (
    ExtractionError,
    ExtractionService,
    JSONResponseError,
    apply_business_review,
    parse_llm_json,
)


class FakeLLMClient:
    """Scripted chat client: pops one canned response (or exception) per call."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.messages: list[list[dict[str, str]]] = []

    def chat_json(self, messages: list[dict[str, str]], **kwargs) -> str:
        self.messages.append(messages)
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


def _classify_payload(**overrides) -> dict:
    payload = {
        "document_type": "invoice",
        "confidence": 0.98,
        "reason": "invoice",
    }
    payload.update(overrides)
    return payload


def _invoice_payload(**overrides) -> dict:
    payload = {
        "invoice_number": "INV-001",
        "invoice_date": "2026-08-01",
        "currency": "USD",
        "seller": {"name": "ACME Corp", "tax_id": "GST123"},
        "buyer": {"name": "Client Co"},
        "items": [
            {"description": "Widget", "quantity": 2, "unit_price": 10.0, "line_total": 20.0}
        ],
        "subtotal": 20.0,
        "total_tax": 1.8,
        "total": 21.8,
    }
    payload.update(overrides)
    return payload


def test_extract_runs_classify_then_invoice():
    client = FakeLLMClient([json.dumps(_classify_payload()), json.dumps(_invoice_payload())])
    service = ExtractionService(get_settings(), client)

    result = service.extract(
        "## Invoice\n\nINV-001",
        document_id="doc1",
        source_filename="inv.png",
        ocr_confidence=0.95,
    )

    assert result.document.id == "doc1"
    assert result.document.document_type == DocumentType.invoice
    assert result.document.extraction_status == "success"
    assert result.document.ocr_confidence == 0.95
    assert result.invoice.document_id == "doc1"
    assert result.invoice.invoice_number == "INV-001"
    assert result.invoice.seller.name == "ACME Corp"
    assert len(client.messages) == 2
    assert "classify" in client.messages[0][0]["content"]
    assert "invoice" in client.messages[1][0]["content"]


def test_classify_unknown_returns_needs_review_no_invoice():
    client = FakeLLMClient([json.dumps(_classify_payload(document_type="unknown"))])
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="doc1", source_filename="r.png")

    assert result.document.document_type == DocumentType.unknown
    assert result.document.extraction_status == "needs_review"
    assert result.document.needs_human_review is True
    assert result.invoice is None
    assert len(client.messages) == 1  # no extraction call


def test_classify_unsupported_type_returns_clean_signal():
    client = FakeLLMClient([json.dumps(_classify_payload(document_type="receipt"))])
    service = ExtractionService(get_settings(), client)

    result = service.extract("m.png", document_id="r1", source_filename="r.png")

    assert result.document.document_type == DocumentType.receipt
    assert result.document.extraction_status == "unsupported"
    assert result.document.needs_human_review is True
    assert result.invoice is None
    assert len(client.messages) == 1


def test_low_confidence_classification_treated_as_unknown():
    settings = Settings(llm_classify_min_confidence=0.5)
    client = FakeLLMClient([json.dumps(_classify_payload(document_type="invoice", confidence=0.3))])
    service = ExtractionService(settings, client)

    result = service.extract("m.png", document_id="r2", source_filename="r.png")

    assert result.document.document_type == DocumentType.unknown
    assert result.invoice is None
    assert len(client.messages) == 1


def test_extract_marks_mismatched_totals_for_review():
    bad = _invoice_payload(subtotal=99.0)
    client = FakeLLMClient([json.dumps(_classify_payload()), json.dumps(bad)])
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="d", source_filename="inv.png")

    assert result.document.needs_human_review is True
    assert result.document.extraction_status == "needs_review"
    assert "subtotal" in result.document.review_reason


def test_classify_retries_on_validation_error_and_feeds_back():
    bad = json.dumps(_classify_payload(document_type="not-a-real-type"))
    client = FakeLLMClient([bad, json.dumps(_classify_payload()), json.dumps(_invoice_payload())])
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="r", source_filename="inv.png")

    assert result.invoice.invoice_number == "INV-001"
    assert len(client.messages) == 3
    assert "Validation errors" in client.messages[1][1]["content"]


def test_extract_retries_on_invalid_json():
    client = FakeLLMClient(
        [json.dumps(_classify_payload()), "```json\n{not valid\n```", json.dumps(_invoice_payload())]
    )
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="r1", source_filename="inv.png")

    assert result.invoice is not None
    assert len(client.messages) == 3


def test_extract_raises_after_max_retries_on_classify():
    bad = json.dumps(_classify_payload(document_type="not-a-real-type"))
    client = FakeLLMClient([bad, bad, bad])
    service = ExtractionService(get_settings(), client)

    with pytest.raises(ExtractionError, match="3 attempts"):
        service.extract("md", document_id="r1", source_filename="inv.png")


def test_extract_raises_after_max_retries_on_invoice():
    bad_invoice = json.dumps(
        _invoice_payload(items=[{"quantity": "not-a-number"}])
    )
    client = FakeLLMClient(
        [json.dumps(_classify_payload()), bad_invoice, bad_invoice, bad_invoice]
    )
    service = ExtractionService(get_settings(), client)

    with pytest.raises(ExtractionError, match="3 attempts"):
        service.extract("md", document_id="r1", source_filename="inv.png")


def test_parse_llm_json_handles_code_fences():
    assert parse_llm_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_llm_json_rejects_non_object():
    with pytest.raises(JSONResponseError):
        parse_llm_json("[1, 2, 3]")


def test_apply_business_review_reports_breakdowns():
    invoice = Invoice(
        document_id="d",
        items=[
            {"description": "a", "quantity": 2, "unit_price": 10.0, "line_total": 21.0}
        ],
        subtotal=20.0,
        total_tax=1.8,
        total=21.8,
    )
    reasons = apply_business_review(invoice)
    assert any("qty*unit" in reason for reason in reasons)
    assert any("subtotal" in reason for reason in reasons)


def test_apply_business_review_clean_invoice_has_no_reasons():
    invoice = Invoice(
        document_id="d",
        items=[
            {"description": "a", "quantity": 2, "unit_price": 10.0, "line_total": 20.0}
        ],
        subtotal=20.0,
        total_tax=1.8,
        total=21.8,
    )
    assert apply_business_review(invoice) == []
    assert apply_business_review(None) == []