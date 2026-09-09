"""
Seed script: replace dummy DB data with the Kapoor & Shah fictional universe.

Run from backend/:
    .venv/Scripts/python.exe tests/fixtures/seed_db.py
    .venv/Scripts/python.exe tests/fixtures/seed_db.py --wipe-only  # just clears
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Absolute path helpers
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent
PDFS_DIR = FIXTURES_DIR / "pdfs"
MANIFEST_PATH = PDFS_DIR / "manifest.json"

DATABASE_URL = "postgresql+asyncpg://project_agent:agentspassword@localhost/ai_docs_orch"

# ---------------------------------------------------------------------------
# Ground-truth extracted_data shaped to match the extraction schemas
# (loaded from manifest.json, then massaged into the extractor schema format)
# ---------------------------------------------------------------------------

def _gt(manifest: dict, filename: str) -> dict:
    """Return the ground_truth dict for a specific filename."""
    for doc in manifest["documents"]:
        if doc["filename"] == filename or doc["filename"].endswith(filename):
            return doc.get("ground_truth", {})
    return {}


def build_extracted_data(manifest: dict) -> dict[str, dict]:
    """Return filename -> extracted_data (JSONB-ready dict) mapping."""
    results: dict[str, dict] = {}

    # ---- invoices ----
    for fname in [
        "clean/invoice_rajput_rs0234.pdf",
        "clean/invoice_rajput_rs0235.pdf",
        "clean/invoice_codeify_ct0189.pdf",
    ]:
        gt = _gt(manifest, fname)
        results[fname] = {
            "invoice_number": gt.get("invoice_number"),
            "invoice_date": gt.get("date"),
            "seller": {
                "name": gt.get("seller_name"),
                "tax_id": gt.get("seller_gstin"),
            },
            "buyer": {
                "name": gt.get("buyer_name"),
                "tax_id": gt.get("buyer_gstin"),
            },
            "currency": "INR",
            "subtotal": gt.get("subtotal"),
            "tax": {
                "cgst": gt.get("cgst"),
                "sgst": gt.get("sgst"),
                "igst": gt.get("igst"),
            },
            "total_tax": (gt.get("cgst") or 0) + (gt.get("sgst") or 0) + (gt.get("igst") or 0),
            "total": gt.get("total"),
        }

    # ---- bank statements ----
    for fname in [
        "clean/bank_stmt_rajput_aug2026.pdf",
        "clean/bank_stmt_codeify_aug2026.pdf",
    ]:
        gt = _gt(manifest, fname)
        results[fname] = {
            "bank_name": gt.get("bank_name"),
            "account_number": gt.get("account_number"),
            "account_holder": gt.get("account_holder"),
            "period_start": gt.get("statement_period", {}).get("start") if isinstance(gt.get("statement_period"), dict) else None,
            "period_end": gt.get("statement_period", {}).get("end") if isinstance(gt.get("statement_period"), dict) else None,
            "opening_balance": gt.get("opening_balance"),
            "closing_balance": gt.get("closing_balance"),
            "currency": "INR",
        }

    # ---- GST returns ----
    for fname in [
        "clean/gstr3b_rajput_aug2026.pdf",
        "clean/gstr3b_codeify_aug2026.pdf",
    ]:
        gt = _gt(manifest, fname)
        results[fname] = {
            "return_type": gt.get("form_type", "GSTR-3B"),
            "gstin": gt.get("gstin"),
            "return_period": gt.get("return_period"),
            "legal_name": gt.get("legal_name"),
            "taxable_turnover": gt.get("taxable_turnover"),
            "outward_tax_summary": {
                "igst": gt.get("outward_igst"),
                "cgst": gt.get("outward_cgst"),
                "sgst": gt.get("outward_sgst"),
                "cess": None,
            },
            "itc_available": {
                "igst": gt.get("itc_available_igst"),
                "cgst": gt.get("itc_available_cgst"),
                "sgst": gt.get("itc_available_sgst"),
                "cess": None,
                "total": gt.get("itc_available_total"),
            },
            "itc_reversed": {
                "igst": gt.get("itc_reversed_igst"),
                "cgst": gt.get("itc_reversed_cgst"),
                "sgst": gt.get("itc_reversed_sgst"),
                "cess": None,
                "total": gt.get("itc_reversed_total"),
            },
            "net_itc": {
                "igst": gt.get("net_itc_igst"),
                "cgst": gt.get("net_itc_cgst"),
                "sgst": gt.get("net_itc_sgst"),
                "cess": None,
                "total": gt.get("net_itc_total"),
            },
        }

    # ---- TDS forms ----
    gt16 = _gt(manifest, "clean/form16_arjun_fy2526.pdf")
    results["clean/form16_arjun_fy2526.pdf"] = {
        "form_type": "Form 16",
        "pan": gt16.get("employee_pan"),
        "tan_of_deductor": gt16.get("employer_tan"),
        "deductor_name": gt16.get("employer_name"),
        "assessment_year": gt16.get("assessment_year"),
        "financial_year": gt16.get("financial_year"),
        "gross_salary": gt16.get("gross_salary"),
        "total_tds_deducted": gt16.get("total_tax_deducted"),
        "total_tds_deposited": gt16.get("total_tax_deposited"),
        "section_deductions": [{"section_code": "192", "tds_deducted": gt16.get("total_tax_deducted")}],
    }

    gt26 = _gt(manifest, "clean/form26as_arjun_ay2627.pdf")
    results["clean/form26as_arjun_ay2627.pdf"] = {
        "form_type": "Form 26AS",
        "pan": gt26.get("assessee_pan"),
        "tan_of_deductor": gt26.get("deductor_tan"),
        "deductor_name": gt26.get("deductor_name"),
        "assessment_year": gt26.get("assessment_year"),
        "financial_year": gt26.get("financial_year"),
        "total_amount_credited": gt26.get("total_amount_paid"),
        "total_tds_deducted": gt26.get("total_tds_deducted"),
        "total_tds_deposited": gt26.get("total_tds_deposited"),
    }

    # ---- investment proofs ----
    gt_lic = _gt(manifest, "clean/lic_receipt_arjun_80c.pdf")
    results["clean/lic_receipt_arjun_80c.pdf"] = {
        "pan": gt_lic.get("pan"),
        "taxpayer_name": gt_lic.get("policyholder"),
        "policy_account_no": gt_lic.get("policy_number"),
        "institution_name": gt_lic.get("institution"),
        "section": "80C",
        "amount_paid": gt_lic.get("total_premium_paid"),
        "financial_year": gt_lic.get("financial_year"),
    }

    gt_ppf = _gt(manifest, "clean/ppf_statement_arjun_80c.pdf")
    results["clean/ppf_statement_arjun_80c.pdf"] = {
        "pan": gt_ppf.get("pan"),
        "taxpayer_name": gt_ppf.get("subscriber_name"),
        "policy_account_no": gt_ppf.get("ppf_account_number"),
        "institution_name": gt_ppf.get("bank_name"),
        "section": "80C",
        "amount_paid": gt_ppf.get("deposits_in_fy"),
        "financial_year": gt_ppf.get("financial_year"),
        "notes": f"Interest credited: {gt_ppf.get('interest_credited')} | Closing balance: {gt_ppf.get('closing_balance')}",
    }

    # ---- edge case (payslip) — unknown, no extracted_data ----
    results["edge_cases/payslip_arjun_aug2026.pdf"] = None

    return results


# ---------------------------------------------------------------------------
# Main seed logic
# ---------------------------------------------------------------------------

async def wipe_all(session: AsyncSession) -> None:
    """Delete all existing data in reverse FK order."""
    print("  Wiping workflow_documents...")
    await session.execute(text("DELETE FROM workflow_documents"))
    print("  Wiping workflow_document_requirements...")
    await session.execute(text("DELETE FROM workflow_document_requirements"))
    print("  Wiping workflows...")
    await session.execute(text("DELETE FROM workflows"))
    print("  Wiping documents...")
    await session.execute(text("DELETE FROM documents"))
    print("  Wiping client_members...")
    await session.execute(text("DELETE FROM client_members"))
    print("  Wiping clients...")
    await session.execute(text("DELETE FROM clients"))
    print("  Wiping organizations...")
    await session.execute(text("DELETE FROM organizations"))
    await session.commit()
    print("  [DONE] All tables cleared.")


async def seed(session: AsyncSession, extracted_data_map: dict) -> None:
    now = datetime.now(timezone.utc)

    # -----------------------------------------------------------------------
    # Organization
    # -----------------------------------------------------------------------
    org_id = uuid.uuid4()
    await session.execute(text("""
        INSERT INTO organizations (id, name, slug, plan, created_at)
        VALUES (:id, :name, :slug, :plan, :created_at)
    """), {
        "id": org_id,
        "name": "Kapoor & Shah Associates",
        "slug": "default-org",
        "plan": "pro",
        "created_at": now,
    })
    print(f"  Org: Kapoor & Shah Associates ({org_id})")

    # -----------------------------------------------------------------------
    # Clients
    # -----------------------------------------------------------------------
    rajput_id = uuid.uuid4()
    codeify_id = uuid.uuid4()
    arjun_id = uuid.uuid4()

    clients = [
        {
            "id": rajput_id,
            "organization_id": org_id,
            "name": "Rajput Steelworks Pvt Ltd",
            "tax_id": "24AABCR5678Q1ZP",
            "email": "accounts@rajputsteelworks.in",
            "phone": "+91 98240 11223",
            "contact_person": "Vikram Rajput",
            "status": "on_track",
        },
        {
            "id": codeify_id,
            "organization_id": org_id,
            "name": "Codeify Technologies LLP",
            "tax_id": "27AAGFC4321N1ZT",
            "email": "finance@codeify.tech",
            "phone": "+91 98200 45678",
            "contact_person": "Ananya Iyer",
            "status": "review_required",
        },
        {
            "id": arjun_id,
            "organization_id": org_id,
            "name": "Arjun Khanna",
            "tax_id": "AKQPK7890G",   # PAN (individual, no GSTIN)
            "email": "arjun.khanna@gmail.com",
            "phone": "+91 98765 32100",
            "contact_person": "Arjun Khanna",
            "status": "on_track",
        },
    ]

    for c in clients:
        await session.execute(text("""
            INSERT INTO clients (id, organization_id, name, tax_id, email, phone, contact_person, status, created_at)
            VALUES (:id, :organization_id, :name, :tax_id, :email, :phone, :contact_person, :status, :created_at)
        """), {**c, "created_at": now})
        print(f"  Client: {c['name']} ({c['id']})")

    # -----------------------------------------------------------------------
    # Workflows
    # -----------------------------------------------------------------------
    wf_rajput_id = uuid.uuid4()
    wf_codeify_id = uuid.uuid4()
    wf_arjun_id = uuid.uuid4()

    workflows = [
        {
            "id": wf_rajput_id,
            "organization_id": org_id,
            "client_id": rajput_id,
            "name": "GST Filing — August 2026",
            "workflow_type": "gst_filing",
            "period_start": date(2026, 8, 1),
            "period_end": date(2026, 8, 31),
            "status": "ready_for_filing",
            "created_at": now,
        },
        {
            "id": wf_codeify_id,
            "organization_id": org_id,
            "client_id": codeify_id,
            "name": "GST Filing — August 2026",
            "workflow_type": "gst_filing",
            "period_start": date(2026, 8, 1),
            "period_end": date(2026, 8, 31),
            "status": "in_review",
            "created_at": now,
        },
        {
            "id": wf_arjun_id,
            "organization_id": org_id,
            "client_id": arjun_id,
            "name": "TDS / ITR Filing — FY 2025-26",
            "workflow_type": "tds_filing",
            "period_start": date(2025, 4, 1),
            "period_end": date(2026, 3, 31),
            "status": "collecting_documents",
            "created_at": now,
        },
    ]

    for wf in workflows:
        await session.execute(text("""
            INSERT INTO workflows (id, organization_id, client_id, name, workflow_type,
                                   period_start, period_end, status, created_at)
            VALUES (:id, :organization_id, :client_id, :name, :workflow_type,
                    :period_start, :period_end, :status, :created_at)
        """), wf)
        print(f"  Workflow: {wf['name']} → {wf['workflow_type']} ({wf['id']})")

    # -----------------------------------------------------------------------
    # WorkflowDocumentRequirements
    # -----------------------------------------------------------------------
    req_rajput_gstr3b  = uuid.uuid4()
    req_rajput_bank    = uuid.uuid4()
    req_rajput_invoice = uuid.uuid4()

    req_codeify_gstr3b  = uuid.uuid4()
    req_codeify_bank    = uuid.uuid4()
    req_codeify_invoice = uuid.uuid4()

    req_arjun_form16  = uuid.uuid4()
    req_arjun_form26  = uuid.uuid4()
    req_arjun_invest  = uuid.uuid4()

    requirements = [
        # Rajput GST filing
        {"id": req_rajput_gstr3b,  "workflow_id": wf_rajput_id, "document_type": "gst_return",     "label": "GSTR-3B Return",         "required_count": 1, "notes": "August 2026 return"},
        {"id": req_rajput_bank,    "workflow_id": wf_rajput_id, "document_type": "bank_statement",  "label": "Bank Statement",         "required_count": 1, "notes": "August 2026 — HDFC current account"},
        {"id": req_rajput_invoice, "workflow_id": wf_rajput_id, "document_type": "invoice",         "label": "Purchase/Sales Invoices","required_count": None, "notes": None},
        # Codeify GST filing
        {"id": req_codeify_gstr3b,  "workflow_id": wf_codeify_id, "document_type": "gst_return",    "label": "GSTR-3B Return",         "required_count": 1, "notes": "August 2026 — under review"},
        {"id": req_codeify_bank,    "workflow_id": wf_codeify_id, "document_type": "bank_statement", "label": "Bank Statement",         "required_count": 1, "notes": None},
        {"id": req_codeify_invoice, "workflow_id": wf_codeify_id, "document_type": "invoice",        "label": "Client Invoices",        "required_count": None, "notes": None},
        # Arjun TDS filing
        {"id": req_arjun_form16, "workflow_id": wf_arjun_id, "document_type": "tds_form",        "label": "Form 16 (Salary TDS)",     "required_count": 1, "notes": "FY 2025-26"},
        {"id": req_arjun_form26, "workflow_id": wf_arjun_id, "document_type": "tds_form",        "label": "Form 26AS / AIS",          "required_count": 1, "notes": "AY 2026-27"},
        {"id": req_arjun_invest, "workflow_id": wf_arjun_id, "document_type": "investment_proof","label": "80C Investment Proofs",    "required_count": None, "notes": "LIC, PPF, ELSS etc."},
    ]

    for req in requirements:
        await session.execute(text("""
            INSERT INTO workflow_document_requirements
                (id, workflow_id, document_type, label, required_count, notes)
            VALUES (:id, :workflow_id, :document_type, :label, :required_count, :notes)
        """), req)
    print(f"  Requirements: {len(requirements)} inserted")

    # -----------------------------------------------------------------------
    # Documents
    # -----------------------------------------------------------------------
    # Each entry: (filename_key, client_id, doc_type, status, ocr_conf, ext_conf,
    #              needs_review, review_reason, uploaded_at_offset_days)
    # uploaded_at_offset: days ago from now

    doc_specs = [
        # Rajput documents
        ("clean/invoice_rajput_rs0234.pdf",   rajput_id, "invoice",          "validated",    0.96, 0.94, False, None,                                               12),
        ("clean/invoice_rajput_rs0235.pdf",   rajput_id, "invoice",          "validated",    0.95, 0.93, False, None,                                               11),
        ("clean/bank_stmt_rajput_aug2026.pdf", rajput_id, "bank_statement",  "validated",    0.97, 0.95, False, None,                                               10),
        ("clean/gstr3b_rajput_aug2026.pdf",   rajput_id, "gst_return",       "validated",    0.97, 0.96, False, None,                                                9),
        # Codeify documents
        ("clean/invoice_codeify_ct0189.pdf",   codeify_id, "invoice",        "needs_review", 0.92, 0.85, True,  "Multi-page invoice; verify line-item totals",       7),
        ("clean/bank_stmt_codeify_aug2026.pdf",codeify_id, "bank_statement", "validated",    0.95, 0.91, False, None,                                                6),
        ("clean/gstr3b_codeify_aug2026.pdf",   codeify_id, "gst_return",     "needs_review", 0.93, 0.87, True,  "ITC reversal requires manual verification",         5),
        # Arjun documents
        ("clean/form16_arjun_fy2526.pdf",      arjun_id, "tds_form",         "validated",    0.97, 0.95, False, None,                                               14),
        ("clean/form26as_arjun_ay2627.pdf",    arjun_id, "tds_form",         "validated",    0.96, 0.93, False, None,                                               13),
        ("clean/lic_receipt_arjun_80c.pdf",    arjun_id, "investment_proof", "validated",    0.95, 0.92, False, None,                                                8),
        ("clean/ppf_statement_arjun_80c.pdf",  arjun_id, "investment_proof", "validated",    0.96, 0.94, False, None,                                                8),
        ("edge_cases/payslip_arjun_aug2026.pdf", arjun_id, "unknown",        "needs_review", 0.71, None, True,  "Document type unrecognized — may be payslip",       3),
    ]

    doc_ids: dict[str, uuid.UUID] = {}
    for spec in doc_specs:
        fname, client_id, doc_type, status, ocr_conf, ext_conf, needs_review, review_reason, days_ago = spec
        doc_id = uuid.uuid4()
        doc_ids[fname] = doc_id

        # Resolve filename to the flat PDFs directory
        short_name = fname.split("/")[-1]
        file_path = str(PDFS_DIR / short_name)

        from datetime import timedelta
        uploaded_at = now - timedelta(days=days_ago, hours=2)
        processed_at = uploaded_at + timedelta(minutes=3) if status != "uploaded" else None

        extracted_data = extracted_data_map.get(fname)
        metadata = {
            "page_count": 2 if "bank_stmt" in fname or "invoice_codeify" in fname else 1,
            "ocr_engine": "PP-OCRv5",
            "category": fname.split("/")[0],
        }

        await session.execute(text("""
            INSERT INTO documents (
                id, organization_id, client_id, source_filename, file_path,
                document_type, status, ocr_confidence, extraction_confidence,
                needs_human_review, review_reason, extracted_data, metadata,
                uploaded_at, processed_at
            ) VALUES (
                :id, :org_id, :client_id, :source_filename, :file_path,
                :document_type, :status, :ocr_confidence, :extraction_confidence,
                :needs_human_review, :review_reason, CAST(:extracted_data AS jsonb), CAST(:metadata AS jsonb),
                :uploaded_at, :processed_at
            )
        """), {
            "id": doc_id,
            "org_id": org_id,
            "client_id": client_id,
            "source_filename": short_name,
            "file_path": file_path,
            "document_type": doc_type,
            "status": status,
            "ocr_confidence": ocr_conf,
            "extraction_confidence": ext_conf,
            "needs_human_review": needs_review,
            "review_reason": review_reason,
            "extracted_data": json.dumps(extracted_data) if extracted_data else None,
            "metadata": json.dumps(metadata),
            "uploaded_at": uploaded_at,
            "processed_at": processed_at,
        })
        print(f"  Document: {short_name} → {doc_type} / {status}")

    # -----------------------------------------------------------------------
    # WorkflowDocuments (link documents to requirements)
    # -----------------------------------------------------------------------
    links = [
        # Rajput
        (wf_rajput_id, doc_ids["clean/gstr3b_rajput_aug2026.pdf"],    req_rajput_gstr3b),
        (wf_rajput_id, doc_ids["clean/bank_stmt_rajput_aug2026.pdf"], req_rajput_bank),
        (wf_rajput_id, doc_ids["clean/invoice_rajput_rs0234.pdf"],    req_rajput_invoice),
        (wf_rajput_id, doc_ids["clean/invoice_rajput_rs0235.pdf"],    req_rajput_invoice),
        # Codeify
        (wf_codeify_id, doc_ids["clean/gstr3b_codeify_aug2026.pdf"],    req_codeify_gstr3b),
        (wf_codeify_id, doc_ids["clean/bank_stmt_codeify_aug2026.pdf"], req_codeify_bank),
        (wf_codeify_id, doc_ids["clean/invoice_codeify_ct0189.pdf"],    req_codeify_invoice),
        # Arjun
        (wf_arjun_id, doc_ids["clean/form16_arjun_fy2526.pdf"],    req_arjun_form16),
        (wf_arjun_id, doc_ids["clean/form26as_arjun_ay2627.pdf"],  req_arjun_form26),
        (wf_arjun_id, doc_ids["clean/lic_receipt_arjun_80c.pdf"],  req_arjun_invest),
        (wf_arjun_id, doc_ids["clean/ppf_statement_arjun_80c.pdf"], req_arjun_invest),
        # Arjun payslip — attached to workflow but no requirement (unrecognized)
        (wf_arjun_id, doc_ids["edge_cases/payslip_arjun_aug2026.pdf"], None),
    ]

    for wf_id, doc_id, req_id in links:
        await session.execute(text("""
            INSERT INTO workflow_documents (id, workflow_id, document_id, requirement_id, added_at)
            VALUES (:id, :wf_id, :doc_id, :req_id, :added_at)
        """), {
            "id": uuid.uuid4(),
            "wf_id": wf_id,
            "doc_id": doc_id,
            "req_id": req_id,
            "added_at": now,
        })
    print(f"  WorkflowDocuments: {len(links)} links inserted")

    await session.commit()
    print("\n[DONE] Seed complete.")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def main(wipe_only: bool = False) -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with AsyncSession(engine) as session:
        print("\n=== Step 1: Wipe existing data ===")
        await wipe_all(session)

        if not wipe_only:
            print("\n=== Step 2: Load manifest ===")
            with open(MANIFEST_PATH) as f:
                manifest = json.load(f)
            extracted_data_map = build_extracted_data(manifest)
            print(f"  Built extracted_data for {len(extracted_data_map)} documents")

            print("\n=== Step 3: Seed ===")
            await seed(session, extracted_data_map)

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the AI Docs Orch database with realistic fixture data.")
    parser.add_argument("--wipe-only", action="store_true", help="Only wipe existing data, do not seed.")
    args = parser.parse_args()
    asyncio.run(main(wipe_only=args.wipe_only))
