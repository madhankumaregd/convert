"""
Media conversion and compression service for audio and video files.

* **Audio** — handled by *pydub* (which wraps ffmpeg/avconv).
* **Video** — handled via direct *subprocess* calls to ``ffmpeg``.
"""

from __future__ import annotations

import os
import shutil
import subprocess

from pydub import AudioSegment


# ======================================================================
# FFmpeg availability check
# ======================================================================

def check_ffmpeg() -> bool:
    """Return ``True`` if ``ffmpeg`` is on the system PATH."""
    return shutil.which("ffmpeg") is not None


# ======================================================================
# Audio
# ======================================================================

# pydub format strings differ slightly from common extensions
_PYDUB_FORMAT_MAP: dict[str, str] = {
    "m4a": "mp4",   # pydub uses "mp4" for m4a container
    "wma": "wma",
}


def _pydub_format(ext: str) -> str:
    """Map a file extension to the format string pydub expects."""
    ext = ext.lower().lstrip(".")
    return _PYDUB_FORMAT_MAP.get(ext, ext)


def convert_audio(
    input_path: str,
    output_path: str,
    target_format: str,
) -> str:
    """Convert an audio file to *target_format* using pydub.

    Returns *output_path* on success.
    """
    src_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
    audio = AudioSegment.from_file(input_path, format=_pydub_format(src_ext))
    audio.export(output_path, format=_pydub_format(target_format))
    return output_path


def compress_audio(
    input_path: str,
    output_path: str,
    bitrate: str = "128k",
) -> str:
    """Re-encode an audio file at a lower bitrate to reduce size.

    The output format matches the input format.  Returns *output_path*.
    """
    src_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
    audio = AudioSegment.from_file(input_path, format=_pydub_format(src_ext))
    audio.export(output_path, format=_pydub_format(src_ext), bitrate=bitrate)
    return output_path


# ======================================================================
# Video
# ======================================================================

def convert_video(
    input_path: str,
    output_path: str,
    target_format: str,
) -> str:
    """Convert a video file to *target_format* using ffmpeg.

    Special handling:
    * **video → mp3/wav** — extracts the audio track only.
    * **video → gif** — creates an animated GIF.

    Returns *output_path* on success.

    Raises ``RuntimeError`` when ffmpeg is not installed or the
    conversion process fails.
    """
    if not check_ffmpeg():
        raise RuntimeError(
            "ffmpeg is not installed or not found on the system PATH. "
            "Please install ffmpeg to enable video conversions."
        )

    target = target_format.lower().lstrip(".")

    # Build the ffmpeg command
    cmd: list[str] = ["ffmpeg", "-y", "-i", input_path]

    if target in ("mp3", "wav"):
        # Extract audio only
        cmd += ["-vn", "-acodec"]
        if target == "mp3":
            cmd += ["libmp3lame", "-q:a", "2"]
        else:
            cmd += ["pcm_s16le"]
        cmd.append(output_path)

    elif target == "gif":
        # Create GIF — scale to max 480px width, 10 fps
        cmd += [
            "-vf", "fps=10,scale=480:-1:flags=lanczos",
            "-loop", "0",
            output_path,
        ]

    else:
        # Generic video-to-video
        cmd += ["-c:v", "libx264", "-c:a", "aac", output_path]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {result.stderr[:500]}")

    return output_path


def compress_video(
    input_path: str,
    output_path: str,
    crf: int = 28,
) -> str:
    """Compress a video file using CRF-based encoding with ffmpeg.

    A higher *crf* value means more compression (lower quality).
    Typical range is 18 (near-lossless) – 35 (very compressed).

    Returns *output_path* on success.
    """
    if not check_ffmpeg():
        raise RuntimeError(
            "ffmpeg is not installed or not found on the system PATH. "
            "Please install ffmpeg to enable video compression."
        )

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg compression failed: {result.stderr[:500]}")

    return output_path
