"""
Compression service — top-level router that delegates to the correct
category-specific compressor and returns unified size-savings metadata.
"""

from __future__ import annotations

import gzip
import os
import shutil
import zipfile

from ..utils.format_registry import get_category
from .image_service import compress_image
from .document_service import compress_document
from .media_service import compress_audio, compress_video


def compress_file(
    input_path: str,
    output_path: str,
    source_ext: str,
    quality: int = 85,
) -> dict:
    """Compress *input_path* and write the result to *output_path*.

    Routing logic:
    * **image**    → ``compress_image`` (Pillow)
    * **document** → ``compress_document`` (PyPDF2 / zip)
    * **audio**    → ``compress_audio`` (pydub, 128 kbps)
    * **video**    → ``compress_video`` (ffmpeg, CRF 28)
    * **archive**  → re-zip with maximum deflation
    * **unknown**  → gzip the raw file

    Returns a dict::

        {
            "original_size":   <int>,
            "compressed_size": <int>,
            "savings_percent": <float>,
        }
    """
    ext = source_ext.lower().lstrip(".")
    category = get_category(ext)
    original_size = os.path.getsize(input_path)

    # ---- Route to category handler ------------------------------------
    if category == "image":
        compress_image(input_path, output_path, quality=quality)

    elif category == "document":
        result_path = compress_document(input_path, output_path)
        # compress_document may change the output path (adds .zip)
        if result_path != output_path:
            output_path = result_path

    elif category == "audio":
        compress_audio(input_path, output_path, bitrate="128k")

    elif category == "video":
        compress_video(input_path, output_path, crf=28)

    elif category == "archive":
        _recompress_archive(input_path, output_path)

    else:
        # Fallback: gzip the file
        _gzip_file(input_path, output_path)

    compressed_size = os.path.getsize(output_path)
    savings = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0.0

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "savings_percent": round(max(savings, 0.0), 2),
        "output_path": output_path,
    }


# ======================================================================
# Internal helpers
# ======================================================================

def _recompress_archive(input_path: str, output_path: str) -> None:
    """Re-zip an archive with maximum deflate compression."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # Try to extract with zipfile first
        try:
            with zipfile.ZipFile(input_path, "r") as zin:
                zin.extractall(tmpdir)
        except zipfile.BadZipFile:
            # Not a zip — just gzip the raw file
            _gzip_file(input_path, output_path)
            return

        # Repack with maximum compression
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
            for root, _dirs, files in os.walk(tmpdir):
                for fname in files:
                    full_path = os.path.join(root, fname)
                    arcname = os.path.relpath(full_path, tmpdir)
                    zout.write(full_path, arcname)


def _gzip_file(input_path: str, output_path: str) -> None:
    """Gzip a file to *output_path*."""
    if not output_path.endswith(".gz"):
        output_path += ".gz"
    with open(input_path, "rb") as f_in, gzip.open(output_path, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)
