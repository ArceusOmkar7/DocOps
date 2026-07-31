"""OCR extraction endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ....core.config import Settings, get_settings
from ....core.storage import (
    UploadTooLarge,
    load_json,
    new_result_id,
    result_dir,
    save_json,
    save_text,
    save_upload,
)
from ....schemas.ocr import OCRResult
from ....services.ocr import OCRError, OCRService
from ...deps import get_ocr_service

router = APIRouter(prefix="/ocr", tags=["ocr"])


def _safe_filename(name: str) -> str:
    return Path(name or "upload").name


def _validate_extension(filename: str, settings: Settings) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type '{ext or '(none)'}'. "
                f"Allowed: {sorted(settings.allowed_extensions)}"
            ),
        )
    return ext


@router.post(
    "/extract",
    response_model=OCRResult,
    summary="Extract text from an uploaded image or PDF",
)
def extract(
    file: UploadFile = File(..., description="Image or PDF to run OCR on"),
    settings: Settings = Depends(get_settings),
    ocr: OCRService = Depends(get_ocr_service),
) -> OCRResult:
    filename = _safe_filename(file.filename)
    _validate_extension(filename, settings)

    result_id = new_result_id()
    try:
        src_path = save_upload(settings, result_id, filename, file.file)
    except UploadTooLarge as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    try:
        result = ocr.extract(src_path, filename, result_id)
    except OCRError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    result.source_url = f"{settings.api_v1_prefix}/ocr/results/{result_id}/source"
    result.markdown_url = f"{settings.api_v1_prefix}/ocr/results/{result_id}/markdown"

    out_dir = result_dir(settings, result_id)
    save_json(out_dir / "result.json", result.model_dump(mode="json"))
    save_text(out_dir / "result.md", result.markdown)
    return result


@router.get(
    "/results/{result_id}",
    response_model=OCRResult,
    summary="Fetch a stored OCR result",
)
def get_result(
    result_id: str, settings: Settings = Depends(get_settings)
) -> dict:
    path = result_dir(settings, result_id) / "result.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    return load_json(path)


@router.get(
    "/results/{result_id}/markdown",
    summary="Download the OCR result as markdown",
)
def get_markdown(
    result_id: str, settings: Settings = Depends(get_settings)
) -> FileResponse:
    path = result_dir(settings, result_id) / "result.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    return FileResponse(
        path, media_type="text/markdown; charset=utf-8", filename=f"{result_id}.md"
    )


@router.get(
    "/results/{result_id}/source",
    summary="Download the original uploaded file",
)
def get_source(
    result_id: str, settings: Settings = Depends(get_settings)
) -> FileResponse:
    up_dir = settings.uploads_dir / result_id
    if not up_dir.exists():
        raise HTTPException(status_code=404, detail="Source not found")
    files = [p for p in up_dir.iterdir() if p.is_file()]
    if not files:
        raise HTTPException(status_code=404, detail="Source not found")
    return FileResponse(files[0])
