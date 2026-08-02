"""Shared FastAPI dependencies."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..db.engine import async_session_factory
from ..services.extraction import ExtractionService
from ..services.ocr import OCRService


@lru_cache
def get_ocr_service() -> OCRService:
    return OCRService(get_settings())


@lru_cache
def get_extraction_service() -> ExtractionService:
    return ExtractionService(get_settings())


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session per request, auto-closing on completion."""
    async with async_session_factory() as session:
        yield session
