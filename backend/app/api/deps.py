"""Shared FastAPI dependencies."""

from functools import lru_cache

from ..core.config import get_settings
from ..services.ocr import OCRService


@lru_cache
def get_ocr_service() -> OCRService:
    return OCRService(get_settings())
