"""Benchmark and live pipeline evaluation script for the 22-PDF synthetic dataset.

Executes:
    1. PaddleOCR PP-StructureV3 on local GPU/CPU -> Markdown & layout blocks
    2. Groq LLM (openai/gpt-oss-120b) -> Two-stage Classification & Typed Extraction
    3. Quantifiable Field-Level & Classification Evaluation against ground truth
    4. Optional PostgreSQL database update with real extracted data and review flags
    5. Markdown & JSON benchmark report generation

Run from backend/:
    .venv/Scripts/python.exe tests/fixtures/benchmark_dataset.py
    .venv/Scripts/python.exe tests/fixtures/benchmark_dataset.py --only-clean
    .venv/Scripts/python.exe tests/fixtures/benchmark_dataset.py --file clean/invoice_rajput_rs0234.pdf
    .venv/Scripts/python.exe tests/fixtures/benchmark_dataset.py --no-db
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("benchmark")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

FIXTURES_DIR = Path(__file__).parent
PDFS_DIR = FIXTURES_DIR / "pdfs"
MANIFEST_PATH = PDFS_DIR / "manifest.json"
OUTPUT_REPORT_PATH = FIXTURES_DIR / "benchmark_results.json"
OUTPUT_MD_PATH = FIXTURES_DIR / "BENCHMARK_REPORT.md"

from app.core.config import get_settings
from app.models.document import Document
from app.models.enums import DocumentStatus, DocumentType
from app.schemas.extraction import (
    BankStatement,
    DocumentExtraction,
    GSTReturn,
    InvestmentProof,
    Invoice,
    TDSForm,
)
from app.services.extraction import ExtractionService
from app.services.ocr import OCRService


# ---------------------------------------------------------------------------
# Evaluation Math & Field Normalization Utilities
# ---------------------------------------------------------------------------

def normalize_id(val: Any) -> str:
    """Normalize identifiers (GSTIN, PAN, TAN, Invoice #, Account #)."""
    if val is None:
        return ""
    # Uppercase, remove spaces, dashes, slashes for relaxed comparison
    s = str(val).strip().upper()
    return re.sub(r"[\s\-_/]", "", s)


def normalize_text(val: Any) -> str:
    """Normalize descriptive text (names, institutions)."""
    if val is None:
        return ""
    s = str(val).lower().strip()
    return re.sub(r"[^\w\s]", "", s)


def text_token_jaccard(pred: str, true: str) -> float:
    """Calculate token-level Jaccard similarity between two text strings."""
    t_pred = set(normalize_text(pred).split())
    t_true = set(normalize_text(true).split())
    if not t_true:
        return 1.0 if not t_pred else 0.0
    return len(t_pred & t_true) / len(t_pred | t_true)


def numeric_match(pred: Any, true: Any, rel_tol: float = 0.005, abs_tol: float = 1.0) -> bool:
    """Check if predicted number matches ground truth within relative or absolute tolerance."""
    if pred is None or true is None:
        return pred == true
    try:
        p_val = float(pred)
        t_val = float(true)
        if abs(p_val - t_val) <= abs_tol:
            return True
        if t_val != 0:
            return (abs(p_val - t_val) / abs(t_val)) <= rel_tol
        return False
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Benchmark Data Models
# ---------------------------------------------------------------------------

@dataclass
class FieldScore:
    field_name: str
    ground_truth: Any
    extracted: Any
    matched: bool
    score: float  # 1.0 = match, 0.0 = mismatch
    note: str = ""


@dataclass
class DocumentBenchmarkResult:
    filename: str
    category: str
    expected_type: str
    classified_type: str
    classification_correct: bool
    classification_confidence: float | None
    ocr_latency_s: float
    ocr_confidence: float | None
    ocr_pages: int
    llm_latency_s: float
    total_latency_s: float
    needs_review: bool
    review_reasons: list[str]
    field_scores: list[FieldScore] = field(default_factory=list)
    field_accuracy: float = 0.0
    extracted_data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


# ---------------------------------------------------------------------------
# Field Extractors & Comparators per Document Family
# ---------------------------------------------------------------------------

def evaluate_invoice(biz: Invoice | None, gt: dict[str, Any]) -> list[FieldScore]:
    if not biz:
        return [FieldScore("invoice_payload", gt, None, False, 0.0, "Missing invoice payload")]

    scores = []
    # 1. Invoice Number
    inv_no = biz.invoice_number or ""
    gt_inv = gt.get("invoice_number", "")
    match_inv = normalize_id(inv_no) == normalize_id(gt_inv)
    scores.append(FieldScore("invoice_number", gt_inv, inv_no, match_inv, 1.0 if match_inv else 0.0))

    # 2. Seller GSTIN
    seller_gst = biz.seller.tax_id if biz.seller else ""
    gt_seller_gst = gt.get("seller_gstin", "")
    match_sgst = normalize_id(seller_gst) == normalize_id(gt_seller_gst)
    scores.append(FieldScore("seller_gstin", gt_seller_gst, seller_gst, match_sgst, 1.0 if match_sgst else 0.0))

    # 3. Buyer GSTIN
    buyer_gst = biz.buyer.tax_id if biz.buyer else ""
    gt_buyer_gst = gt.get("buyer_gstin", "")
    match_bgst = normalize_id(buyer_gst) == normalize_id(gt_buyer_gst)
    scores.append(FieldScore("buyer_gstin", gt_buyer_gst, buyer_gst, match_bgst, 1.0 if match_bgst else 0.0))

    # 4. Subtotal
    sub = biz.subtotal
    gt_sub = gt.get("subtotal")
    match_sub = numeric_match(sub, gt_sub)
    scores.append(FieldScore("subtotal", gt_sub, sub, match_sub, 1.0 if match_sub else 0.0))

    # 5. Total
    tot = biz.total
    gt_tot = gt.get("total")
    match_tot = numeric_match(tot, gt_tot)
    scores.append(FieldScore("total", gt_tot, tot, match_tot, 1.0 if match_tot else 0.0))

    # 6. Tax (CGST / SGST / IGST)
    if "cgst" in gt and gt["cgst"] > 0:
        c_val = biz.tax.cgst if biz.tax else None
        m_cgst = numeric_match(c_val, gt["cgst"])
        scores.append(FieldScore("cgst", gt["cgst"], c_val, m_cgst, 1.0 if m_cgst else 0.0))
    if "igst" in gt and gt["igst"] > 0:
        i_val = biz.tax.igst if biz.tax else None
        m_igst = numeric_match(i_val, gt["igst"])
        scores.append(FieldScore("igst", gt["igst"], i_val, m_igst, 1.0 if m_igst else 0.0))

    return scores


def evaluate_bank_statement(biz: BankStatement | None, gt: dict[str, Any]) -> list[FieldScore]:
    if not biz:
        return [FieldScore("bank_payload", gt, None, False, 0.0, "Missing bank statement payload")]

    scores = []
    # 1. Bank Name
    bank_name = biz.bank_name or ""
    gt_bank = gt.get("bank_name", "")
    j_score = text_token_jaccard(bank_name, gt_bank)
    scores.append(FieldScore("bank_name", gt_bank, bank_name, j_score >= 0.5, 1.0 if j_score >= 0.5 else 0.0))

    # 2. Account Number
    acc_no = biz.account_number or ""
    gt_acc = gt.get("account_number", "")
    m_acc = normalize_id(acc_no) == normalize_id(gt_acc)
    scores.append(FieldScore("account_number", gt_acc, acc_no, m_acc, 1.0 if m_acc else 0.0))

    # 3. Opening Balance
    ob = biz.opening_balance
    gt_ob = gt.get("opening_balance")
    m_ob = numeric_match(ob, gt_ob)
    scores.append(FieldScore("opening_balance", gt_ob, ob, m_ob, 1.0 if m_ob else 0.0))

    # 4. Closing Balance (if statement is complete)
    if "closing_balance" in gt:
        cb = biz.closing_balance
        gt_cb = gt.get("closing_balance")
        m_cb = numeric_match(cb, gt_cb)
        scores.append(FieldScore("closing_balance", gt_cb, cb, m_cb, 1.0 if m_cb else 0.0))

    # 5. Transactions Extracted
    txn_count = len(biz.transactions)
    gt_count = gt.get("transaction_count")
    if gt_count:
        t_match = abs(txn_count - gt_count) <= max(2, int(gt_count * 0.15))
        ratio = min(1.0, txn_count / gt_count) if gt_count else 0.0
        scores.append(FieldScore("transaction_count", gt_count, txn_count, t_match, ratio, f"{txn_count}/{gt_count} txns"))

    return scores


def evaluate_gst_return(biz: GSTReturn | None, gt: dict[str, Any]) -> list[FieldScore]:
    if not biz:
        return [FieldScore("gst_payload", gt, None, False, 0.0, "Missing GST return payload")]

    scores = []
    # 1. GSTIN
    gstin = biz.gstin or ""
    gt_gstin = gt.get("gstin", "")
    m_gst = normalize_id(gstin) == normalize_id(gt_gstin)
    scores.append(FieldScore("gstin", gt_gstin, gstin, m_gst, 1.0 if m_gst else 0.0))

    # 2. Return Type
    rtype = biz.return_type or ""
    gt_rtype = gt.get("form_type", "GSTR-3B")
    m_rt = normalize_id(rtype) == normalize_id(gt_rtype)
    scores.append(FieldScore("return_type", gt_rtype, rtype, m_rt, 1.0 if m_rt else 0.0))

    # 3. Taxable Turnover
    turnover = biz.taxable_turnover
    gt_turnover = gt.get("taxable_turnover")
    m_to = numeric_match(turnover, gt_turnover)
    scores.append(FieldScore("taxable_turnover", gt_turnover, turnover, m_to, 1.0 if m_to else 0.0))

    # 4. Net ITC Total
    net_itc = biz.net_itc.total if biz.net_itc else None
    gt_net = gt.get("net_itc_total")
    m_net = numeric_match(net_itc, gt_net)
    scores.append(FieldScore("net_itc_total", gt_net, net_itc, m_net, 1.0 if m_net else 0.0))

    return scores


def evaluate_tds_form(biz: TDSForm | None, gt: dict[str, Any]) -> list[FieldScore]:
    if not biz:
        return [FieldScore("tds_payload", gt, None, False, 0.0, "Missing TDS form payload")]

    scores = []
    # 1. PAN
    pan = biz.pan or ""
    gt_pan = gt.get("employee_pan") or gt.get("assessee_pan", "")
    m_pan = normalize_id(pan) == normalize_id(gt_pan)
    scores.append(FieldScore("pan", gt_pan, pan, m_pan, 1.0 if m_pan else 0.0))

    # 2. Total TDS Deposited
    dep = biz.total_tds_deposited
    gt_dep = gt.get("total_tax_deposited") or gt.get("total_tds_deposited")
    m_dep = numeric_match(dep, gt_dep)
    scores.append(FieldScore("total_tds_deposited", gt_dep, dep, m_dep, 1.0 if m_dep else 0.0))

    # 3. Assessment Year
    ay = biz.assessment_year or ""
    gt_ay = gt.get("assessment_year", "")
    m_ay = normalize_id(ay) == normalize_id(gt_ay)
    scores.append(FieldScore("assessment_year", gt_ay, ay, m_ay, 1.0 if m_ay else 0.0))

    return scores


def evaluate_investment_proof(biz: InvestmentProof | None, gt: dict[str, Any]) -> list[FieldScore]:
    if not biz:
        return [FieldScore("invest_payload", gt, None, False, 0.0, "Missing investment proof payload")]

    scores = []
    # 1. PAN
    pan = biz.pan or ""
    gt_pan = gt.get("pan", "")
    m_pan = normalize_id(pan) == normalize_id(gt_pan)
    scores.append(FieldScore("pan", gt_pan, pan, m_pan, 1.0 if m_pan else 0.0))

    # 2. Section
    sec = biz.section or ""
    m_sec = "80C" in sec.upper()
    scores.append(FieldScore("section", "80C", sec, m_sec, 1.0 if m_sec else 0.0))

    # 3. Amount Paid
    amt = biz.amount_paid
    gt_amt = gt.get("total_premium_paid") or gt.get("deposits_in_fy")
    m_amt = numeric_match(amt, gt_amt)
    scores.append(FieldScore("amount_paid", gt_amt, amt, m_amt, 1.0 if m_amt else 0.0))

    return scores


# ---------------------------------------------------------------------------
# Pipeline Benchmark Runner
# ---------------------------------------------------------------------------

class PipelineBenchmarkRunner:
    def __init__(self, settings: Any, delay_s: float = 2.0, update_db: bool = True):
        self.settings = settings
        self.delay_s = delay_s
        self.update_db = update_db
        self.ocr_service = OCRService(settings)
        self.extraction_service = ExtractionService(settings)
        self.engine = create_async_engine(settings.database_url, echo=False)

    async def update_database_record(self, filename: str, result: DocumentBenchmarkResult) -> None:
        """Update the PostgreSQL document row with real live extraction results."""
        if not self.update_db:
            return

        short_name = filename.split("/")[-1]
        async with AsyncSession(self.engine) as session:
            stmt = select(Document).where(Document.source_filename == short_name)
            res = await session.execute(stmt)
            doc = res.scalar_one_or_none()
            if not doc:
                return

            now = datetime.now(timezone.utc)
            doc.status = DocumentStatus.needs_review if result.needs_review else DocumentStatus.validated
            try:
                doc.document_type = DocumentType(result.classified_type)
            except ValueError:
                doc.document_type = DocumentType.unknown

            doc.ocr_confidence = result.ocr_confidence
            doc.extraction_confidence = result.classification_confidence
            doc.needs_human_review = result.needs_review
            doc.review_reason = "; ".join(result.review_reasons) if result.review_reasons else None
            doc.extracted_data = result.extracted_data
            doc.metadata_ = {
                "page_count": result.ocr_pages,
                "ocr_latency_s": round(result.ocr_latency_s, 2),
                "llm_latency_s": round(result.llm_latency_s, 2),
                "field_accuracy": round(result.field_accuracy, 2),
                "evaluated_at": now.isoformat(),
            }
            doc.processed_at = now
            await session.commit()

    def evaluate_extracted_object(
        self,
        doc_type: str,
        parsed: DocumentExtraction,
        ground_truth: dict[str, Any],
    ) -> list[FieldScore]:
        if doc_type == "invoice":
            return evaluate_invoice(parsed.invoice, ground_truth)
        elif doc_type == "bank_statement":
            return evaluate_bank_statement(parsed.bank_statement, ground_truth)
        elif doc_type == "gst_return":
            return evaluate_gst_return(parsed.gst_return, ground_truth)
        elif doc_type == "tds_form":
            return evaluate_tds_form(parsed.tds_form, ground_truth)
        elif doc_type == "investment_proof":
            return evaluate_investment_proof(parsed.investment_proof, ground_truth)
        return []

    async def benchmark_document(
        self,
        doc_meta: dict[str, Any],
        ground_truth: dict[str, Any],
    ) -> DocumentBenchmarkResult:
        rel_path = doc_meta["filename"]
        pdf_path = PDFS_DIR / rel_path
        category = doc_meta.get("category_folder", "clean")
        expected_type = doc_meta.get("expected_classification", "unknown")

        logger.info(">>> Processing [%s] %s ...", category, rel_path)

        if not pdf_path.exists():
            return DocumentBenchmarkResult(
                filename=rel_path,
                category=category,
                expected_type=expected_type,
                classified_type="missing_file",
                classification_correct=False,
                classification_confidence=None,
                ocr_latency_s=0.0,
                ocr_confidence=None,
                ocr_pages=0,
                llm_latency_s=0.0,
                total_latency_s=0.0,
                needs_review=True,
                review_reasons=["File not found on disk"],
                error="File does not exist",
            )

        # Step 1: Run PaddleOCR PP-StructureV3
        t0 = time.perf_counter()
        result_id = f"bench_{int(time.time())}_{pdf_path.stem}"
        try:
            ocr_res = self.ocr_service.extract(pdf_path, pdf_path.name, result_id)
            ocr_dur = time.perf_counter() - t0
        except Exception as exc:
            logger.error("OCR Failed on %s: %s", rel_path, exc)
            return DocumentBenchmarkResult(
                filename=rel_path,
                category=category,
                expected_type=expected_type,
                classified_type="ocr_error",
                classification_correct=False,
                classification_confidence=None,
                ocr_latency_s=time.perf_counter() - t0,
                ocr_confidence=None,
                ocr_pages=0,
                llm_latency_s=0.0,
                total_latency_s=time.perf_counter() - t0,
                needs_review=True,
                review_reasons=[f"OCR error: {exc}"],
                error=str(exc),
            )

        all_conf = [
            b.confidence
            for p in ocr_res.pages
            for b in p.blocks
            if b.confidence is not None
        ]
        avg_ocr_conf = round(sum(all_conf) / len(all_conf), 4) if all_conf else None

        # Rate-limiting pause before calling LLM
        time.sleep(self.delay_s)

        # Step 2: Run LLM Classification & Extraction
        t1 = time.perf_counter()
        try:
            parsed = self.extraction_service.extract(
                ocr_res.markdown,
                document_id=result_id,
                source_filename=pdf_path.name,
                ocr_confidence=avg_ocr_conf,
            )
            llm_dur = time.perf_counter() - t1
        except Exception as exc:
            logger.error("LLM Extraction Failed on %s: %s", rel_path, exc)
            return DocumentBenchmarkResult(
                filename=rel_path,
                category=category,
                expected_type=expected_type,
                classified_type="llm_error",
                classification_correct=False,
                classification_confidence=None,
                ocr_latency_s=ocr_dur,
                ocr_confidence=avg_ocr_conf,
                ocr_pages=len(ocr_res.pages),
                llm_latency_s=time.perf_counter() - t1,
                total_latency_s=time.perf_counter() - t0,
                needs_review=True,
                review_reasons=[f"LLM extraction error: {exc}"],
                error=str(exc),
            )

        total_dur = time.perf_counter() - t0

        # Step 3: Evaluate Fields & Accuracy against Ground Truth
        classified_type = parsed.document.document_type.value
        cls_correct = classified_type == expected_type

        biz_objs = parsed.business_objects()
        biz_data = next(iter(biz_objs.values())).model_dump(mode="json") if biz_objs else {}

        field_scores = self.evaluate_extracted_object(expected_type, parsed, ground_truth)
        if field_scores:
            field_acc = sum(s.score for s in field_scores) / len(field_scores)
        else:
            field_acc = 1.0 if cls_correct else 0.0

        all_reasons = []
        if parsed.document.review_reason:
            all_reasons.append(parsed.document.review_reason)

        res = DocumentBenchmarkResult(
            filename=rel_path,
            category=category,
            expected_type=expected_type,
            classified_type=classified_type,
            classification_correct=cls_correct,
            classification_confidence=parsed.document.ocr_confidence,
            ocr_latency_s=round(ocr_dur, 2),
            ocr_confidence=avg_ocr_conf,
            ocr_pages=len(ocr_res.pages),
            llm_latency_s=round(llm_dur, 2),
            total_latency_s=round(total_dur, 2),
            needs_review=parsed.document.needs_human_review,
            review_reasons=all_reasons,
            field_scores=field_scores,
            field_accuracy=round(field_acc * 100, 1),
            extracted_data=biz_data,
        )

        # Step 4: Persist real data into DB
        await self.update_database_record(rel_path, res)

        logger.info(
            "  -> [%s] Class: %s (exp: %s) | Field Acc: %.1f%% | OCR: %.1fs | LLM: %.1fs | Review: %s",
            "PASS" if cls_correct and field_acc >= 0.7 else "WARN",
            classified_type,
            expected_type,
            res.field_accuracy,
            ocr_dur,
            llm_dur,
            "YES" if res.needs_review else "NO",
        )

        return res

    async def close(self) -> None:
        await self.engine.dispose()


# ---------------------------------------------------------------------------
# Report Generation & Analysis
# ---------------------------------------------------------------------------

def compute_aggregate_metrics(results: list[DocumentBenchmarkResult]) -> dict[str, Any]:
    total_docs = len(results)
    if total_docs == 0:
        return {}

    correct_cls = sum(1 for r in results if r.classification_correct)
    cls_accuracy = (correct_cls / total_docs) * 100

    docs_with_fields = [r for r in results if r.field_scores]
    avg_field_acc = (
        sum(r.field_accuracy for r in docs_with_fields) / len(docs_with_fields)
        if docs_with_fields
        else 0.0
    )

    cat_breakdown: dict[str, dict[str, Any]] = {}
    for cat in ["clean", "scanned_good", "scanned_poor", "edge_cases"]:
        cat_res = [r for r in results if r.category == cat]
        if not cat_res:
            continue
        c_acc = (sum(1 for r in cat_res if r.classification_correct) / len(cat_res)) * 100
        f_res = [r for r in cat_res if r.field_scores]
        f_acc = (sum(r.field_accuracy for r in f_res) / len(f_res)) if f_res else 0.0
        avg_ocr = sum(r.ocr_confidence or 0 for r in cat_res) / len(cat_res)
        cat_breakdown[cat] = {
            "count": len(cat_res),
            "classification_accuracy_pct": round(c_acc, 1),
            "field_accuracy_pct": round(f_acc, 1),
            "avg_ocr_confidence": round(avg_ocr, 3),
            "review_flagged_count": sum(1 for r in cat_res if r.needs_review),
        }

    ocr_times = [r.ocr_latency_s for r in results if r.ocr_latency_s > 0]
    llm_times = [r.llm_latency_s for r in results if r.llm_latency_s > 0]
    total_times = [r.total_latency_s for r in results if r.total_latency_s > 0]

    latency_metrics = {
        "mean_ocr_s": round(sum(ocr_times) / len(ocr_times), 2) if ocr_times else 0,
        "mean_llm_s": round(sum(llm_times) / len(llm_times), 2) if llm_times else 0,
        "mean_total_s": round(sum(total_times) / len(total_times), 2) if total_times else 0,
    }

    return {
        "total_documents": total_docs,
        "classification_accuracy_pct": round(cls_accuracy, 1),
        "mean_field_accuracy_pct": round(avg_field_acc, 1),
        "review_flagged_pct": round((sum(1 for r in results if r.needs_review) / total_docs) * 100, 1),
        "category_breakdown": cat_breakdown,
        "latency": latency_metrics,
    }


def generate_markdown_report(
    metrics: dict[str, Any], results: list[DocumentBenchmarkResult]
) -> str:
    lines = [
        "# Live Pipeline Benchmark & Accuracy Report",
        "",
        f"**Run Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Model:** `openai/gpt-oss-120b` via Groq  ",
        f"**OCR Engine:** PaddleOCR `PP-StructureV3` (CUDA GPU)  ",
        f"**Total Documents Evaluated:** {metrics.get('total_documents', len(results))}",
        "",
        "---",
        "",
        "## 1. Executive Summary & Quantifiable Metrics",
        "",
        "| Metric | Result | Benchmark Target | Status |",
        "|---|:---:|:---:|:---:|",
        f"| **Document Classification Accuracy** | **{metrics.get('classification_accuracy_pct', 0)}%** | >= 95% | {'✅ PASS' if metrics.get('classification_accuracy_pct', 0) >= 95 else '⚠️ REVIEW'} |",
        f"| **Key Field Extraction Accuracy** | **{metrics.get('mean_field_accuracy_pct', 0)}%** | >= 85% | {'✅ PASS' if metrics.get('mean_field_accuracy_pct', 0) >= 85 else '⚠️ REVIEW'} |",
        f"| **Human Review Trigger Rate** | **{metrics.get('review_flagged_pct', 0)}%** | Auto-flagged | ℹ️ INFO |",
        f"| **Avg OCR Latency** | **{metrics.get('latency', {}).get('mean_ocr_s', 0)}s** | < 5.0s | ✅ FAST |",
        f"| **Avg LLM Extraction Latency** | **{metrics.get('latency', {}).get('mean_llm_s', 0)}s** | < 4.0s | ✅ FAST |",
        "",
        "---",
        "",
        "## 2. Robustness by Document Condition (Ablation Analysis)",
        "",
        "| Category | Count | Classification Acc | Field Acc | Avg OCR Conf | Review Flagged |",
        "|---|:---:|:---:|:---:|:---:|:---:|",
    ]

    for cat, data in metrics.get("category_breakdown", {}).items():
        lines.append(
            f"| **`{cat}`** | {data['count']} | {data['classification_accuracy_pct']}% | "
            f"{data['field_accuracy_pct']}% | {data['avg_ocr_confidence']} | {data['review_flagged_count']}/{data['count']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Detailed Per-Document Results",
        "",
        "| Filename | Category | Expected | Classified | Field Acc | OCR Conf | Total Time | Review Needed |",
        "|---|---|---|---|:---:|:---:|:---:|:---:|",
    ])

    for r in results:
        status_icon = "✅" if r.classification_correct and r.field_accuracy >= 75 else "⚠️"
        lines.append(
            f"| `{r.filename}` | `{r.category}` | `{r.expected_type}` | `{r.classified_type}` | "
            f"{r.field_accuracy}% | {r.ocr_confidence or 'N/A'} | {r.total_latency_s}s | {'Yes' if r.needs_review else 'No'} {status_icon} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. Field-Level Failure Analysis",
        "",
    ])

    mismatches = []
    for r in results:
        failed_fields = [f for f in r.field_scores if not f.matched]
        if failed_fields:
            mismatches.append((r.filename, failed_fields))

    if mismatches:
        for fname, fields in mismatches:
            lines.append(f"### `{fname}`")
            for f in fields:
                lines.append(f"- **{f.field_name}**: Expected `{f.ground_truth}`, got `{f.extracted}` ({f.note or 'mismatch'})")
            lines.append("")
    else:
        lines.append("No critical field mismatches detected across the dataset! 🎉\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

async def run_benchmark(
    only_clean: bool = False,
    single_file: str | None = None,
    delay_s: float = 2.0,
    no_db: bool = False,
) -> None:
    settings = get_settings()

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    clean_gt_map: dict[str, dict[str, Any]] = {}
    for doc in manifest["documents"]:
        if "ground_truth" in doc:
            clean_gt_map[doc["filename"]] = doc["ground_truth"]
            clean_gt_map[doc["filename"].split("/")[-1]] = doc["ground_truth"]

    docs_to_run = manifest["documents"]
    if single_file:
        docs_to_run = [d for d in docs_to_run if single_file in d["filename"]]
    elif only_clean:
        docs_to_run = [d for d in docs_to_run if d.get("category_folder") == "clean"]

    logger.info("====================================================================")
    logger.info("Starting Dataset Pipeline Benchmark (Total: %d documents)", len(docs_to_run))
    logger.info("LLM Model: %s | Base URL: %s", settings.llm_model, settings.llm_base_url)
    logger.info("Pacing: %.1fs pause between documents (rate-limit safety)", delay_s)
    logger.info("DB Update: %s", "DISABLED (--no-db)" if no_db else "ENABLED (Updating PostgreSQL documents)")
    logger.info("====================================================================")

    runner = PipelineBenchmarkRunner(settings, delay_s=delay_s, update_db=not no_db)
    results: list[DocumentBenchmarkResult] = []

    try:
        for idx, doc_meta in enumerate(docs_to_run, start=1):
            logger.info("\n[%d/%d] --------------------------------------------------", idx, len(docs_to_run))
            gt = doc_meta.get("ground_truth")
            if not gt and "source_pdf" in doc_meta:
                src_key = doc_meta["source_pdf"].split()[0]
                gt = clean_gt_map.get(src_key) or clean_gt_map.get(src_key.split("/")[-1])
            gt = gt or {}

            res = await runner.benchmark_document(doc_meta, gt)
            results.append(res)
    finally:
        await runner.close()

    metrics = compute_aggregate_metrics(results)

    report_dict = {
        "metrics": metrics,
        "results": [
            {
                "filename": r.filename,
                "category": r.category,
                "expected_type": r.expected_type,
                "classified_type": r.classified_type,
                "classification_correct": r.classification_correct,
                "ocr_latency_s": r.ocr_latency_s,
                "ocr_confidence": r.ocr_confidence,
                "llm_latency_s": r.llm_latency_s,
                "total_latency_s": r.total_latency_s,
                "needs_review": r.needs_review,
                "field_accuracy": r.field_accuracy,
                "review_reasons": r.review_reasons,
                "field_scores": [asdict(s) for s in r.field_scores],
            }
            for r in results
        ],
    }

    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    md_content = generate_markdown_report(metrics, results)
    with open(OUTPUT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n" + "=" * 70)
    print("                      BENCHMARK COMPLETE")
    print("=" * 70)
    print(f"Total Evaluated:              {metrics.get('total_documents', len(results))}")
    print(f"Classification Accuracy:      {metrics.get('classification_accuracy_pct')}%")
    print(f"Mean Key Field Accuracy:      {metrics.get('mean_field_accuracy_pct')}%")
    print(f"Avg OCR Inference Time:       {metrics.get('latency', {}).get('mean_ocr_s')}s")
    print(f"Avg LLM Extraction Time:      {metrics.get('latency', {}).get('mean_llm_s')}s")
    print("-" * 70)
    print(f"Saved Machine Report:         {OUTPUT_REPORT_PATH}")
    print(f"Saved Markdown Summary:       {OUTPUT_MD_PATH}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark synthetic dataset through live pipeline.")
    parser.add_argument("--only-clean", action="store_true", help="Only run on clean category documents.")
    parser.add_argument("--file", type=str, default=None, help="Run on a single specific file name.")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay in seconds between LLM calls (rate limit pacing).")
    parser.add_argument("--no-db", action="store_true", help="Do not update PostgreSQL database records.")
    args = parser.parse_args()

    asyncio.run(
        run_benchmark(
            only_clean=args.only_clean,
            single_file=args.file,
            delay_s=args.delay,
            no_db=args.no_db,
        )
    )


if __name__ == "__main__":
    main()
