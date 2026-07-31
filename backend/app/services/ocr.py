"""OCR service: wraps the PaddleOCR engine and exposes structured extraction."""

from __future__ import annotations

import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from paddleocr import PaddleOCR

from ..core.config import Settings
from ..schemas.ocr import OCRBlock, OCREngineInfo, OCRPage, OCRResult


class OCRError(Exception):
    """Raised when OCR extraction fails."""


def sort_blocks_reading_order(blocks: list[OCRBlock]) -> list[OCRBlock]:
    """Sort OCR blocks top-to-bottom, then left-to-right per row."""
    if not blocks:
        return blocks
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

    ordered: list[OCRBlock] = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda b: b.bbox[0]))
    return ordered


def blocks_from_raw(raw: Any) -> list[OCRBlock]:
    """Convert one PaddleOCR page result into ordered OCRBlock models."""
    texts = raw.get("rec_texts") or []
    scores = raw.get("rec_scores") or []
    polys = raw.get("rec_polys") or []

    blocks: list[OCRBlock] = []
    for text, score, poly in zip(texts, scores, polys):
        if not text or poly is None or len(poly) == 0:
            continue
        polygon = [[float(x), float(y)] for x, y in poly]
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        blocks.append(
            OCRBlock(
                text=text,
                confidence=float(score),
                polygon=polygon,
                bbox=[min(xs), min(ys), max(xs), max(ys)],
            )
        )
    return sort_blocks_reading_order(blocks)


def page_from_raw(raw: Any, page_index: int) -> OCRPage:
    """Build an OCRPage from a raw PaddleOCR page result."""
    blocks = blocks_from_raw(raw)
    lines = [b.text for b in blocks]
    return OCRPage(
        page_index=page_index,
        blocks=blocks,
        text="\n".join(lines),
        markdown="\n\n".join(lines),
    )


class OCRService:
    """Lazily-initialized, inference-safe wrapper around the PaddleOCR engine."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._engine: PaddleOCR | None = None
        self._init_lock = Lock()
        self._infer_lock = Lock()

    @property
    def is_loaded(self) -> bool:
        return self._engine is not None

    @property
    def engine_info(self) -> OCREngineInfo:
        s = self._settings
        return OCREngineInfo(
            lang=s.ocr_lang,
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

        pages = [page_from_raw(raw, i) for i, raw in enumerate(raw_results)]
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

    def _get_engine(self) -> PaddleOCR:
        if self._engine is None:
            with self._init_lock:
                if self._engine is None:
                    self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> PaddleOCR:
        s = self._settings
        kwargs: dict[str, Any] = {
            "device": s.ocr_device,
            "enable_mkldnn": s.ocr_enable_mkldnn,
            "cpu_threads": s.ocr_cpu_threads,
            "use_doc_orientation_classify": s.ocr_use_doc_orientation_classify,
            "use_doc_unwarping": s.ocr_use_doc_unwarping,
            "use_textline_orientation": s.ocr_use_textline_orientation,
        }
        if s.ocr_det_model:
            kwargs["text_detection_model_name"] = s.ocr_det_model
        if s.ocr_rec_model:
            kwargs["text_recognition_model_name"] = s.ocr_rec_model
        if not (s.ocr_det_model or s.ocr_rec_model):
            kwargs["lang"] = s.ocr_lang
        return PaddleOCR(**kwargs)

    def close(self) -> None:
        with self._init_lock:
            if self._engine is not None:
                self._engine.close()
                self._engine = None
