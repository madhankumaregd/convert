FROM python:3.12-slim

# Install system dependencies:
#  - ffmpeg for audio/video conversion
#  - LibreOffice Writer & Calc for high-fidelity document conversion (DOCX↔PDF)
#  - fonts-liberation & fonts-dejavu for proper font rendering in PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libreoffice-writer \
    libreoffice-calc \
    fonts-liberation \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
