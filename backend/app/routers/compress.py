"""
Compression router — provides endpoints for single-file and batch
file compression with size-savings metadata.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import zipfile
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse

from ..config import MAX_FILE_SIZE
from ..utils.file_utils import (
    save_upload,
    generate_output_path,
    cleanup_file,
    get_file_size_str,
)
from ..services.compression_service import compress_file

router = APIRouter(tags=["compress"])


# ======================================================================
# POST /api/compress — single-file compression
# ======================================================================

@router.post("/compress")
async def compress_single(
    file: UploadFile = File(...),
    quality: Optional[int] = Form(85),
):
    """Compress a single file and return it with metadata headers:

    * ``X-Original-Size`` — original file size in bytes
    * ``X-Compressed-Size`` — compressed file size in bytes
    * ``X-Savings-Percent`` — percentage of space saved
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    source_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if not source_ext:
        raise HTTPException(status_code=400, detail="Could not determine file extension.")

    # --- Save the upload -------------------------------------------------
    try:
        input_path, original_name = await save_upload(file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {exc}")

    if os.path.getsize(input_path) > MAX_FILE_SIZE:
        cleanup_file(input_path)
        raise HTTPException(status_code=413, detail="File exceeds 500 MB limit.")

    output_path = generate_output_path(original_name, source_ext)

    # --- Compress in a thread pool (CPU-bound) ---------------------------
    try:
        loop = asyncio.get_event_loop()
        result: dict = await loop.run_in_executor(
            None,
            compress_file,
            input_path,
            output_path,
            source_ext,
            quality or 85,
        )
        # The compression service may have changed the output path
        actual_output = result.get("output_path", output_path)

    except Exception as exc:
        cleanup_file(input_path)
        cleanup_file(output_path)
        raise HTTPException(status_code=500, detail=f"Compression failed: {exc}")

    # --- Build the response with metadata headers ------------------------
    download_name = f"compressed_{original_name}"

    response = FileResponse(
        path=actual_output,
        filename=download_name,
        media_type="application/octet-stream",
        background=BackgroundTask(_cleanup_pair, input_path, actual_output),
    )
    response.headers["X-Original-Size"] = str(result["original_size"])
    response.headers["X-Compressed-Size"] = str(result["compressed_size"])
    response.headers["X-Savings-Percent"] = str(result["savings_percent"])
    response.headers["X-Original-Size-Human"] = get_file_size_str(result["original_size"])
    response.headers["X-Compressed-Size-Human"] = get_file_size_str(result["compressed_size"])
    # Expose custom headers to the browser
    response.headers["Access-Control-Expose-Headers"] = (
        "X-Original-Size, X-Compressed-Size, X-Savings-Percent, "
        "X-Original-Size-Human, X-Compressed-Size-Human"
    )

    return response


# ======================================================================
# POST /api/compress/batch — batch compression
# ======================================================================

@router.post("/compress/batch")
async def compress_batch(
    files: List[UploadFile] = File(...),
    quality: Optional[int] = Form(85),
):
    """Compress multiple files and return a ZIP archive containing all
    compressed results."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    compressed_paths: list[str] = []
    input_paths: list[str] = []
    total_original = 0
    total_compressed = 0

    try:
        for upload in files:
            if not upload.filename:
                continue

            source_ext = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
            if not source_ext:
                continue

            input_path, original_name = await save_upload(upload)
            input_paths.append(input_path)

            if os.path.getsize(input_path) > MAX_FILE_SIZE:
                continue

            output_path = generate_output_path(original_name, source_ext)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                compress_file,
                input_path,
                output_path,
                source_ext,
                quality or 85,
            )

            actual_output = result.get("output_path", output_path)
            compressed_paths.append(actual_output)
            total_original += result["original_size"]
            total_compressed += result["compressed_size"]

        if not compressed_paths:
            raise HTTPException(status_code=400, detail="No files could be compressed.")

        # --- Zip the results -----------------------------------------------
        zip_path = os.path.join(
            tempfile.gettempdir(),
            f"compress_batch_{os.urandom(4).hex()}.zip",
        )
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in compressed_paths:
                zf.write(p, os.path.basename(p))

        all_paths = input_paths + compressed_paths
        total_savings = (
            round((total_original - total_compressed) / total_original * 100, 2)
            if total_original > 0
            else 0.0
        )

        response = FileResponse(
            path=zip_path,
            filename="compressed_files.zip",
            media_type="application/zip",
            background=BackgroundTask(_cleanup_many, all_paths + [zip_path]),
        )
        response.headers["X-Original-Size"] = str(total_original)
        response.headers["X-Compressed-Size"] = str(total_compressed)
        response.headers["X-Savings-Percent"] = str(total_savings)
        response.headers["Access-Control-Expose-Headers"] = (
            "X-Original-Size, X-Compressed-Size, X-Savings-Percent"
        )
        return response

    except HTTPException:
        raise
    except Exception as exc:
        for p in input_paths + compressed_paths:
            cleanup_file(p)
        raise HTTPException(status_code=500, detail=f"Batch compression failed: {exc}")


# ======================================================================
# Cleanup helpers
# ======================================================================

def _cleanup_pair(input_path: str, output_path: str) -> None:
    cleanup_file(input_path)
    cleanup_file(output_path)


def _cleanup_many(paths: list[str]) -> None:
    for p in paths:
        cleanup_file(p)
