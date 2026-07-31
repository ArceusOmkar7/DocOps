"""End-to-end test exercising the real OCR pipeline (models are cached)."""

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.main import app


def _make_png_bytes() -> bytes:
    img = Image.new("RGB", (400, 120), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Invoice No 42", fill="black")
    draw.text((10, 60), "Amount: $99.00", fill="black")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_extract_image_end_to_end():
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/ocr/extract",
            files={"file": ("invoice.png", _make_png_bytes(), "image/png")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["file_type"] == "image"
        assert data["page_count"] == 1
        assert len(data["pages"]) == 1
        assert data["source_url"].endswith("/source")
        assert data["markdown_url"].endswith("/markdown")
        assert data["full_text"]


def test_extract_rejects_unsupported_extension():
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/ocr/extract",
            files={"file": ("notes.txt", b"hello", "text/plain")},
        )
        assert res.status_code == 415
