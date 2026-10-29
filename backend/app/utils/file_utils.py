"""
File-system utilities for upload handling, output path generation,
temporary file cleanup, and human-readable size formatting.
"""

from __future__ import annotations

import os
import uuid

from fastapi import UploadFile

from ..config import UPLOAD_DIR, OUTPUT_DIR


async def save_upload(file: UploadFile) -> tuple[str, str]:
    """Persist an uploaded file to *UPLOAD_DIR* with a unique name.

    Returns
    -------
    tuple[str, str]
        ``(saved_path, original_filename)``
    """
    original_filename: str = file.filename or "unknown"
    # Build a unique filename to avoid collisions
    ext = os.path.splitext(original_filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, unique_name)

    # Stream the upload to disk in chunks (memory-friendly for large files)
    with open(saved_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1 MB chunks
            f.write(chunk)

    return saved_path, original_filename


def generate_output_path(original_name: str, target_ext: str) -> str:
    """Create a unique output path inside *OUTPUT_DIR*.

    The returned path uses the original file's stem combined with a UUID
    fragment so the download filename is still recognisable to the user.
    """
    stem = os.path.splitext(os.path.basename(original_name))[0]
    target_ext = target_ext.lstrip(".")
    unique_name = f"{stem}_{uuid.uuid4().hex[:8]}.{target_ext}"
    return os.path.join(OUTPUT_DIR, unique_name)


def cleanup_file(path: str) -> None:
    """Delete *path* from disk if it exists.  Silently ignores missing files."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass  # best-effort cleanup


def get_file_size_str(size_bytes: int) -> str:
    """Return a human-readable string for *size_bytes*.

    Examples: ``"1.23 MB"``, ``"456 KB"``, ``"78 B"``
    """
    if size_bytes < 0:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}" if unit != "B" else f"{size_bytes} B"
        size_bytes /= 1024  # type: ignore[assignment]
    return f"{size_bytes:.2f} PB"
