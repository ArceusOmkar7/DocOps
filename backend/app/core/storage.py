"""Filesystem persistence for uploads and OCR results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from .config import Settings


class StorageError(Exception):
    """Base error for storage operations."""


class UploadTooLarge(StorageError):
    def __init__(self, max_upload_size_mb: int):
        self.max_upload_size_mb = max_upload_size_mb
        super().__init__(f"Upload exceeds the {max_upload_size_mb} MB limit.")


def new_result_id() -> str:
    return uuid4().hex


def upload_dir(settings: Settings, result_id: str) -> Path:
    return settings.uploads_dir / result_id


def result_dir(settings: Settings, result_id: str) -> Path:
    return settings.results_dir / result_id


def save_upload(
    settings: Settings, result_id: str, filename: str, stream: BinaryIO
) -> Path:
    """Persist an uploaded file, enforcing the configured size limit."""
    dest_dir = upload_dir(settings, result_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    written = 0
    with dest.open("wb") as out:
        while chunk := stream.read(1024 * 1024):
            written += len(chunk)
            if written > max_bytes:
                dest.unlink(missing_ok=True)
                raise UploadTooLarge(settings.max_upload_size_mb)
            out.write(chunk)
    return dest


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
