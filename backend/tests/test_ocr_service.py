"""Unit tests for OCR parsing helpers (no engine inference required)."""

from app.schemas.ocr import OCRBlock
from app.services.ocr import (
    blocks_from_raw,
    page_from_raw,
    sort_blocks_reading_order,
)


def _block(x0, y0, x1, y1, text="t") -> OCRBlock:
    return OCRBlock(
        text=text,
        confidence=0.9,
        polygon=[[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
        bbox=[x0, y0, x1, y1],
    )


def test_sort_blocks_reading_order():
    blocks = [
        _block(200, 10, 250, 30, "right-top"),
        _block(10, 10, 60, 30, "left-top"),
        _block(10, 80, 60, 100, "second"),
        _block(10, 150, 60, 170, "third"),
    ]
    ordered = sort_blocks_reading_order(blocks)
    assert [b.text for b in ordered] == ["left-top", "right-top", "second", "third"]


def test_sort_blocks_reading_order_empty():
    assert sort_blocks_reading_order([]) == []


def test_blocks_from_raw_skips_empty():
    raw = {
        "rec_texts": ["hello", "", "world"],
        "rec_scores": [0.9, 0.8, 0.7],
        "rec_polys": [
            [[0, 0], [10, 0], [10, 10], [0, 10]],
            [],
            [[0, 0], [5, 0], [5, 5], [0, 5]],
        ],
    }
    blocks = blocks_from_raw(raw)
    assert [b.text for b in blocks] == ["hello", "world"]
    assert blocks[0].bbox == [0.0, 0.0, 10.0, 10.0]


def test_page_from_raw_builds_text_and_markdown():
    raw = {
        "rec_texts": ["Invoice", "Total"],
        "rec_scores": [0.9, 0.8],
        "rec_polys": [
            [[0, 0], [50, 0], [50, 10], [0, 10]],
            [[0, 20], [50, 20], [50, 30], [0, 30]],
        ],
    }
    page = page_from_raw(raw, 0)
    assert page.page_index == 0
    assert page.text == "Invoice\nTotal"
    assert page.markdown == "Invoice\n\nTotal"
