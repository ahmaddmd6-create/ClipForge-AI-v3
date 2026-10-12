import os
import mimetypes
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.clip import Clip
from backend.app.schemas.clip import ClipDetailResponse, ClipUpdate
from backend.app.core.security import safe_join
from backend.app.core.config import settings

router = APIRouter(prefix="/api/clips", tags=["Clips"])

def format_clip_response(clip: Clip, request: Request) -> dict:
    base_url = str(request.base_url).rstrip("/")
    return {
        "id": clip.id,
        "job_id": clip.job_id,
        "clip_index": clip.clip_index,
        "title": clip.title,
        "hook": clip.hook,
        "transcript_excerpt": clip.transcript_excerpt,
        "start_time": clip.start_time,
        "end_time": clip.end_time,
        "duration": clip.duration,
        "aspect_ratio": clip.aspect_ratio,
        "viral_score": clip.viral_score,
        "selection_reason": clip.selection_reason,
        "status": clip.status,
        "video_path": clip.video_path,
        "video_url": f"{base_url}/api/clips/{clip.id}/download" if clip.video_path else None,
        "thumbnail_path": clip.thumbnail_path,
        "thumbnail_url": f"{base_url}/api/clips/{clip.id}/thumbnail" if clip.thumbnail_path else None,
        "srt_url": f"{base_url}/api/clips/{clip.id}/captions?format=srt" if clip.srt_path else None,
        "vtt_url": f"{base_url}/api/clips/{clip.id}/captions?format=vtt" if clip.vtt_path else None,
        "file_size_mb": clip.file_size_mb,
        "error_message": clip.error_message,
        "created_at": clip.created_at,
        "updated_at": clip.updated_at
    }

@router.get("", response_model=List[ClipDetailResponse])
def list_clips(
    job_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Lists clips with optional job_id and status filters."""
    query = db.query(Clip)
    if job_id:
        query = query.filter(Clip.job_id == job_id)
    if status:
        query = query.filter(Clip.status == status)
    clips = query.order_by(Clip.created_at.desc(), Clip.clip_index.asc()).offset(skip).limit(limit).all()
    return [format_clip_response(c, request) for c in clips]

@router.get("/{clip_id}", response_model=ClipDetailResponse)
def get_clip(clip_id: str, request: Request, db: Session = Depends(get_db)):
    """Retrieves a single clip with full metadata and streaming URLs."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found.")
    return format_clip_response(clip, request)

@router.patch("/{clip_id}", response_model=ClipDetailResponse)
def update_clip(clip_id: str, payload: ClipUpdate, request: Request, db: Session = Depends(get_db)):
    """Allows updating clip title and timestamps with duration >= 60s validation."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found.")

    if payload.title is not None:
        clip.title = payload.title.strip()
    if payload.aspect_ratio is not None:
        clip.aspect_ratio = payload.aspect_ratio

    new_st = payload.start_time if payload.start_time is not None else clip.start_time
    new_et = payload.end_time if payload.end_time is not None else clip.end_time

    if new_st >= new_et:
        raise HTTPException(status_code=400, detail="start_time must be strictly less than end_time.")
    if (new_et - new_st) < 60.0:
        raise HTTPException(status_code=400, detail="Clip duration must be at least 60.0 seconds.")

    clip.start_time = round(new_st, 2)
    clip.end_time = round(new_et, 2)
    clip.duration = round(new_et - new_st, 1)

    db.commit()
    db.refresh(clip)
    return format_clip_response(clip, request)

@router.get("/{clip_id}/download")
def download_clip_video(clip_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Streams the rendered MP4 video file with support for HTTP Range requests
    (essential for video seeking in modern web video players).
    """
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip or not clip.video_path:
        raise HTTPException(status_code=404, detail="Video file for this clip does not exist.")

    video_path = Path(clip.video_path)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found on disk.")

    file_size = video_path.stat().st_size
    range_header = request.headers.get("range")

    if not range_header:
        return FileResponse(
            str(video_path),
            media_type="video/mp4",
            filename=video_path.name
        )

    # Range parsing
    range_match = range_header.strip().replace("bytes=", "").split("-")
    start = int(range_match[0]) if range_match[0] else 0
    end = int(range_match[1]) if range_match[1] else file_size - 1
    length = end - start + 1

    def iter_file():
        with open(video_path, "rb") as f:
            f.seek(start)
            bytes_left = length
            while bytes_left > 0:
                chunk_size = min(bytes_left, 64 * 1024)
                data = f.read(chunk_size)
                if not data:
                    break
                bytes_left -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "Content-Disposition": f'inline; filename="{video_path.name}"'
    }
    return StreamingResponse(iter_file(), status_code=206, headers=headers, media_type="video/mp4")

@router.get("/{clip_id}/thumbnail")
def get_clip_thumbnail(clip_id: str, db: Session = Depends(get_db)):
    """Serves the generated thumbnail image."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip or not clip.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not available.")

    thumb_path = Path(clip.thumbnail_path)
    if not thumb_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found.")

    return FileResponse(str(thumb_path), media_type="image/jpeg")

@router.get("/{clip_id}/captions")
def get_clip_captions(
    clip_id: str,
    format: str = Query("vtt", pattern="^(vtt|srt)$"),
    db: Session = Depends(get_db)
):
    """Downloads or streams subtitles in VTT or SRT format."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found.")

    target_path = clip.vtt_path if format == "vtt" else clip.srt_path
    if not target_path or not Path(target_path).exists():
        raise HTTPException(status_code=404, detail=f"{format.upper()} subtitle file not available.")

    p = Path(target_path)
    media_type = "text/vtt" if format == "vtt" else "application/x-subrip"
    return FileResponse(str(p), media_type=media_type, filename=p.name)

@router.delete("/{clip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clip(clip_id: str, db: Session = Depends(get_db)):
    """Deletes a single clip and associated media files."""
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found.")

    for path_str in [clip.video_path, clip.thumbnail_path, clip.srt_path, clip.vtt_path]:
        if path_str and Path(path_str).exists():
            try:
                Path(path_str).unlink()
            except Exception:
                pass

    db.delete(clip)
    db.commit()
    return None
