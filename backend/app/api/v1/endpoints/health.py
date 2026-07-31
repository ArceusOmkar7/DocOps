"""System health endpoint."""

from fastapi import APIRouter, Depends

from ....core.config import Settings, get_settings
from ....services.ocr import OCRService
from ...deps import get_ocr_service

router = APIRouter(tags=["system"])


@router.get("/health", summary="Service health")
def health(
    settings: Settings = Depends(get_settings),
    ocr: OCRService = Depends(get_ocr_service),
) -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "ocr_loaded": ocr.is_loaded,
        "ocr_device": settings.ocr_device,
    }
