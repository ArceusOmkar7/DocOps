"""System health & configuration endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import Settings, get_settings
from ....services.ocr import OCRService
from ...deps import get_db, get_ocr_service

router = APIRouter(tags=["system"])


@router.get("/health", summary="Service health")
async def health(
    settings: Settings = Depends(get_settings),
    ocr: OCRService = Depends(get_ocr_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "database_connected": db_ok,
        "ocr_loaded": ocr.is_loaded,
        "ocr_pipeline": settings.ocr_pipeline,
        "ocr_device": settings.ocr_device,
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        "llm_json_mode": settings.llm_use_json_mode,
        "llm_has_api_key": bool(settings.llm_api_key),
    }
