"""OCR service: wraps the PP-StructureV3 pipeline and exposes structured extraction."""

from __future__ import annotations

import re
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from paddleocr import PPStructureV3

from ..core.config import Settings
from ..schemas.ocr import (
    OCRBlock,
    OCREngineInfo,
    OCRLayoutBlock,
    OCRPage,
    OCRResult,
)

_IMAGE_LABELS = {"image", "header_image", "footer_image"}


class OCRError(Exception):
    """Raised when OCR extraction fails."""


def group_into_rows(blocks: list[OCRBlock]) -> list[list[OCRBlock]]:
    """Group blocks into visual rows by vertical alignment."""
    if not blocks:
        return []
    heights = [b.bbox[3] - b.bbox[1] for b in blocks]
    tolerance = max(statistics.median(heights) * 0.5, 1.0)

    rows: list[list[OCRBlock]] = []
    for block in blocks:
        center_y = (block.bbox[1] + block.bbox[3]) / 2
        for row in rows:
            row_center_y = sum((b.bbox[1] + b.bbox[3]) / 2 for b in row) / len(row)
            if abs(center_y - row_center_y) <= tolerance:
                row.append(block)
                break
        else:
            rows.append([block])
    return rows


def line_from_row(row: list[OCRBlock]) -> str:
    """Render one visual row as a single line, left-to-right."""
    return " ".join(b.text for b in sorted(row, key=lambda b: b.bbox[0]))


def _match_layout(
    cx: float, cy: float, layout_bboxes: list[list[float]], layout_labels: list[str]
) -> tuple[int, str]:
    """Return (layout index, label) of the layout region containing (cx, cy)."""
    for idx, bbox in enumerate(layout_bboxes):
        if bbox and len(bbox) == 4:
            x1, y1, x2, y2 = bbox
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return idx, layout_labels[idx] if idx < len(layout_labels) else "text"
    return len(layout_bboxes), "text"


def blocks_from_raw(raw: dict) -> list[OCRBlock]:
    """Convert one PP-StructureV3 page result into labeled OCRBlock models.

    `raw` is the page's JSON dict (``res.json["res"]``). Blocks are ordered by
    the layout pipeline's reading order (parsing_res_list), then top-to-bottom
    and left-to-right within a layout region.
    """
    overall = raw.get("overall_ocr_res") or {}
    texts = overall.get("rec_texts") or []
    scores = overall.get("rec_scores") or []
    polys = overall.get("rec_polys") or []

    layout_blocks = raw.get("parsing_res_list") or []
    layout_bboxes = [b.get("block_bbox") for b in layout_blocks]
    layout_labels = [b.get("block_label", "text") for b in layout_blocks]

    candidates: list[tuple[int, OCRBlock]] = []
    for text, score, poly in zip(texts, scores, polys):
        if not text or poly is None or len(poly) == 0:
            continue
        polygon = [[float(x), float(y)] for x, y in poly]
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        layout_idx, label = _match_layout(cx, cy, layout_bboxes, layout_labels)
        candidates.append(
            (
                layout_idx,
                OCRBlock(
                    text=text,
                    confidence=float(score),
                    polygon=polygon,
                    bbox=[min(xs), min(ys), max(xs), max(ys)],
                    label=label,
                ),
            )
        )

    groups: dict[int, list[OCRBlock]] = {}
    for layout_idx, block in candidates:
        groups.setdefault(layout_idx, []).append(block)

    ordered: list[OCRBlock] = []
    for layout_idx in sorted(groups):
        rows = group_into_rows(groups[layout_idx])
        for row in sorted(rows, key=lambda r: min(b.bbox[1] for b in r)):
            ordered.extend(sorted(row, key=lambda b: b.bbox[0]))
    return ordered


def layout_blocks_from_raw(raw: dict) -> list[OCRLayoutBlock]:
    """Convert the parsing_res_list into semantic layout blocks (reading order)."""
    result: list[OCRLayoutBlock] = []
    for idx, block in enumerate(raw.get("parsing_res_list") or []):
        result.append(
            OCRLayoutBlock(
                id=block.get("block_id", idx),
                order=block.get("block_order"),
                label=block.get("block_label", "text"),
                text=block.get("block_content", "") or "",
                bbox=block.get("block_bbox", [0, 0, 0, 0]),
            )
        )
    return result


def html_table_to_text(html: str) -> str:
    """Render an HTML table as plain text rows (cells joined with two spaces)."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, flags=re.IGNORECASE | re.DOTALL)
    lines: list[str] = []
    for row in rows:
        cells = re.findall(
            r"<t[hd][^>]*>(.*?)</t[hd]>", row, flags=re.IGNORECASE | re.DOTALL
        )
        if not cells:
            continue
        cleaned = []
        for cell in cells:
            text = re.sub(r"<[^>]+>", "", cell)
            cleaned.append(text.replace("&nbsp;", " ").strip())
        lines.append("  ".join(cleaned))
    return "\n".join(lines)


def plain_text_from_layout(raw: dict) -> str:
    """Build plain text from the layout blocks, in reading order."""
    lines: list[str] = []
    for block in raw.get("parsing_res_list") or []:
        label = block.get("block_label", "text")
        content = (block.get("block_content") or "").strip()
        if not content or label in _IMAGE_LABELS:
            continue
        if label == "table":
            lines.append(html_table_to_text(content))
        else:
            lines.append(content)
    return "\n\n".join(lines)


def page_from_raw(raw: dict, page_index: int, markdown: str = "") -> OCRPage:
    """Build an OCRPage from a PP-StructureV3 page result dict."""
    blocks = blocks_from_raw(raw)
    layout_blocks = layout_blocks_from_raw(raw)

    text = plain_text_from_layout(raw)
    if not text and blocks:
        text = "\n\n".join(line_from_row(row) for row in group_into_rows(blocks))
    markdown = markdown.strip() or text

    return OCRPage(
        page_index=page_index,
        width=raw.get("width"),
        height=raw.get("height"),
        blocks=blocks,
        layout_blocks=layout_blocks,
        text=text,
        markdown=markdown,
    )


class OCRService:
    """Lazily-initialized, inference-safe wrapper around the PP-StructureV3 pipeline."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._engine: PPStructureV3 | None = None
        self._init_lock = Lock()
        self._infer_lock = Lock()

    @property
    def is_loaded(self) -> bool:
        return self._engine is not None

    @property
    def engine_info(self) -> OCREngineInfo:
        s = self._settings
        return OCREngineInfo(
            pipeline=s.ocr_pipeline,
            lang=s.ocr_lang,
            layout_model=s.ocr_layout_model,
            detection_model=s.ocr_det_model,
            recognition_model=s.ocr_rec_model,
            device=s.ocr_device,
        )

    def extract(self, input_path: Path, filename: str, result_id: str) -> OCRResult:
        started = time.perf_counter()
        try:
            raw_results = self._predict(input_path)
        except OCRError:
            raise
        except Exception as exc:
            raise OCRError(f"OCR inference failed: {exc}") from exc

        pages: list[OCRPage] = []
        for index, res in enumerate(raw_results):
            raw_json = res.json.get("res", {})
            markdown = (res.markdown or {}).get("markdown_texts", "")
            pages.append(page_from_raw(raw_json, index, markdown=markdown))

        return OCRResult(
            result_id=result_id,
            filename=filename,
            file_type="pdf" if input_path.suffix.lower() == ".pdf" else "image",
            page_count=len(pages),
            pages=pages,
            full_text="\n\n".join(page.text for page in pages),
            markdown="\n\n".join(page.markdown for page in pages),
            engine=self.engine_info,
            processing_time_ms=int((time.perf_counter() - started) * 1000),
            created_at=datetime.now(timezone.utc),
        )

    def _predict(self, input_path: Path) -> list[Any]:
        engine = self._get_engine()
        # The pipeline is not safe for concurrent predict calls.
        with self._infer_lock:
            return engine.predict(str(input_path))

    def _get_engine(self) -> PPStructureV3:
        if self._engine is None:
            with self._init_lock:
                if self._engine is None:
                    self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> PPStructureV3:
        s = self._settings
        kwargs: dict[str, Any] = {
            "device": s.ocr_device,
            "enable_mkldnn": s.ocr_enable_mkldnn,
            "cpu_threads": s.ocr_cpu_threads,
            "use_doc_orientation_classify": s.ocr_use_doc_orientation_classify,
            "use_doc_unwarping": s.ocr_use_doc_unwarping,
            "use_textline_orientation": s.ocr_use_textline_orientation,
            "use_table_recognition": s.ocr_use_table_recognition,
            "use_formula_recognition": s.ocr_use_formula_recognition,
            "use_chart_recognition": s.ocr_use_chart_recognition,
            "use_seal_recognition": s.ocr_use_seal_recognition,
            "use_region_detection": s.ocr_use_region_detection,
        }
        if s.ocr_layout_model:
            kwargs["layout_detection_model_name"] = s.ocr_layout_model
        if s.ocr_det_model:
            kwargs["text_detection_model_name"] = s.ocr_det_model
        if s.ocr_rec_model:
            kwargs["text_recognition_model_name"] = s.ocr_rec_model
        if not (s.ocr_det_model or s.ocr_rec_model):
            kwargs["lang"] = s.ocr_lang
        return PPStructureV3(**kwargs)

    def close(self) -> None:
        with self._init_lock:
            if self._engine is not None:
                self._engine.close()
                self._engine = None
