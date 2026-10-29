"""
Convert API — FastAPI application entry point.

Assembles the routers, configures CORS, sets up temp directories on
startup, and provides a root health-check / info endpoint.
"""

from __future__ import annotations

import os
import shutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import UPLOAD_DIR, OUTPUT_DIR
from .routers import convert, compress

# ======================================================================
# Application factory
# ======================================================================

app = FastAPI(
    title="Convert API",
    description=(
        "Universal file converter & compressor API. "
        "Supports images, documents, audio, video, and archives."
    ),
    version="1.0.0",
)

# ======================================================================
# CORS — allow the Vite dev server and any other origin
# ======================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose custom compression-metadata headers to the browser
    expose_headers=[
        "X-Original-Size",
        "X-Compressed-Size",
        "X-Savings-Percent",
        "X-Original-Size-Human",
        "X-Compressed-Size-Human",
    ],
)

# ======================================================================
# Routers
# ======================================================================

app.include_router(convert.router, prefix="/api")
app.include_router(compress.router, prefix="/api")

# ======================================================================
# Startup / shutdown events
# ======================================================================

@app.on_event("startup")
async def startup_event():
    """Ensure temp directories exist when the server starts."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Best-effort cleanup of temp directories on graceful shutdown."""
    for directory in (UPLOAD_DIR, OUTPUT_DIR):
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=True)
        except OSError:
            pass


# ======================================================================
# Root & utility endpoints
# ======================================================================

@app.get("/")
async def root():
    """Health-check / API information endpoint."""
    return {
        "name": "Convert API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "formats":        "GET  /api/formats",
            "convert":        "POST /api/convert",
            "convert_batch":  "POST /api/convert/batch",
            "compress":       "POST /api/compress",
            "compress_batch": "POST /api/compress/batch",
            "cleanup":        "POST /api/cleanup",
        },
    }


@app.post("/api/cleanup")
async def cleanup_temp_files():
    """Manually trigger cleanup of all temporary files.

    Useful for freeing disk space without restarting the server.
    """
    removed = 0
    for directory in (UPLOAD_DIR, OUTPUT_DIR):
        if os.path.exists(directory):
            for fname in os.listdir(directory):
                fpath = os.path.join(directory, fname)
                try:
                    os.remove(fpath)
                    removed += 1
                except OSError:
                    pass
    return {"message": f"Cleanup complete. Removed {removed} file(s)."}
