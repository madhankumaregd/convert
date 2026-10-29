"""
Document conversion and compression service.

Supports conversions between PDF, DOCX, TXT, XLSX, and CSV using
PyPDF2, python-docx, openpyxl, and the standard-library csv module.
"""

from __future__ import annotations

import csv
import io
import os
import zipfile

from PyPDF2 import PdfReader, PdfWriter
from docx import Document  # python-docx
from openpyxl import Workbook, load_workbook


# ======================================================================
# Internal helpers
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
    """Create a minimal, valid single-page PDF containing *text*.

    Uses raw PDF stream construction so we have zero extra dependencies
    beyond the standard library.  The text is encoded in Latin-1; any
    characters outside that range are replaced with '?'.
    """
    # Escape special PDF characters in the text
    safe_text = (
        text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
    )

    # Split into lines and paginate (approx 60 lines per page at 12pt)
    lines = safe_text.split("\n")
    max_lines_per_page = 60
    pages_content: list[str] = []

    for i in range(0, len(lines), max_lines_per_page):
        page_lines = lines[i : i + max_lines_per_page]
        # Build the text-drawing operators for this page
        y = 750  # starting Y position
        text_ops: list[str] = []
        for line in page_lines:
            text_ops.append(f"BT /F1 10 Tf 50 {y} Td ({line}) Tj ET")
            y -= 12
        pages_content.append("\n".join(text_ops))

    # Build the PDF object tree
    objects: list[str] = []
    # Object 1 – Catalog
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    # Object 2 – Pages (built after we know page count)
    page_obj_numbers: list[int] = []
    obj_counter = 4  # 1=catalog, 2=pages, 3=font

    # Object 3 – Font
    objects.append(
        "3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj"
    )

    for content in pages_content:
        # Stream object for page content
        stream_obj = obj_counter
        stream_bytes = content.encode("latin-1", errors="replace")
        objects.append(
            f"{stream_obj} 0 obj\n"
            f"<< /Length {len(stream_bytes)} >>\n"
            f"stream\n{content}\nendstream\nendobj"
        )
        obj_counter += 1

        # Page object
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

    # Now build object 2 (Pages)
    kids = " ".join(f"{n} 0 R" for n in page_obj_numbers)
    pages_obj = (
        f"2 0 obj\n<< /Type /Pages /Kids [{kids}] "
        f"/Count {len(page_obj_numbers)} >>\nendobj"
    )
    # Insert pages object at position 1 (after catalog)
    objects.insert(1, pages_obj)

    # Assemble the full PDF
    pdf_lines: list[str] = ["%PDF-1.4"]
    offsets: list[int] = []
    current_offset = len(pdf_lines[0]) + 1  # +1 for newline

    for obj_str in objects:
        offsets.append(current_offset)
        pdf_lines.append(obj_str)
        current_offset += len(obj_str.encode("latin-1", errors="replace")) + 1

    # Cross-reference table
    xref_offset = current_offset
    xref_lines = [f"xref\n0 {len(offsets) + 1}", "0000000000 65535 f "]
    for off in offsets:
        xref_lines.append(f"{off:010d} 00000 n ")
    pdf_lines.append("\n".join(xref_lines))

    # Trailer
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

    # ---- PDF source ------------------------------------------------------
    if src == "pdf" and tgt == "txt":
        text = _extract_text_from_pdf(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path

    if src == "pdf" and tgt == "docx":
        text = _extract_text_from_pdf(input_path)
        return _create_docx_from_text(text, output_path)

    # ---- DOCX source -----------------------------------------------------
    if src == "docx" and tgt == "txt":
        text = _extract_text_from_docx(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path

    if src == "docx" and tgt == "pdf":
        text = _extract_text_from_docx(input_path)
        return _create_pdf_from_text(text, output_path)

    # ---- TXT source ------------------------------------------------------
    if src == "txt" and tgt == "pdf":
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return _create_pdf_from_text(text, output_path)

    if src == "txt" and tgt == "docx":
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return _create_docx_from_text(text, output_path)

    # ---- XLSX source -----------------------------------------------------
    if src == "xlsx" and tgt == "csv":
        wb = load_workbook(input_path, read_only=True, data_only=True)
        ws = wb.active
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(row)
        wb.close()
        return output_path

    if src == "xlsx" and tgt == "pdf":
        wb = load_workbook(input_path, read_only=True, data_only=True)
        ws = wb.active
        lines: list[str] = []
        for row in ws.iter_rows(values_only=True):
            lines.append("\t".join(str(c) if c is not None else "" for c in row))
        wb.close()
        return _create_pdf_from_text("\n".join(lines), output_path)

    # ---- CSV source ------------------------------------------------------
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

    if src == "csv" and tgt == "pdf":
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
        # Remove unused objects to shrink the file
        writer.remove_links()  # strips link annotations
        with open(output_path, "wb") as f:
            writer.write(f)
        return output_path

    # For non-PDF documents, zip-compress the file
    base_name = os.path.basename(input_path)
    # Ensure output has .zip extension for generic compression
    if not output_path.endswith(".zip"):
        output_path = output_path + ".zip"
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(input_path, base_name)
    return output_path
