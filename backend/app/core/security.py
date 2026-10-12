import re
import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Tuple
from fastapi import HTTPException, status

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
ALLOWED_MIME_TYPES = {
    "video/mp4", "video/quicktime", "video/x-matroska", "video/webm", "video/x-msvideo"
}

# Standard MP4/MOV/MKV/WebM header magic bytes
MAGIC_BYTES = {
    b"\x00\x00\x00\x18ftyp": "mp4",
    b"\x00\x00\x00\x20ftyp": "mp4",
    b"\x00\x00\x00\x1cftyp": "mp4",
    b"\x1a\x45\xdf\xa3": "mkv_or_webm",
    b"RIFF": "avi",
}

YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})"
)

def validate_youtube_url(url: str) -> str:
    """
    Validates a YouTube URL, ensures it matches allowed domains and returns the 11-char video ID.
    Blocks any internal SSRF or non-YouTube destinations.
    """
    url = url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="YouTube URL cannot be empty.")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Invalid URL scheme. Must be http or https.")

    hostname = (parsed.hostname or "").lower()
    allowed_hosts = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
    if hostname not in allowed_hosts:
        raise HTTPException(status_code=400, detail=f"Domain '{hostname}' is not a permitted YouTube host.")

    # Prevent SSRF: Resolve IP and verify not private or loopback
    try:
        ip_str = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            raise HTTPException(status_code=400, detail="Blocked internal IP address.")
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Could not resolve YouTube hostname.")

    match = YOUTUBE_REGEX.search(url)
    if not match:
        raise HTTPException(status_code=400, detail="Could not extract a valid 11-character YouTube video ID.")

    video_id = match.group(4)
    return video_id

def validate_file_extension(filename: str) -> str:
    """Verifies filename has an allowed video extension and no path traversal in filename."""
    name = Path(filename).name
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}"
        )
    return ext

def validate_magic_bytes(header: bytes) -> bool:
    """Checks initial file bytes against known video container signatures."""
    if len(header) < 12:
        return False
    # Check for ftyp tag anywhere in first 16 bytes for MP4
    if b"ftyp" in header[:16]:
        return True
    if header.startswith(b"\x1a\x45\xdf\xa3"):  # MKV / WebM
        return True
    if header.startswith(b"RIFF") and b"AVI " in header[:12]:
        return True
    return False

def safe_join(base_dir: Path, target_path: str) -> Path:
    """
    Safely joins target_path to base_dir, preventing directory traversal attacks.
    Raises HTTPException 400 if target resolves outside base_dir.
    """
    base_resolved = base_dir.resolve()
    # Strip any leading slashes/backslashes
    clean_target = target_path.lstrip("/\\")
    full_resolved = (base_resolved / clean_target).resolve()

    if not str(full_resolved).startswith(str(base_resolved)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access denied: Path traversal detected."
        )
    return full_resolved
