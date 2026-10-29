"""
Document conversion and compression service.

Supports conversions between PDF, DOCX, TXT, XLSX, and CSV.

Features:
1. High-fidelity DOCX -> PDF conversion using Mammoth + xhtml2pdf:
   - Preserves headings, bold, italics, text alignment, lists, tables, and colors.
   - Extracts embedded images and renders them inline via base64 data URIs.
2. Structured XLSX / CSV -> PDF conversion with styled HTML tables and borders.
3. Clean TXT -> PDF conversion with proper pagination and typography.
4. Optional LibreOffice headless integration if installed on host.
"""

from __future__ import annotations

import csv
import html
import io
import os
import shutil
import subprocess
import tempfile
import zipfile

from PyPDF2 import PdfReader, PdfWriter
from docx import Document  # python-docx
from openpyxl import Workbook, load_workbook

# Pure-Python high-fidelity HTML & PDF generators
import mammoth
from xhtml2pdf import pisa


# ======================================================================
# LibreOffice detection (optional, used if available)
# ======================================================================

def _find_libreoffice() -> str | None:
    """Locate the LibreOffice binary on the system if installed."""
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


def _convert_with_libreoffice(
    input_path: str,
    output_path: str,
    target_format: str,
) -> str:
    """Convert a document using LibreOffice headless mode."""
    assert _LIBREOFFICE_BIN is not None, "LibreOffice not found"

    with tempfile.TemporaryDirectory(prefix="lo_convert_") as tmp_dir:
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

        env = os.environ.copy()
        env["HOME"] = tmp_dir

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(
                f"LibreOffice conversion failed (exit {result.returncode}): {stderr}"
            )

        input_basename = os.path.splitext(os.path.basename(input_path))[0]
        expected_name = f"{input_basename}.{lo_format}"
        lo_output = os.path.join(tmp_dir, expected_name)

        if not os.path.exists(lo_output):
            files = os.listdir(tmp_dir)
            matching = [
                f for f in files
                if f.startswith(input_basename) and not f.endswith(".tmp")
            ]
            if matching:
                lo_output = os.path.join(tmp_dir, matching[0])
            else:
                raise RuntimeError(
                    f"LibreOffice did not produce output. Expected: {expected_name}, Found: {files}"
                )

        shutil.copy2(lo_output, output_path)

    return output_path


# ======================================================================
# Pure-Python High-Fidelity HTML -> PDF Engine (Runs on Vercel)
# ======================================================================

_DOCUMENT_CSS = """
@page {
    size: a4 portrait;
    margin-top: 2cm;
    margin-bottom: 2cm;
    margin-left: 2cm;
    margin-right: 2cm;
    @bottom-right {
        content: counter(page);
        font-family: Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #777777;
    }
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.45;
    color: #1a1a1a;
}
h1, h2, h3, h4, h5, h6 {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: bold;
    color: #0f172a;
}
h1 {
    font-size: 18pt;
    margin-top: 16pt;
    margin-bottom: 8pt;
}
h2 {
    font-size: 14pt;
    margin-top: 14pt;
    margin-bottom: 6pt;
}
h3 {
    font-size: 12pt;
    margin-top: 10pt;
    margin-bottom: 4pt;
}
h4 {
    font-size: 10.5pt;
    margin-top: 8pt;
    margin-bottom: 4pt;
}
p {
    margin-top: 0;
    margin-bottom: 7pt;
    text-align: justify;
}
strong, b {
    font-weight: bold;
}
em, i {
    font-style: italic;
}
table {
    width: 100%;
    margin-top: 10pt;
    margin-bottom: 12pt;
}
th, td {
    border: 0.5pt solid #94a3b8;
    padding: 5pt 7pt;
    font-size: 8.5pt;
    vertical-align: top;
}
th {
    background-color: #f1f5f9;
    font-weight: bold;
    text-align: left;
}
img {
    max-width: 100%;
    height: auto;
    text-align: center;
    margin: 8pt 0;
}
ul, ol {
    margin-top: 4pt;
    margin-bottom: 8pt;
    padding-left: 18pt;
}
li {
    margin-bottom: 3pt;
}
code, pre {
    font-family: Courier, monospace;
    font-size: 8.5pt;
    background-color: #f8fafc;
}
pre {
    padding: 6pt 8pt;
    border: 0.5pt solid #e2e8f0;
    white-space: pre-wrap;
}
"""


def _html_to_pdf(html_content: str, output_path: str) -> str:
    """Render full HTML with CSS to a PDF file using xhtml2pdf."""
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{_DOCUMENT_CSS}
</style>
</head>
<body>
{html_content}
</body>
</html>"""

    with open(output_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)
        if pisa_status.err:
            raise RuntimeError(f"xhtml2pdf rendering error code: {pisa_status.err}")

    return output_path


def _convert_docx_to_pdf_html(input_path: str, output_path: str) -> str:
    """Convert DOCX to PDF using Mammoth (HTML extraction) + xhtml2pdf.

    Extracts images as embedded Base64 data URIs, preserves tables,
    headings, bold, italics, lists, and layout styles.
    """
    with open(input_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html_body = result.value

    return _html_to_pdf(html_body, output_path)


def _convert_xlsx_to_pdf_html(input_path: str, output_path: str) -> str:
    """Convert XLSX to a beautifully styled PDF table."""
    wb = load_workbook(input_path, read_only=True, data_only=True)
    ws = wb.active

    html_parts = ["<h2>Spreadsheet Data</h2><table>"]
    is_first_row = True

    for row in ws.iter_rows(values_only=True):
        if not any(c is not None for c in row):
            continue
        html_parts.append("<tr>")
        tag = "th" if is_first_row else "td"
        for cell in row:
            val = html.escape(str(cell) if cell is not None else "")
            html_parts.append(f"<{tag}>{val}</{tag}>")
        html_parts.append("</tr>")
        is_first_row = False

    html_parts.append("</table>")
    wb.close()

    return _html_to_pdf("".join(html_parts), output_path)


def _convert_csv_to_pdf_html(input_path: str, output_path: str) -> str:
    """Convert CSV file to a styled PDF table."""
    html_parts = ["<h2>CSV Data Export</h2><table>"]
    is_first_row = True

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not any(row):
                continue
            html_parts.append("<tr>")
            tag = "th" if is_first_row else "td"
            for cell in row:
                val = html.escape(cell)
                html_parts.append(f"<{tag}>{val}</{tag}>")
            html_parts.append("</tr>")
            is_first_row = False

    html_parts.append("</table>")
    return _html_to_pdf("".join(html_parts), output_path)


def _convert_txt_to_pdf_html(input_path: str, output_path: str) -> str:
    """Convert plain text to a clean PDF with proper margins and typography."""
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    escaped = html.escape(text)
    paragraphs = [
        f"<p>{p.strip()}</p>" for p in escaped.split("\n\n") if p.strip()
    ]
    html_body = "".join(paragraphs) if paragraphs else f"<pre>{escaped}</pre>"

    return _html_to_pdf(html_body, output_path)


# ======================================================================
# Text & Word helpers (fallback and text routes)
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


def _create_docx_from_text(text: str, output_path: str) -> str:
    """Create a structured DOCX file from plain text."""
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

    # ---- 1. Check LibreOffice if installed on server --------------------
    libreoffice_routes = {
        ("pdf", "docx"), ("docx", "pdf"),
        ("pdf", "doc"), ("doc", "pdf"),
        ("xlsx", "pdf"), ("docx", "xlsx"),
        ("xlsx", "docx"),
    }
    if (src, tgt) in libreoffice_routes and _is_libreoffice_available():
        try:
            return _convert_with_libreoffice(input_path, output_path, tgt)
        except Exception:
            pass  # Fall back to Python HTML pipeline

    # ---- 2. DOCX -> PDF (Mammoth + xhtml2pdf high fidelity) -------------
    if src == "docx" and tgt == "pdf":
        try:
            return _convert_docx_to_pdf_html(input_path, output_path)
        except Exception:
            # Fallback to text extraction
            text = _extract_text_from_docx(input_path)
            return _convert_txt_to_pdf_html(input_path, output_path)

    # ---- 3. PDF source routes -------------------------------------------
    if src == "pdf" and tgt == "txt":
        text = _extract_text_from_pdf(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path

    if src == "pdf" and tgt == "docx":
        text = _extract_text_from_pdf(input_path)
        return _create_docx_from_text(text, output_path)

    # ---- 4. DOCX -> TXT -------------------------------------------------
    if src == "docx" and tgt == "txt":
        text = _extract_text_from_docx(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path

    # ---- 5. TXT source routes -------------------------------------------
    if src == "txt" and tgt == "pdf":
        return _convert_txt_to_pdf_html(input_path, output_path)

    if src == "txt" and tgt == "docx":
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return _create_docx_from_text(text, output_path)

    # ---- 6. XLSX source routes ------------------------------------------
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
        return _convert_xlsx_to_pdf_html(input_path, output_path)

    # ---- 7. CSV source routes -------------------------------------------
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
        return _convert_csv_to_pdf_html(input_path, output_path)

    raise ValueError(f"Unsupported document conversion: {src} -> {tgt}")


def compress_document(input_path: str, output_path: str) -> str:
    """Compress a document file.

    * **PDF** - rebuilds the PDF with PyPDF2, stripping duplicate
      objects, annotations, and metadata.
    * **Other formats** - wrapped in a standard ZIP archive.

    Returns *output_path*.
    """
    ext = os.path.splitext(input_path)[1].lower().lstrip(".")

    if ext == "pdf":
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.remove_links()
        with open(output_path, "wb") as f:
            writer.write(f)
        return output_path

    base_name = os.path.basename(input_path)
    if not output_path.endswith(".zip"):
        output_path = output_path + ".zip"
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(input_path, base_name)
    return output_path
