"""
Integrity tests for synthetic accounting document dataset.
Verifies all 22 PDFs, rendering, manifest entries, and ground-truth financial math.
"""
from pathlib import Path
import json
import pytest
import pymupdf


@pytest.fixture(scope="module")
def dataset_info():
    base_dir = Path(__file__).resolve().parent / "pdfs"
    manifest_path = base_dir / "manifest.json"
    assert manifest_path.exists(), f"manifest.json missing at {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    return {"base_dir": base_dir, "manifest": manifest}


def test_manifest_structure(dataset_info):
    manifest = dataset_info["manifest"]
    assert manifest["total_documents"] == 22
    assert len(manifest["documents"]) == 22
    assert manifest["breakdown"] == {
        "clean": 11,
        "scanned_good": 5,
        "scanned_poor": 4,
        "edge_cases": 2,
    }


def test_all_pdf_files_exist_and_render(dataset_info):
    base_dir = dataset_info["base_dir"]
    manifest = dataset_info["manifest"]

    for item in manifest["documents"]:
        rel_path = item["filename"]
        pdf_path = base_dir / rel_path
        assert pdf_path.exists(), f"File missing: {rel_path}"
        assert pdf_path.stat().st_size > 0, f"File is empty: {rel_path}"

        # PyMuPDF rendering validation
        doc = pymupdf.open(str(pdf_path))
        assert len(doc) >= 1, f"No pages found in {rel_path}"
        for idx in range(len(doc)):
            pix = doc[idx].get_pixmap(dpi=72)
            assert pix.width > 0 and pix.height > 0
        doc.close()


def test_invoice_math(dataset_info):
    manifest = dataset_info["manifest"]
    doc_map = {d["filename"]: d for d in manifest["documents"]}

    # RS0234
    inv1 = doc_map["clean/invoice_rajput_rs0234.pdf"]["ground_truth"]
    assert round(inv1["subtotal"] + inv1["cgst"] + inv1["sgst"] + inv1["igst"], 2) == round(inv1["total"], 2)

    # RS0235
    inv2 = doc_map["clean/invoice_rajput_rs0235.pdf"]["ground_truth"]
    assert round(inv2["subtotal"] + inv2["igst"], 2) == round(inv2["total"], 2)

    # CT0189
    inv3 = doc_map["clean/invoice_codeify_ct0189.pdf"]["ground_truth"]
    assert round(inv3["subtotal"] + inv3["igst"], 2) == round(inv3["total"], 2)


def test_bank_statement_math(dataset_info):
    manifest = dataset_info["manifest"]
    doc_map = {d["filename"]: d for d in manifest["documents"]}

    # Rajput SBI
    stmt1 = doc_map["clean/bank_stmt_rajput_aug2026.pdf"]["ground_truth"]
    assert round(stmt1["opening_balance"] + stmt1["total_credits"] - stmt1["total_debits"], 2) == round(stmt1["closing_balance"], 2)
    assert stmt1["transaction_count"] == 35

    # Codeify Axis
    stmt2 = doc_map["clean/bank_stmt_codeify_aug2026.pdf"]["ground_truth"]
    assert round(stmt2["opening_balance"] + stmt2["total_credits"] - stmt2["total_debits"], 2) == round(stmt2["closing_balance"], 2)
    assert stmt2["transaction_count"] == 28


def test_gstr3b_itc_math(dataset_info):
    manifest = dataset_info["manifest"]
    doc_map = {d["filename"]: d for d in manifest["documents"]}

    gst1 = doc_map["clean/gstr3b_rajput_aug2026.pdf"]["ground_truth"]
    assert round(gst1["itc_available_total"] - gst1["itc_reversed_total"], 2) == round(gst1["net_itc_total"], 2)

    gst2 = doc_map["clean/gstr3b_codeify_aug2026.pdf"]["ground_truth"]
    assert round(gst2["itc_available_total"] - gst2["itc_reversed_total"], 2) == round(gst2["net_itc_total"], 2)


def test_tds_cross_referencing(dataset_info):
    manifest = dataset_info["manifest"]
    doc_map = {d["filename"]: d for d in manifest["documents"]}

    f16 = doc_map["clean/form16_arjun_fy2526.pdf"]["ground_truth"]
    f26 = doc_map["clean/form26as_arjun_ay2627.pdf"]["ground_truth"]
    assert f16["employer_tan"] == f26["deductor_tan"]
    assert f16["employee_pan"] == f26["assessee_pan"]
    assert round(f16["gross_salary"], 2) == round(f26["total_amount_paid"], 2)
    assert round(f16["total_tax_deposited"], 2) == round(f26["total_tds_deposited"], 2)


def test_investment_proof_80c_cap(dataset_info):
    manifest = dataset_info["manifest"]
    doc_map = {d["filename"]: d for d in manifest["documents"]}

    lic = doc_map["clean/lic_receipt_arjun_80c.pdf"]["ground_truth"]
    ppf = doc_map["clean/ppf_statement_arjun_80c.pdf"]["ground_truth"]
    assert round(lic["eligible_80c_amount"] + ppf["eligible_80c_amount"], 2) == 150000.00
