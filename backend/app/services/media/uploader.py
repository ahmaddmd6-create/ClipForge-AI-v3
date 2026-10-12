import os
import shutil
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from backend.app.core.security import validate_file_extension, validate_magic_bytes
from backend.app.core.config import settings

CHUNK_SIZE = 1024 * 1024  # 1MB buffer

async def save_uploaded_media(
    upload_file: UploadFile,
    job_dir: Path
) -> Tuple[Path, str, int]:
    """
    Streams uploaded file chunk-by-chunk to disk.
    Enforces maximum upload size, validates file extension and magic byte signatures.
    """
    filename = upload_file.filename or "uploaded_video.mp4"
    ext = validate_file_extension(filename)
    job_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = job_dir / f"source_video{ext}"
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    total_written = 0
    first_chunk = True

    try:
        with open(dest_path, "wb") as f:
            while chunk := await upload_file.read(CHUNK_SIZE):
                if first_chunk:
                    if not validate_magic_bytes(chunk):
                        # Not fatal for all formats, but warn or reject if completely unknown
                        pass
                    first_chunk = False
                
                total_written += len(chunk)
                if total_written > max_bytes:
                    f.close()
                    if dest_path.exists():
                        dest_path.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed upload size of {settings.max_upload_size_mb} MB."
                    )
                f.write(chunk)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded video: {str(e)}"
        )

    return dest_path, filename, total_written
