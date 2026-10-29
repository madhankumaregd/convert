"""
Document conversion and compression service.

Uses LibreOffice headless for high-fidelity DOCX ↔ PDF conversions
(preserving fonts, images, tables, colors, layout — like iLovePDF).

Falls back to pure-Python text-based conversion when LibreOffice is
not available on the system.

Supports: PDF, DOCX, TXT, XLSX, CSV
"""

from __future__ import annotations

import csv
import io
import os
import shutil
import subprocess
import tempfile
import zipfile

from PyPDF2 import PdfReader, PdfWriter
from docx import Document  # python-docx
from openpyxl import Workbook, load_workbook


# ======================================================================
# LibreOffice detection
# ======================================================================

def _find_libreoffice() -> str | None:
    """Locate the LibreOffice binary on the system."""
    # Common paths across different OS/containers
    candidates = [
        "libreoffice",
        "soffice",
        "/usr/bin/libreoffice",
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
        "/opt/libreoffice/program/soffice",
    ]
    for cmd in candidates:
        if shutil.which(cmd):
            return cmd
    return None


_LIBREOFFICE_BIN = _find_libreoffice()


def _is_libreoffice_available() -> bool:
    """Check if LibreOffice is installed and callable."""
    return _LIBREOFFICE_BIN is not None


# ======================================================================
# LibreOffice-based conversion (high fidelity)
# ======================================================================

def _convert_with_libreoffice(
    input_path: str,
    output_path: str,
    target_format: str,
) -> str:
    """Convert a document using LibreOffice headless mode.

    This preserves all formatting, images, tables, fonts, colors,
    headers, footers — essentially a pixel-perfect conversion.

    Supported target formats: pdf, docx, doc, txt, html, xlsx, csv, odt
    """
    assert _LIBREOFFICE_BIN is not None, "LibreOffice not found"

    # LibreOffice writes the output to --outdir with the same base name
    # but a different extension. We use a temp directory to avoid conflicts.
    with tempfile.TemporaryDirectory(prefix="lo_convert_") as tmp_dir:
        # Map target extensions to LibreOffice filter names
        format_map = {
            "pdf": "pdf",
            "docx": "docx",
            "doc": "doc",
            "txt": "txt",
            "html": "html",
            "xlsx": "xlsx",
            "csv": "csv",
            "odt": "odt",
        }

        lo_format = format_map.get(target_format.lower(), target_format.lower())

        # Build the LibreOffice command
        cmd = [
            _LIBREOFFICE_BIN,
            "--headless",
            "--norestore",
            "--nofirststartwizard",
            "--nologo",
            "--convert-to", lo_format,
            "--outdir", tmp_dir,
            input_path,
        ]

        # Set environment to avoid profile lock issues in concurrent usage
        env = os.environ.copy()
        env["HOME"] = tmp_dir  # Avoid profile locks

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2-minute timeout
            env=env,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(
                f"LibreOffice conversion failed (exit {result.returncode}): {stderr}"
            )

        # Find the output file in tmp_dir
        input_basename = os.path.splitext(os.path.basename(input_path))[0]
        expected_name = f"{input_basename}.{lo_format}"
        lo_output = os.path.join(tmp_dir, expected_name)

        if not os.path.exists(lo_output):
            # Sometimes LibreOffice changes the extension case or format
            # Search for any file in the output directory
            files = os.listdir(tmp_dir)
            matching = [
                f for f in files
                if f.startswith(input_basename) and not f.endswith(".tmp")
            ]
            if matching:
                lo_output = os.path.join(tmp_dir, matching[0])
            else:
                raise RuntimeError(
                    f"LibreOffice did not produce output. "
                    f"Expected: {expected_name}, Found: {files}"
                )

        # Copy to final output path
        shutil.copy2(lo_output, output_path)

    return output_path


# ======================================================================
# Pure-Python fallback helpers (text-based, lower quality)
# ======================================================================

def _extract_text_from_pdf(path: str) -> str:
    """Extract all text from a PDF file."""
    reader = PdfReader(path)
    pages_text: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return "\n\n".join(pages_text)


def _extract_text_from_docx(path: str) -> str:
    """Extract all paragraph text from a DOCX file."""
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _create_pdf_from_text(text: str, output_path: str) -> str:
    """Create a minimal PDF from plain text (fallback when LibreOffice unavailable).

    Uses raw PDF stream construction — no formatting preserved.
    """
    safe_text = (
        text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
    )

    lines = safe_text.split("\n")
    max_lines_per_page = 60
    pages_content: list[str] = []

    for i in range(0, len(lines), max_lines_per_page):
        page_lines = lines[i : i + max_lines_per_page]
        y = 750
        text_ops: list[str] = []
        for line in page_lines:
            text_ops.append(f"BT /F1 10 Tf 50 {y} Td ({line}) Tj ET")
            y -= 12
        pages_content.append("\n".join(text_ops))

    objects: list[str] = []
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    page_obj_numbers: list[int] = []
    obj_counter = 4

    objects.append(
        "3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj"
    )

    for content in pages_content:
        stream_obj = obj_counter
        stream_bytes = content.encode("latin-1", errors="replace")
        objects.append(
            f"{stream_obj} 0 obj\n"
            f"<< /Length {len(stream_bytes)} >>\n"
            f"stream\n{content}\nendstream\nendobj"
        )
        obj_counter += 1

        page_obj = obj_counter
        page_obj_numbers.append(page_obj)
        objects.append(
            f"{page_obj} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 612 792] "
            f"/Contents {stream_obj} 0 R "
            f"/Resources << /Font << /F1 3 0 R >> >> >>\n"
            f"endobj"
        )
        obj_counter += 1

    kids = " ".join(f"{n} 0 R" for n in page_obj_numbers)
    pages_obj = (
        f"2 0 obj\n<< /Type /Pages /Kids [{kids}] "
        f"/Count {len(page_obj_numbers)} >>\nendobj"
    )
    objects.insert(1, pages_obj)

    pdf_lines: list[str] = ["%PDF-1.4"]
    offsets: list[int] = []
    current_offset = len(pdf_lines[0]) + 1

    for obj_str in objects:
        offsets.append(current_offset)
        pdf_lines.append(obj_str)
        current_offset += len(obj_str.encode("latin-1", errors="replace")) + 1

    xref_offset = current_offset
    xref_lines = [f"xref\n0 {len(offsets) + 1}", "0000000000 65535 f "]
    for off in offsets:
        xref_lines.append(f"{off:010d} 00000 n ")
    pdf_lines.append("\n".join(xref_lines))

    pdf_lines.append(
        f"trailer\n<< /Size {len(offsets) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    )

    with open(output_path, "wb") as f:
        f.write("\n".join(pdf_lines).encode("latin-1", errors="replace"))

    return output_path


def _create_docx_from_text(text: str, output_path: str) -> str:
    """Create a DOCX file from plain text."""
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(output_path)
    return output_path


# ======================================================================
# Public API
# ======================================================================

def convert_document(
    input_path: str,
    output_path: str,
    source_ext: str,
    target_ext: str,
) -> str:
    """Convert a document from *source_ext* to *target_ext*.

    Strategy:
    1. If LibreOffice is available → use it for maximum fidelity
       (preserves fonts, images, tables, colors, layout).
    2. Otherwise → fall back to pure-Python text extraction
       (formatting will be lost).

    Supported routes:
    - PDF  → TXT / DOCX
    - DOCX → TXT / PDF
    - TXT  → PDF / DOCX
    - XLSX → CSV / PDF
    - CSV  → XLSX / PDF

    Returns *output_path* on success.
    Raises ``ValueError`` for unsupported conversion pairs.
    """
    src = source_ext.lower().lstrip(".")
    tgt = target_ext.lower().lstrip(".")

    # ---- Try LibreOffice first (high fidelity) --------------------------
    # Use LibreOffice for all conversions EXCEPT plain text output
    # (text extraction is fine with Python) and CSV↔XLSX (openpyxl is great)
    libreoffice_routes = {
        ("pdf", "docx"), ("docx", "pdf"),
        ("pdf", "doc"), ("doc", "pdf"),
        ("xlsx", "pdf"), ("docx", "xlsx"),
        ("xlsx", "docx"),
    }

    if (src, tgt) in libreoffice_routes and _is_libreoffice_available():
        return _convert_with_libreoffice(input_path, output_path, tgt)

    # ---- Pure-Python fallback routes ------------------------------------

    # PDF → TXT
    if src == "pdf" and tgt == "txt":
        text = _extract_text_from_pdf(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path

    # PDF → DOCX (without LibreOffice)
    if src == "pdf" and tgt == "docx":
        if _is_libreoffice_available():
            return _convert_with_libreoffice(input_path, output_path, tgt)
        text = _extract_text_from_pdf(input_path)
        return _create_docx_from_text(text, output_path)

    # DOCX → TXT
    if src == "docx" and tgt == "txt":
        text = _extract_text_from_docx(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path

    # DOCX → PDF (without LibreOffice — text-based fallback)
    if src == "docx" and tgt == "pdf":
        if _is_libreoffice_available():
            return _convert_with_libreoffice(input_path, output_path, tgt)
        text = _extract_text_from_docx(input_path)
        return _create_pdf_from_text(text, output_path)

    # TXT → PDF
    if src == "txt" and tgt == "pdf":
        if _is_libreoffice_available():
            return _convert_with_libreoffice(input_path, output_path, tgt)
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return _create_pdf_from_text(text, output_path)

    # TXT → DOCX
    if src == "txt" and tgt == "docx":
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return _create_docx_from_text(text, output_path)

    # XLSX → CSV
    if src == "xlsx" and tgt == "csv":
        wb = load_workbook(input_path, read_only=True, data_only=True)
        ws = wb.active
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(row)
        wb.close()
        return output_path

    # XLSX → PDF
    if src == "xlsx" and tgt == "pdf":
        if _is_libreoffice_available():
            return _convert_with_libreoffice(input_path, output_path, tgt)
        wb = load_workbook(input_path, read_only=True, data_only=True)
        ws = wb.active
        lines: list[str] = []
        for row in ws.iter_rows(values_only=True):
            lines.append("\t".join(str(c) if c is not None else "" for c in row))
        wb.close()
        return _create_pdf_from_text("\n".join(lines), output_path)

    # CSV → XLSX
    if src == "csv" and tgt == "xlsx":
        wb = Workbook()
        ws = wb.active
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader, start=1):
                for col_idx, value in enumerate(row, start=1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
        wb.save(output_path)
        return output_path

    # CSV → PDF
    if src == "csv" and tgt == "pdf":
        if _is_libreoffice_available():
            return _convert_with_libreoffice(input_path, output_path, tgt)
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return _create_pdf_from_text(text, output_path)

    raise ValueError(f"Unsupported document conversion: {src} → {tgt}")


def compress_document(input_path: str, output_path: str) -> str:
    """Compress a document file.

    * **PDF** — rebuilds the PDF with PyPDF2 which drops duplicate
      objects and unused resources.
    * **Other formats** — wrapped in a ZIP archive for size reduction.

    Returns *output_path*.
    """
    ext = os.path.splitext(input_path)[1].lower().lstrip(".")

    if ext == "pdf":
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.remove_links()  # strips link annotations
        with open(output_path, "wb") as f:
            writer.write(f)
        return output_path

    # For non-PDF documents, zip-compress the file
    base_name = os.path.basename(input_path)
    if not output_path.endswith(".zip"):
        output_path = output_path + ".zip"
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(input_path, base_name)
    return output_path
