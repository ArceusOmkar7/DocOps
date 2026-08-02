"""Integration tests for DB-backed Organization, Client, Workflow, and Document API endpoints."""

from __future__ import annotations

import shutil
import uuid

from fastapi.testclient import TestClient

from app.api.deps import get_extraction_service
from app.core.config import get_settings
from app.core.storage import result_dir, save_json
from app.main import app
from app.schemas.extraction import Document as SchemaDocument, DocumentExtraction, DocumentType, Invoice


class FakeExtractionService:
    def extract(self, markdown, *, document_id, source_filename, ocr_confidence=None):
        invoice = Invoice(document_id=document_id, invoice_number="INV-2026")
        document = SchemaDocument(
            id=document_id,
            source_filename=source_filename,
            document_type=DocumentType.invoice,
            ocr_confidence=ocr_confidence,
            raw_markdown=markdown,
            extraction_status="success",
        )
        return DocumentExtraction(document=document, invoice=invoice)


def _sample_ocr_result(rid: str) -> dict:
    return {
        "result_id": rid,
        "filename": "sample_invoice.pdf",
        "file_type": "pdf",
        "page_count": 1,
        "pages": [
            {
                "page_index": 0,
                "width": 600,
                "height": 800,
                "blocks": [
                    {
                        "text": "Invoice # INV-2026",
                        "confidence": 0.95,
                        "polygon": [[0, 0], [1, 0], [1, 1], [0, 1]],
                        "bbox": [0, 0, 1, 1],
                        "label": "text",
                    }
                ],
                "layout_blocks": [],
                "text": "Invoice # INV-2026",
                "markdown": "## Invoice # INV-2026",
            }
        ],
        "full_text": "Invoice # INV-2026",
        "markdown": "## Invoice # INV-2026",
        "engine": {
            "pipeline": "PP-StructureV3",
            "device": "gpu",
        },
        "processing_time_ms": 120,
        "created_at": "2026-08-02T12:00:00Z",
    }


def test_organization_crud():
    slug = f"test-org-{uuid.uuid4().hex[:6]}"
    with TestClient(app) as client:
        # Create
        create_res = client.post(
            "/api/v1/organizations",
            json={"name": "Test Org", "slug": slug, "plan": "pro"},
        )
        assert create_res.status_code == 201
        org_data = create_res.json()
        assert org_data["name"] == "Test Org"
        assert org_data["slug"] == slug
        org_id = org_data["id"]

        # Get by ID
        get_res = client.get(f"/api/v1/organizations/{org_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == org_id

        # List
        list_res = client.get("/api/v1/organizations")
        assert list_res.status_code == 200
        assert any(o["id"] == org_id for o in list_res.json())


def test_client_crud():
    slug = f"test-org-{uuid.uuid4().hex[:6]}"
    with TestClient(app) as client:
        # Create org first
        org_res = client.post(
            "/api/v1/organizations",
            json={"name": "Client Test Org", "slug": slug, "plan": "free"},
        )
        org_id = org_res.json()["id"]

        # Create Client
        c_res = client.post(
            "/api/v1/clients",
            json={
                "organization_id": org_id,
                "name": "ABC Corp",
                "tax_id": "GSTIN12345",
                "email": "abc@example.com",
            },
        )
        assert c_res.status_code == 201
        client_data = c_res.json()
        assert client_data["name"] == "ABC Corp"
        client_id = client_data["id"]

        # Update Client
        patch_res = client.patch(
            f"/api/v1/clients/{client_id}",
            json={"contact_person": "Jane Doe", "status": "action_required"},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["contact_person"] == "Jane Doe"
        assert patch_res.json()["status"] == "action_required"

        # List Clients
        list_res = client.get(f"/api/v1/clients?organization_id={org_id}")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1
        assert list_res.json()[0]["id"] == client_id


def test_workflow_crud_and_requirement():
    slug = f"test-org-{uuid.uuid4().hex[:6]}"
    with TestClient(app) as client:
        # Create org & client
        org_id = client.post("/api/v1/organizations", json={"name": "Wf Org", "slug": slug}).json()["id"]
        client_id = client.post(
            "/api/v1/clients",
            json={"organization_id": org_id, "name": "Wf Client"},
        ).json()["id"]

        # Create Workflow with requirements
        wf_res = client.post(
            "/api/v1/workflows",
            json={
                "organization_id": org_id,
                "client_id": client_id,
                "name": "August 2026 GST Filing",
                "workflow_type": "gst_filing",
                "period_start": "2026-08-01",
                "period_end": "2026-08-31",
                "requirements": [
                    {
                        "document_type": "invoice",
                        "label": "Purchase Invoices",
                        "required_count": 5,
                    }
                ],
            },
        )
        assert wf_res.status_code == 201
        wf_data = wf_res.json()
        assert wf_data["name"] == "August 2026 GST Filing"
        assert wf_data["status"] == "collecting_documents"
        assert len(wf_data["requirements"]) == 1
        assert wf_data["requirements"][0]["label"] == "Purchase Invoices"


def test_parse_endpoint_persists_to_db():
    settings = get_settings()
    rid = f"db_parse_test_{uuid.uuid4().hex[:6]}"
    out_dir = result_dir(settings, rid)
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(out_dir / "result.json", _sample_ocr_result(rid))

    app.dependency_overrides[get_extraction_service] = lambda: FakeExtractionService()
    try:
        with TestClient(app) as client:
            res = client.post(f"/api/v1/ocr/results/{rid}/parse")
            assert res.status_code == 200

            # Verify document exists in PostgreSQL DB via /api/v1/documents
            doc_res = client.get("/api/v1/documents")
            assert doc_res.status_code == 200
            docs = doc_res.json()
            matching = [d for d in docs if d["ocr_result_id"] == rid]
            assert len(matching) == 1
            db_doc = matching[0]
            assert db_doc["document_type"] == "invoice"
            assert db_doc["status"] == "extracted"
            assert db_doc["extracted_data"]["invoice_number"] == "INV-2026"
    finally:
        app.dependency_overrides.clear()
        shutil.rmtree(out_dir, ignore_errors=True)
