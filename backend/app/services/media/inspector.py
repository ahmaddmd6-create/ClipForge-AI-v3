import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MediaInspectionError(Exception):
    pass

def inspect_media_file(file_path: Path) -> Dict[str, Any]:
    """
    Executes ffprobe safely to extract container and stream metadata.
    Validates existence, readable streams, duration, and audio presence.
    """
    if not file_path.exists():
        raise MediaInspectionError(f"File not found: {file_path}")

    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(file_path.resolve())
    ]

    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
    except subprocess.TimeoutExpired:
        raise MediaInspectionError("FFprobe inspection timed out after 30 seconds.")
    except Exception as e:
        raise MediaInspectionError(f"Failed to execute FFprobe: {str(e)}")

    if res.returncode != 0:
        raise MediaInspectionError(f"FFprobe failed to inspect media: {res.stderr.strip() or 'Unknown error'}")

    try:
        info = json.loads(res.stdout)
    except Exception as e:
        raise MediaInspectionError(f"Failed to parse FFprobe JSON output: {str(e)}")

    format_info = info.get("format", {})
    streams = info.get("streams", [])

    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    if not video_streams:
        raise MediaInspectionError("No valid video stream found in the source file.")

    primary_video = video_streams[0]
    has_audio = len(audio_streams) > 0
    audio_codec = audio_streams[0].get("codec_name", "unknown") if has_audio else "none"

    # Compute duration
    duration = 0.0
    if "duration" in format_info:
        try:
            duration = float(format_info["duration"])
        except (ValueError, TypeError):
            pass
    if duration <= 0 and "duration" in primary_video:
        try:
            duration = float(primary_video["duration"])
        except (ValueError, TypeError):
            pass

    width = int(primary_video.get("width", 0))
    height = int(primary_video.get("height", 0))

    # Frame rate
    r_frame_rate = primary_video.get("r_frame_rate", "30/1")
    fps = 30.0
    if "/" in r_frame_rate:
        num, den = r_frame_rate.split("/")
        try:
            den_f = float(den)
            if den_f > 0:
                fps = round(float(num) / den_f, 2)
        except (ValueError, ZeroDivisionError):
            fps = 30.0

    # Rotation from side data or tags
    rotation = 0
    for side_data in primary_video.get("side_data_list", []):
        if "rotation" in side_data:
            rotation = int(side_data["rotation"])
    if rotation == 0:
        tags = primary_video.get("tags", {})
        if "rotate" in tags:
            try:
                rotation = int(tags["rotate"])
            except (ValueError, TypeError):
                rotation = 0

    return {
        "duration_seconds": round(duration, 2),
        "width": width,
        "height": height,
        "aspect_ratio": f"{width}:{height}" if width and height else "unknown",
        "frame_rate": fps,
        "video_codec": primary_video.get("codec_name", "unknown"),
        "audio_codec": audio_codec,
        "has_audio": has_audio,
        "rotation": rotation,
        "file_size_bytes": file_path.stat().st_size,
        "bit_rate": int(format_info.get("bit_rate", 0))
    }
