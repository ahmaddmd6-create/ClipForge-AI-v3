import pytest
from pathlib import Path
from fastapi import HTTPException
from backend.app.core.security import (
    validate_youtube_url,
    validate_file_extension,
    validate_magic_bytes,
    safe_join
)

def test_validate_youtube_url_valid():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    vid_id = validate_youtube_url(url)
    assert vid_id == "dQw4w9WgXcQ"

    short_url = "https://youtu.be/dQw4w9WgXcQ"
    assert validate_youtube_url(short_url) == "dQw4w9WgXcQ"

def test_validate_youtube_url_rejects_ssrf_and_invalid():
    with pytest.raises(HTTPException):
        validate_youtube_url("https://malicious-site.com/video")

    with pytest.raises(HTTPException):
        validate_youtube_url("http://127.0.0.1:8000/api")

    with pytest.raises(HTTPException):
        validate_youtube_url("file:///etc/passwd")

def test_validate_file_extension():
    assert validate_file_extension("sample.mp4") == ".mp4"
    assert validate_file_extension("video.mkv") == ".mkv"
    assert validate_file_extension("clip.webm") == ".webm"

    with pytest.raises(HTTPException):
        validate_file_extension("exploit.exe")

    with pytest.raises(HTTPException):
        validate_file_extension("script.sh")

def test_safe_join_prevents_directory_traversal():
    base = Path("/app/storage")
    joined = safe_join(base, "outputs/job_123/clip_01.mp4")
    assert str(joined).startswith(str(base.resolve()))

    with pytest.raises(HTTPException):
        safe_join(base, "../../etc/passwd")

    with pytest.raises(HTTPException):
        safe_join(base, "outputs/../../../secret")
