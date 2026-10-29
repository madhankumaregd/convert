"""
Configuration settings for the Convert application.

Defines upload/output directories, file size limits, and ensures
required directories exist at import time.
"""

import os
import tempfile

# ---------------------------------------------------------------------------
# Directory configuration – all temp files live under a shared root inside
# the OS temp directory so they are automatically cleaned on reboot.
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.join(tempfile.gettempdir(), "convert_app")

UPLOAD_DIR: str = os.path.join(_BASE_DIR, "uploads")
OUTPUT_DIR: str = os.path.join(_BASE_DIR, "outputs")

# Maximum upload size in bytes (500 MB)
MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 524 288 000 bytes

# ---------------------------------------------------------------------------
# Ensure directories exist on first import
# ---------------------------------------------------------------------------
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
