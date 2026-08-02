"""Tests for the parse endpoint (LLM extraction is mocked)."""

import shutil

from fastapi.testclient import TestClient

from app.api.deps import get_extraction_service
from app.core.config import get_settings
from app.core.storage import result_dir, save_json
from app.main import app
from app.schemas.extraction import Document, DocumentExtraction, DocumentType, Invoice


class FakeExtractionService:
    def extract(self, markdown, *, document_id, source_filename, ocr_confidence=None):
        invoice = Invoice(document_id=document_id, invoice_number="INV-9")
        document = Document(
            id=document_id,
            source_filename=source_filename,
            document_type=DocumentType.invoice,
            ocr_confidence=ocr_confidence,
            raw_markdown=markdown,
            extraction_status="success",
        )
        return DocumentExtraction(document=document, invoice=invoice)


def _stored_result(rid: str) -> dict:
    return {
        "result_id": rid,
        "filename": "invoice.png",
        "file_type": "image",
        "page_count": 1,
        "pages": [
            {
                "page_index": 0,
                "width": 100,
                "height": 100,
                "blocks": [
                    {
                        "text": "hi",
                        "confidence": 0.9,
                        "polygon": [[0, 0], [1, 0], [1, 1], [0, 1]],
                        "bbox": [0, 0, 1, 1],
                        "label": "text",
                    }
                ],
                "layout_blocks": [],
                "text": "hi",
                "markdown": "## Invoice",
            }
        ],
        "full_text": "hi",
        "markdown": "## Invoice",
        "source_url": None,
        "markdown_url": None,
        "engine": {
            "pipeline": "PP-StructureV3",
            "lang": "en",
            "layout_model": None,
            "detection_model": None,
            "recognition_model": None,
            "device": "gpu",
        },
        "processing_time_ms": 1,
        "created_at": "2026-08-01T00:00:00Z",
    }


def test_parse_missing_result_returns_404():
    with TestClient(app) as client:
        res = client.post("/api/v1/ocr/results/doesnotexist/parse")
    assert res.status_code == 404


def test_parse_stored_result_returns_document_and_invoice():
    settings = get_settings()
    rid = "parse_test_abc"
    out_dir = result_dir(settings, rid)
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(out_dir / "result.json", _stored_result(rid))

    app.dependency_overrides[get_extraction_service] = lambda: FakeExtractionService()
    try:
        with TestClient(app) as client:
            res = client.post(f"/api/v1/ocr/results/{rid}/parse")
    finally:
        app.dependency_overrides.clear()
        shutil.rmtree(out_dir, ignore_errors=True)

    assert res.status_code == 200
    data = res.json()
    assert data["document"]["id"] == rid
    assert data["document"]["document_type"] == "invoice"
    assert data["document"]["ocr_confidence"] == 0.9
    assert data["invoice"]["invoice_number"] == "INV-9"
