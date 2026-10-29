"""
Archive conversion service.

Extracts source archives into a temporary directory and repackages them
into the requested target archive format.

Supported formats: zip, tar, gz (tar.gz), bz2 (tar.bz2), 7z*, rar*.

*7z and rar EXTRACTION requires the ``py7zr`` / ``rarfile`` packages
 or the ``7z`` CLI.  If unavailable the service falls back to extracting
 with the corresponding CLI tool (if present) or raises an error.
"""

from __future__ import annotations

import bz2
import gzip
import os
import shutil
import tarfile
import tempfile
import zipfile


def convert_archive(
    input_path: str,
    output_path: str,
    source_ext: str,
    target_ext: str,
) -> str:
    """Convert an archive from *source_ext* to *target_ext*.

    Workflow:
    1. Extract the source archive into a temporary directory.
    2. Re-pack the contents into the target format.

    Returns *output_path* on success.
    """
    src = source_ext.lower().lstrip(".")
    tgt = target_ext.lower().lstrip(".")

    with tempfile.TemporaryDirectory() as tmpdir:
        # ---- Step 1: Extract ------------------------------------------------
        _extract(input_path, src, tmpdir)

        # ---- Step 2: Re-pack ------------------------------------------------
        _pack(tmpdir, output_path, tgt)

    return output_path


# ======================================================================
# Internal extraction helpers
# ======================================================================

def _extract(path: str, ext: str, dest: str) -> None:
    """Extract the archive at *path* (with extension *ext*) into *dest*."""
    if ext == "zip":
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(dest)

    elif ext == "tar":
        with tarfile.open(path, "r:") as tf:
            tf.extractall(dest)

    elif ext == "gz":
        # Could be a tar.gz or a standalone gzip file
        try:
            with tarfile.open(path, "r:gz") as tf:
                tf.extractall(dest)
        except tarfile.TarError:
            # Standalone .gz — decompress to a single file
            out_name = os.path.basename(path).removesuffix(".gz") or "file"
            with gzip.open(path, "rb") as gz_in, \
                 open(os.path.join(dest, out_name), "wb") as f_out:
                shutil.copyfileobj(gz_in, f_out)

    elif ext == "bz2":
        try:
            with tarfile.open(path, "r:bz2") as tf:
                tf.extractall(dest)
        except tarfile.TarError:
            out_name = os.path.basename(path).removesuffix(".bz2") or "file"
            with bz2.open(path, "rb") as bz_in, \
                 open(os.path.join(dest, out_name), "wb") as f_out:
                shutil.copyfileobj(bz_in, f_out)

    elif ext == "7z":
        # Try py7zr first, then fall back to CLI
        try:
            import py7zr  # type: ignore[import-untyped]
            with py7zr.SevenZipFile(path, "r") as sz:
                sz.extractall(dest)
        except ImportError:
            _cli_extract(["7z", "x", f"-o{dest}", "-y", path])

    elif ext == "rar":
        try:
            import rarfile  # type: ignore[import-untyped]
            with rarfile.RarFile(path, "r") as rf:
                rf.extractall(dest)
        except ImportError:
            _cli_extract(["unrar", "x", "-y", path, dest])

    else:
        raise ValueError(f"Cannot extract archive format: .{ext}")


def _cli_extract(cmd: list[str]) -> None:
    """Run an external extraction command and raise on failure."""
    import subprocess

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Extraction failed: {result.stderr[:500]}")


# ======================================================================
# Internal packing helpers
# ======================================================================

def _pack(source_dir: str, output_path: str, ext: str) -> None:
    """Pack the contents of *source_dir* into *output_path* as .*ext*."""
    if ext == "zip":
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for root, _dirs, files in os.walk(source_dir):
                for fname in files:
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, source_dir)
                    zf.write(full, arcname)

    elif ext == "tar":
        with tarfile.open(output_path, "w") as tf:
            for root, _dirs, files in os.walk(source_dir):
                for fname in files:
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, source_dir)
                    tf.add(full, arcname)

    elif ext == "gz":
        # Create a tar.gz archive
        with tarfile.open(output_path, "w:gz") as tf:
            for root, _dirs, files in os.walk(source_dir):
                for fname in files:
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, source_dir)
                    tf.add(full, arcname)

    elif ext == "bz2":
        # Create a tar.bz2 archive
        with tarfile.open(output_path, "w:bz2") as tf:
            for root, _dirs, files in os.walk(source_dir):
                for fname in files:
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, source_dir)
                    tf.add(full, arcname)

    else:
        raise ValueError(f"Cannot create archive format: .{ext}")
