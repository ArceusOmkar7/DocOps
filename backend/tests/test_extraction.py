"""Unit tests for the LLM classification + extraction pipeline (no real LLM calls)."""

import json

import pytest

from app.core.config import Settings, get_settings
from app.schemas.extraction import (
    BankStatement,
    DocumentType,
    GSTReturn,
    Invoice,
    InvestmentProof,
    TDSForm,
)
from app.services.extraction import (
    ExtractionError,
    ExtractionService,
    JSONResponseError,
    apply_business_review,
    apply_structural_review,
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


# ---------------------------------------------------------------------------
# Phase 1 — multi-document family extractors
# ---------------------------------------------------------------------------


def _bank_statement_payload(**overrides) -> dict:
    payload = {
        "account_number": "1234567890",
        "bank_name": "HDFC Bank",
        "ifsc_code": "HDFC0001234",
        "account_holder": "Ramesh Kumar",
        "period_start": "2026-04-01",
        "period_end": "2026-06-30",
        "opening_balance": 10000.0,
        "closing_balance": 59500.0,
        "currency": "INR",
        "transactions": [
            {"date": "2026-04-05", "description": "UPI/SWIGGY", "debit": 500.0, "balance": 9500.0},
            {"date": "2026-04-10", "description": "SALARY APR", "credit": 50000.0, "balance": 59500.0},
        ],
    }
    payload.update(overrides)
    return payload


def _gst_return_payload(**overrides) -> dict:
    payload = {
        "return_type": "GSTR-3B",
        "gstin": "27ABCDE1234F1Z5",
        "return_period": "08-2026",
        "filing_date": "2026-09-20",
        "arn_number": "AA270826123456B",
        "legal_name": "ABC Traders Pvt Ltd",
        "taxable_turnover": 500000.0,
        "outward_tax_summary": {"igst": 0.0, "cgst": 45000.0, "sgst": 45000.0},
        "itc_available": {"igst": 1000.0, "cgst": 2000.0, "sgst": 2000.0, "total": 5000.0},
        "itc_reversed": {"total": 1000.0},
        "net_itc": {"total": 4000.0},
    }
    payload.update(overrides)
    return payload


def _tds_form_payload(**overrides) -> dict:
    payload = {
        "form_type": "Form 16",
        "pan": "ABCPK1234F",
        "tan_of_deductor": "MUMA12345B",
        "deductor_name": "Infosys Limited",
        "assessment_year": "2026-27",
        "financial_year": "2025-26",
        "gross_salary": 1200000.0,
        "total_tds_deducted": 150000.0,
        "total_tds_deposited": 150000.0,
        "section_deductions": [{"section_code": "192", "amount_paid_credited": 1200000.0, "tds_deducted": 150000.0}],
    }
    payload.update(overrides)
    return payload


def _investment_proof_payload(**overrides) -> dict:
    payload = {
        "pan": "ABCPK1234F",
        "taxpayer_name": "Sunita Kumar",
        "policy_account_no": "123456789",
        "institution_name": "LIC of India",
        "section": "80C",
        "amount_paid": 25000.0,
        "date_of_payment": "2026-03-15",
        "financial_year": "2025-26",
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    ("document_type", "payload_builder", "field"),
    [
        (DocumentType.bank_statement, _bank_statement_payload, "bank_statement"),
        (DocumentType.gst_return, _gst_return_payload, "gst_return"),
        (DocumentType.tds_form, _tds_form_payload, "tds_form"),
        (DocumentType.investment_proof, _investment_proof_payload, "investment_proof"),
    ],
)
def test_new_document_family_extracts_into_typed_object(document_type, payload_builder, field):
    client = FakeLLMClient([json.dumps(_classify_payload(document_type=document_type.value)), json.dumps(payload_builder())])
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="doc1", source_filename="f.pdf")

    assert result.document.document_type == document_type
    assert result.document.extraction_status == "success"
    obj = getattr(result, field)
    assert obj is not None
    assert obj.document_id == "doc1"
    # Siblings stay None; exactly one business object populated.
    assert len(result.business_objects()) == 1


def test_bank_statement_running_balance_mismatch_flags_review():
    bad = _bank_statement_payload()
    bad["transactions"][1]["balance"] = 60000.0  # should be 59500
    client = FakeLLMClient(
        [json.dumps(_classify_payload(document_type="bank_statement")), json.dumps(bad)]
    )
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="d", source_filename="stmt.pdf")

    assert result.document.extraction_status == "needs_review"
    assert "running balance" in result.document.review_reason


def test_bank_statement_closing_balance_mismatch_flags_review():
    bad = _bank_statement_payload(closing_balance=99999.0)
    client = FakeLLMClient(
        [json.dumps(_classify_payload(document_type="bank_statement")), json.dumps(bad)]
    )
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="d", source_filename="stmt.pdf")

    assert result.document.extraction_status == "needs_review"
    assert "closing balance" in result.document.review_reason


def test_gst_return_net_itc_mismatch_flags_review():
    bad = _gst_return_payload(net_itc={"total": 99999.0})
    client = FakeLLMClient(
        [json.dumps(_classify_payload(document_type="gst_return")), json.dumps(bad)]
    )
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="d", source_filename="3b.pdf")

    assert result.document.extraction_status == "needs_review"
    assert "net ITC" in result.document.review_reason


def test_new_family_retries_on_validation_error_then_succeeds():
    invalid = json.dumps({"form_type": "Not A Form"})
    client = FakeLLMClient(
        [json.dumps(_classify_payload(document_type="tds_form")), invalid, json.dumps(_tds_form_payload())]
    )
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="d", source_filename="f16.pdf")

    assert result.tds_form.pan == "ABCPK1234F"
    assert len(client.messages) == 3
    assert "Validation errors" in client.messages[2][1]["content"]


def test_receipt_still_unsupported_after_registry_expansion():
    client = FakeLLMClient([json.dumps(_classify_payload(document_type="receipt"))])
    service = ExtractionService(get_settings(), client)

    result = service.extract("md", document_id="r", source_filename="r.png")

    assert result.document.extraction_status == "unsupported"
    assert len(result.business_objects()) == 0


# ---------------------------------------------------------------------------
# Structural review dispatch
# ---------------------------------------------------------------------------


def test_structural_review_dispatch_and_noop():
    statement = BankStatement.model_validate(
        {"document_id": "d", **_bank_statement_payload()}
    )
    gst = GSTReturn.model_validate({"document_id": "d", **_gst_return_payload()})
    tds = TDSForm.model_validate({"document_id": "d", **_tds_form_payload()})
    inv_proof = InvestmentProof.model_validate(
        {"document_id": "d", **_investment_proof_payload()}
    )

    assert apply_structural_review(DocumentType.bank_statement, statement) == []
    assert apply_structural_review(DocumentType.gst_return, gst) == []
    assert apply_structural_review(DocumentType.tds_form, tds) == []
    assert apply_structural_review(DocumentType.investment_proof, inv_proof) == []

    broken = BankStatement.model_validate(
        {"document_id": "d", **_bank_statement_payload(closing_balance=42.0)}
    )
    reasons = apply_structural_review(DocumentType.bank_statement, broken)
    assert any("closing balance" in reason for reason in reasons)


# ---------------------------------------------------------------------------
# Schema validation edge cases
# ---------------------------------------------------------------------------


def test_gst_return_rejects_unknown_return_type():
    with pytest.raises(Exception):
        GSTReturn.model_validate({"document_id": "d", "return_type": "GSTR-XYZ"})


def test_investment_proof_rejects_bogus_section():
    with pytest.raises(Exception):
        InvestmentProof.model_validate({"document_id": "d", "section": "90Z"})


def test_tds_form_accepts_known_form_kinds_only():
    with pytest.raises(Exception):
        TDSForm.model_validate({"document_id": "d", "form_type": "Form 12BB"})