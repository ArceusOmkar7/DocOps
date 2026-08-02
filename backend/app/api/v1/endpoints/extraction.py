"""Business extraction endpoints (markdown -> Document + Invoice)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ....core.config import Settings, get_settings
from ....core.storage import load_json, result_dir, save_json
from ....schemas.extraction import DocumentExtraction
from ....services.extraction import ExtractionError, ExtractionService
from ...deps import get_extraction_service

router = APIRouter(tags=["extraction"])


def _average_confidence(result: dict) -> float | None:
    confidences = [
        block["confidence"]
        for page in result.get("pages", [])
        for block in page.get("blocks", [])
        if block.get("confidence") is not None
    ]
    if not confidences:
        return None
    return round(sum(confidences) / len(confidences), 4)


@router.post(
    "/ocr/results/{result_id}/parse",
    response_model=DocumentExtraction,
    summary="Parse stored OCR markdown into a business object",
)
def parse(
    result_id: str,
    settings: Settings = Depends(get_settings),
    extraction: ExtractionService = Depends(get_extraction_service),
) -> DocumentExtraction:
    path = result_dir(settings, result_id) / "result.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    result = load_json(path)

    try:
        parsed = extraction.extract(
            result["markdown"],
            document_id=result_id,
            source_filename=result["filename"],
            ocr_confidence=_average_confidence(result),
        )
    except ExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    out_dir = result_dir(settings, result_id)
    save_json(out_dir / "document.json", parsed.document.model_dump(mode="json"))
    if parsed.invoice is not None:
        save_json(out_dir / "invoice.json", parsed.invoice.model_dump(mode="json"))
    return parsed
