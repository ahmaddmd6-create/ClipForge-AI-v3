import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Callable
import yt_dlp
from backend.app.core.security import validate_youtube_url

logger = logging.getLogger(__name__)

class DownloadError(Exception):
    pass

def fetch_youtube_metadata(url: str) -> Dict[str, Any]:
    """Retrieves metadata only without downloading full video payload."""
    validate_youtube_url(url)
    ydl_opts = {
        'skip_download': True,
        'extract_flat': False,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 15,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "id": info.get("id"),
                "title": info.get("title", "YouTube Video"),
                "duration": float(info.get("duration", 0)),
                "uploader": info.get("uploader", "Creator"),
                "description": (info.get("description") or "")[:800],
                "thumbnail": info.get("thumbnail"),
                "view_count": info.get("view_count", 0),
                "tags": info.get("tags", [])
            }
    except yt_dlp.utils.DownloadError as e:
        err = str(e)
        if "Private video" in err or "Sign in" in err:
            raise DownloadError("The YouTube video is private or requires authentication. Please upload the local video file instead.")
        if "members-only" in err:
            raise DownloadError("This video is members-only and cannot be processed via URL. Please upload the video file directly.")
        raise DownloadError(f"Could not retrieve YouTube video metadata: {err}")
    except Exception as e:
        raise DownloadError(f"Error inspecting YouTube source: {str(e)}")

def download_youtube_source(
    url: str,
    target_dir: Path,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Tuple[Path, Optional[Path], Dict[str, Any]]:
    """
    Downloads YouTube video in MP4 container (720p/1080p).
    If official/automatic captions are present, extracts them; otherwise Whisper handles transcription.
    """
    validate_youtube_url(url)
    target_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(target_dir / "source_video.%(ext)s")

    def _hook(d):
        if progress_callback and d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            downloaded = d.get('downloaded_bytes', 0)
            pct = int((downloaded / total) * 100)
            progress_callback(pct, f"Downloading video stream: {pct}%")

    base_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best/18',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 45,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web_creator', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'progress_hooks': [_hook],
    }

    # Clean up any leftover temp files in target_dir to prevent WinError 183 on Windows
    for old_file in target_dir.glob("source_video.temp.*"):
        try:
            old_file.unlink(missing_ok=True)
        except Exception:
            pass

    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/18/best',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'overwrites': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 60,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'progress_hooks': [_hook],
    }

    info = None
    try:
        if progress_callback:
            progress_callback(5, "Acquiring authorized YouTube stream...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        logger.warning(f"Initial yt-dlp attempt failed: {e}. Retrying with android format 18...")
        for old_file in target_dir.glob("source_video.*"):
            try:
                old_file.unlink(missing_ok=True)
            except Exception:
                pass
        fallback_opts = {
            **ydl_opts,
            'overwrites': True,
            'format': '18/best[height<=720]/best',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
        try:
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as fallback_err:
            raise DownloadError(
                f"Unable to download YouTube video: {str(fallback_err)}. "
                "The source may be geo-restricted or rate-limited. Please use local video upload."
            )

    meta = {
        "id": info.get("id"),
        "title": info.get("title", "YouTube Source"),
        "duration": float(info.get("duration", 0)),
        "uploader": info.get("uploader", "Creator"),
        "thumbnail": info.get("thumbnail"),
        "description": (info.get("description") or "")[:500],
        "tags": info.get("tags", [])
    }

    # Locate downloaded video
    video_path = target_dir / "source_video.mp4"
    if not video_path.exists():
        candidates = [c for c in target_dir.glob("source_video.*") if c.suffix.lower() in [".mp4", ".mkv", ".webm"]]
        if candidates:
            video_path = candidates[0]
        else:
            raise DownloadError("Download finished but source video file could not be located on disk.")

    # Locate subtitle file if available
    sub_candidates = list(target_dir.glob("source_video.*.vtt")) + list(target_dir.glob("source_video.*.srt"))
    subtitle_path = sub_candidates[0] if sub_candidates else None

    return video_path, subtitle_path, meta
