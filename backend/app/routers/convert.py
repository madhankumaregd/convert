"""
Conversion router — provides endpoints for single-file and batch
file-format conversions.
"""

from __future__ import annotations

import asyncio
import os
import zipfile
import tempfile
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse

from ..config import MAX_FILE_SIZE
from ..utils.format_registry import (
    get_all_formats,
    get_category,
    get_valid_targets,
    is_valid_conversion,
)
from ..utils.file_utils import save_upload, generate_output_path, cleanup_file
from ..services.image_service import convert_image
from ..services.document_service import convert_document
from ..services.media_service import convert_audio, convert_video
from ..services.archive_service import convert_archive

router = APIRouter(tags=["convert"])


# ======================================================================
# GET /api/formats — return the full format registry for the frontend
# ======================================================================

@router.get("/formats")
async def list_formats():
    """Return the complete format registry so the frontend can build
    its dynamic source/target selectors."""
    return get_all_formats()


# ======================================================================
# POST /api/convert — single-file conversion
# ======================================================================

@router.post("/convert")
async def convert_file(
    file: UploadFile = File(...),
    target_format: str = Form(...),
):
    """Accept a file upload and convert it to *target_format*.

    Returns the converted file as a download with correct MIME type and
    ``Content-Disposition`` header.
    """
    # --- Validate upload -------------------------------------------------
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    source_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    target_ext = target_format.lower().lstrip(".")

    if not source_ext:
        raise HTTPException(status_code=400, detail="Could not determine source file extension.")

    if not is_valid_conversion(source_ext, target_ext):
        valid = get_valid_targets(source_ext)
        raise HTTPException(
            status_code=400,
            detail=f"Cannot convert .{source_ext} to .{target_ext}. "
                   f"Valid targets: {valid}",
        )

    # --- Save the upload -------------------------------------------------
    try:
        input_path, original_name = await save_upload(file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {exc}")

    # Check file size
    if os.path.getsize(input_path) > MAX_FILE_SIZE:
        cleanup_file(input_path)
        raise HTTPException(status_code=413, detail="File exceeds 500 MB limit.")

    output_path = generate_output_path(original_name, target_ext)

    # --- Perform conversion in a thread pool (CPU-bound) -----------------
    try:
        loop = asyncio.get_event_loop()
        category = get_category(source_ext)

        if category == "image":
            await loop.run_in_executor(None, convert_image, input_path, output_path, target_ext)
        elif category == "document":
            await loop.run_in_executor(None, convert_document, input_path, output_path, source_ext, target_ext)
        elif category == "audio":
            await loop.run_in_executor(None, convert_audio, input_path, output_path, target_ext)
        elif category == "video":
            await loop.run_in_executor(None, convert_video, input_path, output_path, target_ext)
        elif category == "archive":
            await loop.run_in_executor(None, convert_archive, input_path, output_path, source_ext, target_ext)
        else:
            cleanup_file(input_path)
            raise HTTPException(status_code=400, detail=f"Unsupported file category for .{source_ext}")

    except HTTPException:
        raise
    except Exception as exc:
        cleanup_file(input_path)
        cleanup_file(output_path)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")

    # --- Return the converted file ---------------------------------------
    download_name = os.path.splitext(original_name)[0] + f".{target_ext}"

    return FileResponse(
        path=output_path,
        filename=download_name,
        media_type="application/octet-stream",
        background=BackgroundTask(_cleanup_pair, input_path, output_path),
    )


# ======================================================================
# POST /api/convert/batch — batch conversion
# ======================================================================

@router.post("/convert/batch")
async def convert_batch(
    files: List[UploadFile] = File(...),
    target_format: str = Form(...),
):
    """Convert multiple files to *target_format* and return a ZIP archive
    containing all converted files."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    target_ext = target_format.lower().lstrip(".")
    converted_paths: list[str] = []
    input_paths: list[str] = []

    try:
        for upload in files:
            if not upload.filename:
                continue

            source_ext = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
            if not source_ext or not is_valid_conversion(source_ext, target_ext):
                continue  # skip unsupported files silently in batch mode

            input_path, original_name = await save_upload(upload)
            input_paths.append(input_path)

            if os.path.getsize(input_path) > MAX_FILE_SIZE:
                continue

            output_path = generate_output_path(original_name, target_ext)
            loop = asyncio.get_event_loop()
            category = get_category(source_ext)

            if category == "image":
                await loop.run_in_executor(None, convert_image, input_path, output_path, target_ext)
            elif category == "document":
                await loop.run_in_executor(None, convert_document, input_path, output_path, source_ext, target_ext)
            elif category == "audio":
                await loop.run_in_executor(None, convert_audio, input_path, output_path, target_ext)
            elif category == "video":
                await loop.run_in_executor(None, convert_video, input_path, output_path, target_ext)
            elif category == "archive":
                await loop.run_in_executor(None, convert_archive, input_path, output_path, source_ext, target_ext)
            else:
                continue

            converted_paths.append(output_path)

        if not converted_paths:
            raise HTTPException(status_code=400, detail="No files could be converted.")

        # --- Zip the results -----------------------------------------------
        zip_path = os.path.join(
            tempfile.gettempdir(),
            f"convert_batch_{os.urandom(4).hex()}.zip",
        )
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in converted_paths:
                zf.write(p, os.path.basename(p))

        # Collect all paths that need cleanup
        all_paths = input_paths + converted_paths

        return FileResponse(
            path=zip_path,
            filename="converted_files.zip",
            media_type="application/zip",
            background=BackgroundTask(_cleanup_many, all_paths + [zip_path]),
        )

    except HTTPException:
        raise
    except Exception as exc:
        # Best-effort cleanup on error
        for p in input_paths + converted_paths:
            cleanup_file(p)
        raise HTTPException(status_code=500, detail=f"Batch conversion failed: {exc}")


# ======================================================================
# Cleanup helpers
# ======================================================================

def _cleanup_pair(input_path: str, output_path: str) -> None:
    """Remove both the input and output temp files."""
    cleanup_file(input_path)
    cleanup_file(output_path)


def _cleanup_many(paths: list[str]) -> None:
    """Remove a list of temp files."""
    for p in paths:
        cleanup_file(p)
