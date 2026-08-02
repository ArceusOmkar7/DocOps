"""Application configuration loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    app_name: str = "AI Docs Orchestration"
    app_version: str = "0.1.0"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    data_dir: Path = BASE_DIR / "data"
    max_upload_size_mb: int = 50
    allowed_extensions: tuple[str, ...] = (
        ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp", ".pdf",
    )

    # OCR engine (PP-StructureV3 pipeline)
    ocr_pipeline: str = "PP-StructureV3"
    ocr_lang: str = "en"
    ocr_layout_model: str = "PP-DocLayout_plus-L"
    ocr_det_model: str = "PP-OCRv5_mobile_det"
    ocr_rec_model: str = "PP-OCRv5_mobile_rec"
    ocr_device: str = "cpu"
    ocr_enable_mkldnn: bool = False
    ocr_cpu_threads: int = 4
    ocr_use_doc_orientation_classify: bool = True
    ocr_use_doc_unwarping: bool = False
    ocr_use_textline_orientation: bool = True
    ocr_use_table_recognition: bool = True
    ocr_use_formula_recognition: bool = False
    ocr_use_chart_recognition: bool = False
    ocr_use_seal_recognition: bool = False
    ocr_use_region_detection: bool = True

    # LLM extraction (OpenAI-compatible /chat/completions API)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_max_retries: int = 3
    llm_timeout_seconds: float = 60.0
    llm_max_tokens: int = 2000
    llm_use_json_mode: bool = True

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def results_dir(self) -> Path:
        return self.data_dir / "results"

    def ensure_dirs(self) -> None:
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
