"""Pydantic schemas for OCR API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class OCRBlock(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    polygon: list[list[float]]
    bbox: list[float] = Field(min_length=4, max_length=4)


class OCRPage(BaseModel):
    page_index: int
    blocks: list[OCRBlock]
    text: str
    markdown: str


class OCREngineInfo(BaseModel):
    lang: str
    detection_model: str
    recognition_model: str
    device: str


class OCRResult(BaseModel):
    result_id: str
    filename: str
    file_type: Literal["image", "pdf"]
    page_count: int
    pages: list[OCRPage]
    full_text: str
    markdown: str
    source_url: str | None = None
    markdown_url: str | None = None
    engine: OCREngineInfo
    processing_time_ms: int
    created_at: datetime
