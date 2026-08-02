"""Shared FastAPI dependencies."""

from functools import lru_cache

from ..core.config import get_settings
from ..services.extraction import ExtractionService
from ..services.ocr import OCRService


@lru_cache
def get_ocr_service() -> OCRService:
    return OCRService(get_settings())


@lru_cache
def get_extraction_service() -> ExtractionService:
    return ExtractionService(get_settings())
