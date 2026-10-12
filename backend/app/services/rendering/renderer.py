import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.services.rendering.subtitles import generate_subtitle_files
from backend.app.services.media.inspector import inspect_media_file, MediaInspectionError

logger = logging.getLogger(__name__)

class RenderError(Exception):
    pass

def render_clip_video(
    source_video_path: Path,
    output_dir: Path,
    clip_id: str,
    clip_index: int,
    start_time: float,
    end_time: float,
    aspect_ratio: str = "9:16",
    subtitle_style: str = "hormozi_yellow",
    burn_subtitles: bool = True,
    clip_segments: Optional[list] = None
) -> Dict[str, Any]:
    """
    Renders an individual clip using FFmpeg.
    Enforces minimum 60-second duration and validates rendered MP4 with ffprobe.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    duration = end_time - start_time
    if duration < 60.0:
        raise RenderError(f"Requested duration {duration:.1f}s is less than mandatory 60.0s minimum.")

    base_name = f"clip_{clip_index:02d}"
    out_video_path = output_dir / f"{base_name}.mp4"
    out_thumb_path = output_dir / f"{base_name}.jpg"
    sub_base_path = output_dir / base_name

    # Step 1: Generate subtitle files (ASS, SRT, VTT)
    sub_paths = generate_subtitle_files(
        clip_segments=clip_segments or [],
        clip_start_time=start_time,
        base_output_path=sub_base_path,
        style_name=subtitle_style
    )

    # Windows-safe path escaping for libass filtergraph in FFmpeg
    # Replace backslashes with forward slashes and escape colon
    escaped_ass_path = str(sub_paths["ass"].resolve()).replace("\\", "/").replace(":", "\\:")

    # Step 2: Build FFmpeg filtergraph depending on aspect ratio
    if aspect_ratio == "9:16":
        # 1080x1920 with blurred background and centered foreground
        if burn_subtitles and sub_paths["ass"].exists():
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
                f"[0:v]scale=1080:-2[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2,"
                f"subtitles='{escaped_ass_path}'[outv]"
            )
        else:
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
                f"[0:v]scale=1080:-2[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2[outv]"
            )
    elif aspect_ratio == "1:1":
        # 1080x1080 square
        if burn_subtitles and sub_paths["ass"].exists():
            filter_complex = (
                f"[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,boxblur=20:5[bg];"
                f"[0:v]scale=1080:-2[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2,"
                f"subtitles='{escaped_ass_path}'[outv]"
            )
        else:
            filter_complex = (
                f"[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080[outv]"
            )
    else:
        # 16:9 Landscape
        if burn_subtitles and sub_paths["ass"].exists():
            filter_complex = f"[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,subtitles='{escaped_ass_path}'[outv]"
        else:
            filter_complex = f"[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[outv]"

    # Assemble FFmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-i", str(source_video_path.resolve()),
        "-t", str(duration),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(out_video_path.resolve())
    ]

    logger.info(f"Rendering Clip {clip_index} from {start_time:.1f}s to {end_time:.1f}s ({duration:.1f}s)...")
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    if res.returncode != 0:
        logger.warning(f"Render failed with subtitle filter: {res.stderr[:200]}. Attempting fallback without burned subtitles...")
        # Fallback without subtitle filter
        if aspect_ratio == "9:16":
            fb_filter = (
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
                "[0:v]scale=1080:-2[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2[outv]"
            )
        else:
            fb_filter = "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[outv]"

        cmd_fb = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", str(source_video_path.resolve()),
            "-t", str(duration),
            "-filter_complex", fb_filter,
            "-map", "[outv]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_video_path.resolve())
        ]
        res_fb = subprocess.run(cmd_fb, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res_fb.returncode != 0:
            raise RenderError(f"FFmpeg rendering failed: {res_fb.stderr.strip()[:300]}")

    # Step 3: Extract thumbnail at 2.0s mark
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "2.0",
        "-i", str(out_video_path.resolve()),
        "-vframes", "1",
        "-q:v", "2",
        str(out_thumb_path.resolve())
    ]
    subprocess.run(thumb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 4: Validate rendered output with FFprobe
    try:
        probe_meta = inspect_media_file(out_video_path)
    except MediaInspectionError as e:
        raise RenderError(f"Render validation failed: output file is not readable by FFprobe ({e})")

    if probe_meta["file_size_bytes"] <= 0:
        raise RenderError("Render validation failed: output file is empty (0 bytes).")

    actual_duration = probe_meta["duration_seconds"]
    if actual_duration < 59.0:  # Allow 1s tolerance for container frame timing
        raise RenderError(f"Render validation failed: final video duration ({actual_duration:.1f}s) is shorter than 60.0s requirement.")

    file_size_mb = round(probe_meta["file_size_bytes"] / (1024 * 1024), 2)

    return {
        "video_path": str(out_video_path),
        "video_filename": out_video_path.name,
        "thumbnail_path": str(out_thumb_path) if out_thumb_path.exists() else None,
        "thumbnail_filename": out_thumb_path.name if out_thumb_path.exists() else None,
        "srt_path": str(sub_paths["srt"]),
        "vtt_path": str(sub_paths["vtt"]),
        "duration": actual_duration,
        "file_size_mb": file_size_mb
    }
