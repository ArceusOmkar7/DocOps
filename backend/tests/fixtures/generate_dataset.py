"""
Master Synthetic Dataset Generator for Indian Accounting Documents.
Generates 22 PDFs across clean, scanned_good, scanned_poor, and edge_cases folders,
along with manifest.json documenting metadata and expected extraction targets.
"""
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure both project root and backend are in sys.path
_current_dir = Path(__file__).resolve().parent
_backend_dir = _current_dir.parent.parent
_root_dir = _backend_dir.parent

for p in [str(_root_dir), str(_backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.tests.fixtures.generators.invoice import (
        generate_invoice_rajput_rs0234,
        generate_invoice_rajput_rs0235,
        generate_invoice_codeify_ct0189,
    )
    from backend.tests.fixtures.generators.bank_statement import (
        generate_bank_stmt_rajput_aug2026,
        generate_bank_stmt_codeify_aug2026,
    )
    from backend.tests.fixtures.generators.gst_return import (
        generate_gstr3b_rajput_aug2026,
        generate_gstr3b_codeify_aug2026,
    )
    from backend.tests.fixtures.generators.tds_form import (
        generate_form16_arjun_fy2526,
        generate_form26as_arjun_ay2627,
    )
    from backend.tests.fixtures.generators.investment_proof import (
        generate_lic_receipt_arjun_80c,
        generate_ppf_statement_arjun_80c,
    )
    from backend.tests.fixtures.generators.edge_cases import (
        generate_payslip_arjun_aug2026,
        generate_blank_page,
    )
    from backend.tests.fixtures.degradation import DegradeConfig, scan_degrade
except ImportError:
    from tests.fixtures.generators.invoice import (
        generate_invoice_rajput_rs0234,
        generate_invoice_rajput_rs0235,
        generate_invoice_codeify_ct0189,
    )
    from tests.fixtures.generators.bank_statement import (
        generate_bank_stmt_rajput_aug2026,
        generate_bank_stmt_codeify_aug2026,
    )
    from tests.fixtures.generators.gst_return import (
        generate_gstr3b_rajput_aug2026,
        generate_gstr3b_codeify_aug2026,
    )
    from tests.fixtures.generators.tds_form import (
        generate_form16_arjun_fy2526,
        generate_form26as_arjun_ay2627,
    )
    from tests.fixtures.generators.investment_proof import (
        generate_lic_receipt_arjun_80c,
        generate_ppf_statement_arjun_80c,
    )
    from tests.fixtures.generators.edge_cases import (
        generate_payslip_arjun_aug2026,
        generate_blank_page,
    )
    from tests.fixtures.degradation import DegradeConfig, scan_degrade


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DatasetGenerator")


def build_all_documents(output_base: Path) -> Dict[str, Any]:
    clean_dir = output_base / "clean"
    good_dir = output_base / "scanned_good"
    poor_dir = output_base / "scanned_poor"
    edge_dir = output_base / "edge_cases"

    for d in [clean_dir, good_dir, poor_dir, edge_dir]:
        d.mkdir(parents=True, exist_ok=True)

    manifest_entries = []

    # ==========================================
    # 1. CATEGORY A: CLEAN DIGITAL BORN (11 PDFs)
    # ==========================================
    logger.info("Generating Clean documents (11 files)...")

    # 1. invoice_rajput_rs0234.pdf
    p = clean_dir / "invoice_rajput_rs0234.pdf"
    meta = generate_invoice_rajput_rs0234(p)
    manifest_entries.append({
        "filename": "clean/invoice_rajput_rs0234.pdf",
        "category_folder": "clean",
        "expected_classification": "invoice",
        "ground_truth": meta,
    })

    # 2. invoice_rajput_rs0235.pdf
    p = clean_dir / "invoice_rajput_rs0235.pdf"
    meta = generate_invoice_rajput_rs0235(p)
    manifest_entries.append({
        "filename": "clean/invoice_rajput_rs0235.pdf",
        "category_folder": "clean",
        "expected_classification": "invoice",
        "ground_truth": meta,
    })

    # 3. invoice_codeify_ct0189.pdf
    p = clean_dir / "invoice_codeify_ct0189.pdf"
    meta = generate_invoice_codeify_ct0189(p)
    manifest_entries.append({
        "filename": "clean/invoice_codeify_ct0189.pdf",
        "category_folder": "clean",
        "expected_classification": "invoice",
        "ground_truth": meta,
    })

    # 4. bank_stmt_rajput_aug2026.pdf
    p = clean_dir / "bank_stmt_rajput_aug2026.pdf"
    meta = generate_bank_stmt_rajput_aug2026(p)
    manifest_entries.append({
        "filename": "clean/bank_stmt_rajput_aug2026.pdf",
        "category_folder": "clean",
        "expected_classification": "bank_statement",
        "ground_truth": meta,
    })

    # 5. bank_stmt_codeify_aug2026.pdf
    p = clean_dir / "bank_stmt_codeify_aug2026.pdf"
    meta = generate_bank_stmt_codeify_aug2026(p)
    manifest_entries.append({
        "filename": "clean/bank_stmt_codeify_aug2026.pdf",
        "category_folder": "clean",
        "expected_classification": "bank_statement",
        "ground_truth": meta,
    })

    # 6. gstr3b_rajput_aug2026.pdf
    p = clean_dir / "gstr3b_rajput_aug2026.pdf"
    meta = generate_gstr3b_rajput_aug2026(p)
    manifest_entries.append({
        "filename": "clean/gstr3b_rajput_aug2026.pdf",
        "category_folder": "clean",
        "expected_classification": "gst_return",
        "ground_truth": meta,
    })

    # 7. gstr3b_codeify_aug2026.pdf
    p = clean_dir / "gstr3b_codeify_aug2026.pdf"
    meta = generate_gstr3b_codeify_aug2026(p)
    manifest_entries.append({
        "filename": "clean/gstr3b_codeify_aug2026.pdf",
        "category_folder": "clean",
        "expected_classification": "gst_return",
        "ground_truth": meta,
    })

    # 8. form16_arjun_fy2526.pdf
    p = clean_dir / "form16_arjun_fy2526.pdf"
    meta = generate_form16_arjun_fy2526(p)
    manifest_entries.append({
        "filename": "clean/form16_arjun_fy2526.pdf",
        "category_folder": "clean",
        "expected_classification": "tds_form",
        "ground_truth": meta,
    })

    # 9. form26as_arjun_ay2627.pdf
    p = clean_dir / "form26as_arjun_ay2627.pdf"
    meta = generate_form26as_arjun_ay2627(p)
    manifest_entries.append({
        "filename": "clean/form26as_arjun_ay2627.pdf",
        "category_folder": "clean",
        "expected_classification": "tds_form",
        "ground_truth": meta,
    })

    # 10. lic_receipt_arjun_80c.pdf
    p = clean_dir / "lic_receipt_arjun_80c.pdf"
    meta = generate_lic_receipt_arjun_80c(p)
    manifest_entries.append({
        "filename": "clean/lic_receipt_arjun_80c.pdf",
        "category_folder": "clean",
        "expected_classification": "investment_proof",
        "ground_truth": meta,
    })

    # 11. ppf_statement_arjun_80c.pdf
    p = clean_dir / "ppf_statement_arjun_80c.pdf"
    meta = generate_ppf_statement_arjun_80c(p)
    manifest_entries.append({
        "filename": "clean/ppf_statement_arjun_80c.pdf",
        "category_folder": "clean",
        "expected_classification": "investment_proof",
        "ground_truth": meta,
    })

    # ==========================================
    # 2. CATEGORY B: SCANNED GOOD (5 PDFs)
    # ==========================================
    logger.info("Generating Scanned Good documents (5 files)...")

    # 12. invoice_rajput_rs0234_scan.pdf
    dst = good_dir / "invoice_rajput_rs0234_scan.pdf"
    scan_degrade(
        clean_dir / "invoice_rajput_rs0234.pdf",
        dst,
        DegradeConfig(dpi=200, rotation_angle=0.5, noise_sigma=4.0, jpeg_quality=80),
    )
    manifest_entries.append({
        "filename": "scanned_good/invoice_rajput_rs0234_scan.pdf",
        "category_folder": "scanned_good",
        "source_pdf": "clean/invoice_rajput_rs0234.pdf",
        "expected_classification": "invoice",
        "degradation": "200 DPI flatbed, +0.5 deg rotation, sigma=4 noise, q=80",
    })

    # 13. bank_stmt_rajput_scan.pdf (page 1)
    dst = good_dir / "bank_stmt_rajput_scan.pdf"
    scan_degrade(
        clean_dir / "bank_stmt_rajput_aug2026.pdf",
        dst,
        DegradeConfig(dpi=200, rotation_angle=-0.4, grey_background=True, jpeg_quality=80, page_indices=[0]),
    )
    manifest_entries.append({
        "filename": "scanned_good/bank_stmt_rajput_scan.pdf",
        "category_folder": "scanned_good",
        "source_pdf": "clean/bank_stmt_rajput_aug2026.pdf (page 1)",
        "expected_classification": "bank_statement",
        "degradation": "200 DPI, -0.4 deg rotation, grey unbleached paper tint",
    })

    # 14. gstr3b_rajput_scan.pdf
    dst = good_dir / "gstr3b_rajput_scan.pdf"
    scan_degrade(
        clean_dir / "gstr3b_rajput_aug2026.pdf",
        dst,
        DegradeConfig(dpi=200, rotation_angle=0.3, noise_sigma=5.0, stamp_text="FILED", jpeg_quality=80),
    )
    manifest_entries.append({
        "filename": "scanned_good/gstr3b_rajput_scan.pdf",
        "category_folder": "scanned_good",
        "source_pdf": "clean/gstr3b_rajput_aug2026.pdf",
        "expected_classification": "gst_return",
        "degradation": "200 DPI, +0.3 deg rotation, FILED rubber stamp, sigma=5 noise",
    })

    # 15. form16_arjun_scan.pdf
    dst = good_dir / "form16_arjun_scan.pdf"
    scan_degrade(
        clean_dir / "form16_arjun_fy2526.pdf",
        dst,
        DegradeConfig(dpi=200, rotation_angle=0.7, noise_sigma=3.0, jpeg_quality=82),
    )
    manifest_entries.append({
        "filename": "scanned_good/form16_arjun_scan.pdf",
        "category_folder": "scanned_good",
        "source_pdf": "clean/form16_arjun_fy2526.pdf",
        "expected_classification": "tds_form",
        "degradation": "200 DPI ADF feeder skew +0.7 deg, 2 pages, q=82",
    })

    # 16. lic_receipt_arjun_scan.pdf
    dst = good_dir / "lic_receipt_arjun_scan.pdf"
    scan_degrade(
        clean_dir / "lic_receipt_arjun_80c.pdf",
        dst,
        DegradeConfig(dpi=200, rotation_angle=-0.3, crease_line=True, noise_sigma=3.0, jpeg_quality=80),
    )
    manifest_entries.append({
        "filename": "scanned_good/lic_receipt_arjun_scan.pdf",
        "category_folder": "scanned_good",
        "source_pdf": "clean/lic_receipt_arjun_80c.pdf",
        "expected_classification": "investment_proof",
        "degradation": "200 DPI, fold crease line artifact across midpoint",
    })

    # ==========================================
    # 3. CATEGORY C: SCANNED POOR / MOBILE (4 PDFs)
    # ==========================================
    logger.info("Generating Scanned Poor / Mobile documents (4 files)...")

    # 17. invoice_codeify_ct0189_mobile.pdf (page 1)
    dst = poor_dir / "invoice_codeify_ct0189_mobile.pdf"
    scan_degrade(
        clean_dir / "invoice_codeify_ct0189.pdf",
        dst,
        DegradeConfig(
            dpi=150,
            rotation_angle=-2.8,
            noise_sigma=16.0,
            brightness=1.18,
            perspective_tilt=True,
            jpeg_quality=60,
            page_indices=[0],
        ),
    )
    manifest_entries.append({
        "filename": "scanned_poor/invoice_codeify_ct0189_mobile.pdf",
        "category_folder": "scanned_poor",
        "source_pdf": "clean/invoice_codeify_ct0189.pdf (page 1)",
        "expected_classification": "invoice",
        "degradation": "150 DPI mobile photo, -2.8 deg rotation, perspective keystoning, sigma=16 noise, brightened",
    })

    # 18. bank_stmt_codeify_mobile.pdf (page 2)
    dst = poor_dir / "bank_stmt_codeify_mobile.pdf"
    scan_degrade(
        clean_dir / "bank_stmt_codeify_aug2026.pdf",
        dst,
        DegradeConfig(
            dpi=150,
            rotation_angle=1.8,
            shadow_edge="left",
            noise_sigma=10.0,
            jpeg_quality=65,
            page_indices=[1],
        ),
    )
    manifest_entries.append({
        "filename": "scanned_poor/bank_stmt_codeify_mobile.pdf",
        "category_folder": "scanned_poor",
        "source_pdf": "clean/bank_stmt_codeify_aug2026.pdf (page 2)",
        "expected_classification": "bank_statement",
        "degradation": "150 DPI mobile capture with hand/room shadow gradient on left edge, +1.8 deg rotation",
    })

    # 19. form26as_arjun_mobile.pdf (page 1)
    dst = poor_dir / "form26as_arjun_mobile.pdf"
    scan_degrade(
        clean_dir / "form26as_arjun_ay2627.pdf",
        dst,
        DegradeConfig(
            dpi=150,
            rotation_angle=3.5,
            brightness=1.24,
            contrast=0.88,
            noise_sigma=12.0,
            jpeg_quality=65,
            page_indices=[0],
        ),
    )
    manifest_entries.append({
        "filename": "scanned_poor/form26as_arjun_mobile.pdf",
        "category_folder": "scanned_poor",
        "source_pdf": "clean/form26as_arjun_ay2627.pdf (page 1)",
        "expected_classification": "tds_form",
        "degradation": "150 DPI mobile photo, washed out / low contrast, +3.5 deg tilt, high noise",
    })

    # 20. ppf_statement_arjun_mobile.pdf
    dst = poor_dir / "ppf_statement_arjun_mobile.pdf"
    scan_degrade(
        clean_dir / "ppf_statement_arjun_80c.pdf",
        dst,
        DegradeConfig(
            dpi=150,
            rotation_angle=-2.2,
            blur_radius=1.2,
            noise_sigma=14.0,
            jpeg_quality=65,
        ),
    )
    manifest_entries.append({
        "filename": "scanned_poor/ppf_statement_arjun_mobile.pdf",
        "category_folder": "scanned_poor",
        "source_pdf": "clean/ppf_statement_arjun_80c.pdf",
        "expected_classification": "investment_proof",
        "degradation": "150 DPI slightly out-of-focus camera capture (1.2px blur), -2.2 deg tilt, noise",
    })

    # ==========================================
    # 4. CATEGORY D: EDGE CASES (2 PDFs)
    # ==========================================
    logger.info("Generating Edge Cases (2 files)...")

    # 21. payslip_arjun_aug2026.pdf
    p = edge_dir / "payslip_arjun_aug2026.pdf"
    meta = generate_payslip_arjun_aug2026(p)
    manifest_entries.append({
        "filename": "edge_cases/payslip_arjun_aug2026.pdf",
        "category_folder": "edge_cases",
        "expected_classification": "unknown",
        "ground_truth": meta,
        "notes": "Legitimate salary payslip; expected classification is 'unknown' as payslip is not a primary tax/statutory doc type.",
    })

    # 22. blank_page.pdf
    p = edge_dir / "blank_page.pdf"
    meta = generate_blank_page(p)
    manifest_entries.append({
        "filename": "edge_cases/blank_page.pdf",
        "category_folder": "edge_cases",
        "expected_classification": "unknown",
        "ground_truth": meta,
        "notes": "Blank A4 page to test pipeline robustness on empty/near-empty OCR returns.",
    })

    # ==========================================
    # MANIFEST.JSON
    # ==========================================
    manifest = {
        "dataset_name": "Indian Accounting Documents Synthetic Dataset",
        "version": "1.0",
        "total_documents": len(manifest_entries),
        "breakdown": {
            "clean": 11,
            "scanned_good": 5,
            "scanned_poor": 4,
            "edge_cases": 2,
        },
        "documents": manifest_entries,
    }

    manifest_path = output_base / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"Successfully generated all {len(manifest_entries)} documents!")
    logger.info(f"Manifest written to: {manifest_path}")

    return manifest


def verify_dataset(output_base: Path) -> bool:
    """
    Verifies that all 22 documents exist, are valid PDFs, can be rendered,
    and all ground-truth mathematical and cross-referential constraints hold.
    """
    import pymupdf

    manifest_path = output_base / "manifest.json"
    if not manifest_path.exists():
        logger.error(f"Manifest not found: {manifest_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    docs = manifest.get("documents", [])
    logger.info(f"--- Verifying Dataset ({len(docs)} documents listed in manifest) ---")

    passed_files = 0
    failed_files = 0
    all_passed = True

    # 1. File existence, size, and PDF parsing check
    for item in docs:
        rel_path = item["filename"]
        full_path = output_base / rel_path
        if not full_path.exists():
            logger.error(f"[FAIL] Missing file: {rel_path}")
            failed_files += 1
            all_passed = False
            continue

        size = full_path.stat().st_size
        if size == 0:
            logger.error(f"[FAIL] Empty file: {rel_path}")
            failed_files += 1
            all_passed = False
            continue

        try:
            doc = pymupdf.open(str(full_path))
            pages = len(doc)
            # Verify every page can be rendered
            for page_idx in range(pages):
                _ = doc[page_idx].get_pixmap(dpi=72)
            doc.close()
            logger.info(f"[PASS] {rel_path:<40} | {pages} pg(s) | {size:>7} bytes | class: {item['expected_classification']}")
            passed_files += 1
        except Exception as e:
            logger.error(f"[FAIL] Corruption in {rel_path}: {e}")
            failed_files += 1
            all_passed = False

    # 2. Mathematical Consistency Checks on Clean documents
    logger.info("--- Verifying Ground Truth Financial Mathematics ---")
    doc_map = {item["filename"]: item for item in docs}

    # Invoices
    inv1 = doc_map["clean/invoice_rajput_rs0234.pdf"]["ground_truth"]
    assert round(inv1["subtotal"] + inv1["cgst"] + inv1["sgst"] + inv1["igst"], 2) == round(inv1["total"], 2)
    logger.info(f"[PASS] Math: RS0234 subtotal ({inv1['subtotal']}) + taxes ({inv1['cgst']}+{inv1['sgst']}) == total ({inv1['total']})")

    inv2 = doc_map["clean/invoice_rajput_rs0235.pdf"]["ground_truth"]
    assert round(inv2["subtotal"] + inv2["igst"], 2) == round(inv2["total"], 2)
    logger.info(f"[PASS] Math: RS0235 subtotal ({inv2['subtotal']}) + IGST ({inv2['igst']}) == total ({inv2['total']})")

    inv3 = doc_map["clean/invoice_codeify_ct0189.pdf"]["ground_truth"]
    assert round(inv3["subtotal"] + inv3["igst"], 2) == round(inv3["total"], 2)
    logger.info(f"[PASS] Math: CT0189 subtotal ({inv3['subtotal']}) + IGST ({inv3['igst']}) == total ({inv3['total']})")

    # Bank Statements
    stmt1 = doc_map["clean/bank_stmt_rajput_aug2026.pdf"]["ground_truth"]
    assert round(stmt1["opening_balance"] + stmt1["total_credits"] - stmt1["total_debits"], 2) == round(stmt1["closing_balance"], 2)
    logger.info(f"[PASS] Math: Rajput SBI Stmt opening ({stmt1['opening_balance']}) + cr ({stmt1['total_credits']}) - dr ({stmt1['total_debits']}) == closing ({stmt1['closing_balance']})")

    stmt2 = doc_map["clean/bank_stmt_codeify_aug2026.pdf"]["ground_truth"]
    assert round(stmt2["opening_balance"] + stmt2["total_credits"] - stmt2["total_debits"], 2) == round(stmt2["closing_balance"], 2)
    logger.info(f"[PASS] Math: Codeify Axis Stmt opening ({stmt2['opening_balance']}) + cr ({stmt2['total_credits']}) - dr ({stmt2['total_debits']}) == closing ({stmt2['closing_balance']})")

    # GST Returns
    gst1 = doc_map["clean/gstr3b_rajput_aug2026.pdf"]["ground_truth"]
    assert round(gst1["itc_available_total"] - gst1["itc_reversed_total"], 2) == round(gst1["net_itc_total"], 2)
    logger.info(f"[PASS] Math: Rajput GSTR-3B ITC available ({gst1['itc_available_total']}) - reversed ({gst1['itc_reversed_total']}) == net ITC ({gst1['net_itc_total']})")

    gst2 = doc_map["clean/gstr3b_codeify_aug2026.pdf"]["ground_truth"]
    assert round(gst2["itc_available_total"] - gst2["itc_reversed_total"], 2) == round(gst2["net_itc_total"], 2)
    logger.info(f"[PASS] Math: Codeify GSTR-3B ITC available ({gst2['itc_available_total']}) - reversed ({gst2['itc_reversed_total']}) == net ITC ({gst2['net_itc_total']})")

    # TDS Cross-Referencing
    f16 = doc_map["clean/form16_arjun_fy2526.pdf"]["ground_truth"]
    f26 = doc_map["clean/form26as_arjun_ay2627.pdf"]["ground_truth"]
    assert f16["employer_tan"] == f26["deductor_tan"]
    assert f16["employee_pan"] == f26["assessee_pan"]
    assert round(f16["gross_salary"], 2) == round(f26["total_amount_paid"], 2)
    assert round(f16["total_tax_deposited"], 2) == round(f26["total_tds_deposited"], 2)
    logger.info(f"[PASS] Cross-Ref: Form 16 & Form 26AS match on TAN ({f16['employer_tan']}), Gross Salary ({f16['gross_salary']}), and TDS ({f16['total_tax_deposited']})")

    # Investment Proofs vs Form 16
    lic = doc_map["clean/lic_receipt_arjun_80c.pdf"]["ground_truth"]
    ppf = doc_map["clean/ppf_statement_arjun_80c.pdf"]["ground_truth"]
    assert round(lic["eligible_80c_amount"] + ppf["eligible_80c_amount"], 2) == 150000.00
    logger.info(f"[PASS] Cross-Ref: LIC (Rs. {lic['eligible_80c_amount']}) + PPF (Rs. {ppf['eligible_80c_amount']}) == Rs. 1,50,000 (Section 80C cap on Form 16 Part B)")

    logger.info(f"--- Verification Summary: {passed_files}/22 files passed, {failed_files} failed ---")
    return all_passed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Synthetic Accounting Document Dataset Generator & Verifier")
    parser.add_argument("--verify", action="store_true", help="Run validation checks on existing dataset")
    parser.add_argument("--generate", action="store_true", help="Generate all documents (default if no flag given)")
    args = parser.parse_args()

    base_output = Path(__file__).resolve().parent / "pdfs"

    if args.verify:
        success = verify_dataset(base_output)
        sys.exit(0 if success else 1)
    else:
        build_all_documents(base_output)
        success = verify_dataset(base_output)
        sys.exit(0 if success else 1)

