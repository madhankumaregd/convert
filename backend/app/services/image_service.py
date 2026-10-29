"""
Image conversion and compression service.

Uses Pillow for all raster image operations including format conversion,
RGBA → RGB handling for JPEG, and quality-based compression.
"""

from __future__ import annotations

from PIL import Image


# Mapping from common file extensions to Pillow format identifiers
_PILLOW_FORMAT_MAP: dict[str, str] = {
    "jpg":  "JPEG",
    "jpeg": "JPEG",
    "png":  "PNG",
    "webp": "WEBP",
    "bmp":  "BMP",
    "tiff": "TIFF",
    "tif":  "TIFF",
    "gif":  "GIF",
    "ico":  "ICO",
    "pdf":  "PDF",
}


def _get_pillow_format(ext: str) -> str:
    """Resolve a file extension to its Pillow format string."""
    return _PILLOW_FORMAT_MAP.get(ext.lower().lstrip("."), ext.upper())


def convert_image(input_path: str, output_path: str, target_format: str) -> str:
    """Convert an image file to *target_format* and save to *output_path*.

    Handles special cases:
    * RGBA images converted to JPEG are first flattened to RGB (white bg).
    * ICO output is resized to 256×256 if larger.

    Returns the *output_path* on success.
    """
    img = Image.open(input_path)
    pil_fmt = _get_pillow_format(target_format)
    target_lower = target_format.lower().lstrip(".")

    # --- RGBA → RGB for formats that don't support alpha ----------------
    if img.mode in ("RGBA", "LA", "P") and target_lower in ("jpg", "jpeg", "bmp", "pdf"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
        img = background
    elif img.mode not in ("RGB", "L") and target_lower in ("jpg", "jpeg"):
        img = img.convert("RGB")

    # --- ICO requires constrained sizes ----------------------------------
    if target_lower == "ico":
        max_ico = 256
        if img.width > max_ico or img.height > max_ico:
            img.thumbnail((max_ico, max_ico), Image.LANCZOS)

    # --- Save with format-appropriate options ----------------------------
    save_kwargs: dict = {"format": pil_fmt}
    if target_lower in ("jpg", "jpeg"):
        save_kwargs["quality"] = 95
    elif target_lower == "webp":
        save_kwargs["quality"] = 90
    elif target_lower == "png":
        save_kwargs["optimize"] = True

    img.save(output_path, **save_kwargs)
    return output_path


def compress_image(
    input_path: str,
    output_path: str,
    quality: int = 85,
) -> str:
    """Compress an image to *output_path* using the given *quality*.

    * **JPEG / WEBP** — uses the ``quality`` parameter directly.
    * **PNG** — uses ``optimize=True`` (quality param is ignored by PNG).
    * **Other formats** — saved as-is with optimisation where supported.

    Returns the *output_path* on success.
    """
    img = Image.open(input_path)
    original_format = img.format or "PNG"

    save_kwargs: dict = {"format": original_format}

    if original_format in ("JPEG", "JPG"):
        # Ensure RGB mode for JPEG output
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            img = background
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif original_format == "PNG":
        save_kwargs["optimize"] = True
    elif original_format == "WEBP":
        save_kwargs["quality"] = quality
    else:
        # Fallback – just re-save; many formats don't support quality kwarg
        pass

    img.save(output_path, **save_kwargs)
    return output_path
