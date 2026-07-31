"""Unit tests for OCR parsing helpers (no engine inference required)."""

from app.schemas.ocr import OCRBlock, OCRLayoutBlock
from app.services.ocr import (
    blocks_from_raw,
    group_into_rows,
    html_table_to_text,
    layout_blocks_from_raw,
    page_from_raw,
    plain_text_from_layout,
)


def _block(x0, y0, x1, y1, text="t") -> OCRBlock:
    return OCRBlock(
        text=text,
        confidence=0.9,
        polygon=[[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
        bbox=[x0, y0, x1, y1],
    )


def _raw(
    rec_texts,
    rec_scores=None,
    rec_polys=None,
    parsing=None,
    width=100,
    height=200,
) -> dict:
    scores = rec_scores or [0.9] * len(rec_texts)
    polys = rec_polys or [
        [[10, i * 10], [60, i * 10], [60, i * 10 + 10], [10, i * 10 + 10]]
        for i in range(len(rec_texts))
    ]
    return {
        "width": width,
        "height": height,
        "overall_ocr_res": {
            "rec_texts": rec_texts,
            "rec_scores": scores,
            "rec_polys": polys,
        },
        "parsing_res_list": parsing or [],
    }


def test_group_into_rows_joins_vertically_aligned_blocks():
    blocks = [
        _block(0, 0, 30, 10, "No."),
        _block(60, 0, 90, 10, "Qty"),
        _block(0, 40, 50, 50, "second row"),
    ]
    rows = group_into_rows(blocks)
    assert len(rows) == 2
    assert [b.text for b in rows[0]] == ["No.", "Qty"]


def test_blocks_from_raw_skips_empty():
    raw = _raw(
        ["hello", "", "world"],
        rec_scores=[0.9, 0.8, 0.7],
        rec_polys=[
            [[0, 0], [10, 0], [10, 10], [0, 10]],
            [],
            [[0, 0], [5, 0], [5, 5], [0, 5]],
        ],
    )
    blocks = blocks_from_raw(raw)
    assert [b.text for b in blocks] == ["hello", "world"]
    assert blocks[0].bbox == [0.0, 0.0, 10.0, 10.0]
    assert all(b.label == "text" for b in blocks)


def test_blocks_from_raw_follows_layout_reading_order():
    parsing = [
        {
            "block_id": 0,
            "block_order": 1,
            "block_label": "text",
            "block_content": "left",
            "block_bbox": [0, 0, 100, 20],
        },
        {
            "block_id": 1,
            "block_order": 2,
            "block_label": "table",
            "block_content": "<table></table>",
            "block_bbox": [0, 50, 100, 120],
        },
    ]
    # listed in reverse reading order to prove ordering comes from layout
    raw = _raw(
        ["right-table", "left-top"],
        rec_scores=[0.7, 0.9],
        rec_polys=[
            [[10, 60], [60, 60], [60, 70], [10, 70]],
            [[10, 5], [60, 5], [60, 15], [10, 15]],
        ],
        parsing=parsing,
    )
    blocks = blocks_from_raw(raw)
    assert [b.text for b in blocks] == ["left-top", "right-table"]
    assert [b.label for b in blocks] == ["text", "table"]


def test_layout_blocks_from_raw():
    parsing = [
        {
            "block_id": 0,
            "block_order": 1,
            "block_label": "paragraph_title",
            "block_content": "Invoice",
            "block_bbox": [10, 10, 200, 40],
        },
        {
            "block_id": 1,
            "block_order": None,
            "block_label": "table",
            "block_content": "<table><tr><td>a</td></tr></table>",
            "block_bbox": [10, 50, 200, 100],
        },
    ]
    blocks = layout_blocks_from_raw(_raw([], parsing=parsing))
    assert [b.label for b in blocks] == ["paragraph_title", "table"]
    assert blocks[0].order == 1
    assert blocks[1].order is None
    assert blocks[1].id == 1
    assert blocks[0].bbox == [10, 10, 200, 40]


def test_html_table_to_text():
    html = (
        "<html><body><table><tbody>"
        "<tr><td>No.</td><td>Qty</td><td>Total</td></tr>"
        "<tr><td>1.</td><td>3</td><td>209,00</td></tr>"
        "</tbody></table></body></html>"
    )
    text = html_table_to_text(html)
    assert text.splitlines() == [
        "No.  Qty  Total",
        "1.  3  209,00",
    ]


def test_plain_text_from_layout_includes_plain_blocks_and_tables():
    parsing = [
        {
            "block_id": 0,
            "block_order": 1,
            "block_label": "text",
            "block_content": "Seller: ACME",
            "block_bbox": [0, 0, 100, 20],
        },
        {
            "block_id": 1,
            "block_order": None,
            "block_label": "table",
            "block_content": "<table><tr><td>a</td><td>b</td></tr></table>",
            "block_bbox": [0, 30, 100, 60],
        },
        {
            "block_id": 2,
            "block_order": 2,
            "block_label": "image",
            "block_content": "",
            "block_bbox": [0, 70, 100, 90],
        },
    ]
    text = plain_text_from_layout(_raw([], parsing=parsing))
    assert text == "Seller: ACME\n\na  b"


def test_page_from_raw_builds_text_and_markdown():
    parsing = [
        {
            "block_id": 0,
            "block_order": 1,
            "block_label": "paragraph_title",
            "block_content": "Invoice",
            "block_bbox": [10, 10, 200, 40],
        },
        {
            "block_id": 1,
            "block_order": 2,
            "block_label": "text",
            "block_content": "Total",
            "block_bbox": [10, 50, 200, 70],
        },
    ]
    page = page_from_raw(_raw(["Invoice", "Total"], parsing=parsing), 0, markdown="## Invoice\n\nTotal")
    assert page.page_index == 0
    assert page.width == 100
    assert page.height == 200
    assert page.text == "Invoice\n\nTotal"
    assert page.markdown == "## Invoice\n\nTotal"
    assert len(page.layout_blocks) == 2


def test_page_from_raw_falls_back_to_blocks_when_no_layout():
    raw = _raw(["Invoice", "Total"], parsing=[])
    page = page_from_raw(raw, 0)
    assert page.text == "Invoice\n\nTotal"
    assert page.markdown == "Invoice\n\nTotal"
    assert page.layout_blocks == []


def test_page_from_raw_joins_same_row_blocks_into_one_line():
    parsing = [
        {
            "block_id": 0,
            "block_order": 1,
            "block_label": "text",
            "block_content": "No. Qty Net price",
            "block_bbox": [0, 0, 200, 10],
        }
    ]
    raw = _raw(
        ["Qty", "Net price", "No."],
        rec_scores=[0.9, 0.8, 0.7],
        rec_polys=[
            [[100, 0], [130, 0], [130, 10], [100, 10]],
            [[60, 0], [90, 0], [90, 10], [60, 10]],
            [[0, 0], [30, 0], [30, 10], [0, 10]],
        ],
        parsing=parsing,
    )
    page = page_from_raw(raw, 0)
    assert page.text == "No. Qty Net price"
    assert page.markdown == "No. Qty Net price"
