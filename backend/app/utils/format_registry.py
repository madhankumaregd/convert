"""
Format Registry — the single source of truth for every supported file
format, its category, and which target formats it can be converted to.

The frontend fetches this registry via GET /api/formats so its UI is
always in sync with backend capabilities.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Complete format mapping
# ---------------------------------------------------------------------------
FORMAT_CATEGORIES: dict[str, dict] = {
    "image": {
        "extensions": [
            "jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "gif", "ico", "svg",
        ],
        "targets": {
            "jpg":  ["png", "webp", "bmp", "tiff", "gif", "ico", "pdf"],
            "jpeg": ["png", "webp", "bmp", "tiff", "gif", "ico", "pdf"],
            "png":  ["jpg", "webp", "bmp", "tiff", "gif", "ico", "pdf"],
            "webp": ["jpg", "png", "bmp", "tiff", "gif", "ico", "pdf"],
            "bmp":  ["jpg", "png", "webp", "tiff", "gif", "ico", "pdf"],
            "tiff": ["jpg", "png", "webp", "bmp", "gif", "ico", "pdf"],
            "tif":  ["jpg", "png", "webp", "bmp", "gif", "ico", "pdf"],
            "gif":  ["jpg", "png", "webp", "bmp", "tiff", "ico"],
            "ico":  ["jpg", "png", "webp", "bmp"],
            "svg":  ["png", "jpg", "webp", "pdf"],
        },
    },
    "document": {
        "extensions": ["pdf", "docx", "txt", "xlsx", "csv"],
        "targets": {
            "pdf":  ["docx", "txt"],
            "docx": ["pdf", "txt"],
            "txt":  ["pdf", "docx"],
            "xlsx": ["csv", "pdf"],
            "csv":  ["xlsx", "pdf"],
        },
    },
    "audio": {
        "extensions": ["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a"],
        "targets": {
            "mp3":  ["wav", "ogg", "flac", "aac", "m4a"],
            "wav":  ["mp3", "ogg", "flac", "aac", "m4a"],
            "ogg":  ["mp3", "wav", "flac", "aac", "m4a"],
            "flac": ["mp3", "wav", "ogg", "aac", "m4a"],
            "aac":  ["mp3", "wav", "ogg", "flac", "m4a"],
            "wma":  ["mp3", "wav", "ogg", "flac", "aac"],
            "m4a":  ["mp3", "wav", "ogg", "flac", "aac"],
        },
    },
    "video": {
        "extensions": ["mp4", "mkv", "avi", "webm", "mov", "flv", "wmv"],
        "targets": {
            "mp4":  ["mkv", "avi", "webm", "mov", "mp3", "wav", "gif"],
            "mkv":  ["mp4", "avi", "webm", "mov", "mp3", "wav"],
            "avi":  ["mp4", "mkv", "webm", "mov", "mp3", "wav"],
            "webm": ["mp4", "mkv", "avi", "mov", "mp3", "wav"],
            "mov":  ["mp4", "mkv", "avi", "webm", "mp3", "wav"],
            "flv":  ["mp4", "mkv", "avi", "webm", "mov"],
            "wmv":  ["mp4", "mkv", "avi", "webm", "mov"],
        },
    },
    "archive": {
        "extensions": ["zip", "tar", "gz", "bz2", "7z", "rar"],
        "targets": {
            "zip": ["tar", "gz", "bz2"],
            "tar": ["zip", "gz", "bz2"],
            "gz":  ["zip", "tar"],
            "bz2": ["zip", "tar"],
            "7z":  ["zip", "tar"],
            "rar": ["zip", "tar"],
        },
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_category(extension: str) -> str | None:
    """Return the category name ('image', 'document', …) for a file
    extension, or ``None`` if the extension is not recognised."""
    ext = extension.lower().lstrip(".")
    for category, info in FORMAT_CATEGORIES.items():
        if ext in info["extensions"]:
            return category
    return None


def get_valid_targets(extension: str) -> list[str]:
    """Return the list of formats that *extension* can be converted to.
    Returns an empty list when the extension is unknown."""
    ext = extension.lower().lstrip(".")
    for info in FORMAT_CATEGORIES.values():
        if ext in info["targets"]:
            return info["targets"][ext]
    return []


def get_all_formats() -> dict:
    """Return the entire ``FORMAT_CATEGORIES`` dictionary.
    Used by the ``GET /api/formats`` endpoint."""
    return FORMAT_CATEGORIES


def is_valid_conversion(source_ext: str, target_ext: str) -> bool:
    """Check whether converting from *source_ext* to *target_ext* is a
    supported operation."""
    src = source_ext.lower().lstrip(".")
    tgt = target_ext.lower().lstrip(".")
    return tgt in get_valid_targets(src)
