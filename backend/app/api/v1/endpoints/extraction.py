"""Business extraction endpoints (markdown -> Document + Invoice)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import Settings, get_settings
from ....core.storage import load_json, result_dir, save_json
from ....schemas.extraction import DocumentExtraction
from ....services.db_helpers import save_extracted_document_to_db
from ....services.extraction import ExtractionError, ExtractionService
from ...deps import get_db, get_extraction_service

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
async def parse(
    result_id: str,
    organization_id: uuid.UUID | None = Query(None),
    client_id: uuid.UUID | None = Query(None),
    settings: Settings = Depends(get_settings),
    extraction: ExtractionService = Depends(get_extraction_service),
    db: AsyncSession = Depends(get_db),
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

    # Persist every populated business object (invoice.json, bank_statement.json, ...)
    # and use it as the DB extracted_data payload.
    business_payloads = {
        name: obj.model_dump(mode="json")
        for name, obj in parsed.business_objects().items()
    }
    for name, payload in business_payloads.items():
        save_json(out_dir / f"{name}.json", payload)

    extracted_biz_object = next(iter(business_payloads.values()), None)
    metadata_info = {
        "page_count": result.get("page_count", 1),
        "ocr_engine": result.get("engine", {}).get("pipeline", settings.ocr_pipeline),
        "processing_time_ms": result.get("processing_time_ms"),
    }
    # Persist to PostgreSQL as well
    await save_extracted_document_to_db(
        db,
        result_id=result_id,
        source_filename=result["filename"],
        document_type=parsed.document.document_type.value,
        extraction_status=parsed.document.extraction_status,
        needs_human_review=parsed.document.needs_human_review,
        review_reason=parsed.document.review_reason,
        ocr_confidence=parsed.document.ocr_confidence,
        extracted_data=extracted_biz_object,
        metadata=metadata_info,
        organization_id=organization_id,
        client_id=client_id,
    )

    return parsed
