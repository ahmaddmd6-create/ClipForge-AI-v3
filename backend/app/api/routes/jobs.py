import uuid
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.job import Job
from backend.app.models.clip import Clip
from backend.app.models.source_asset import SourceAsset
from backend.app.schemas.job import JobCreate, JobResponse, JobUpdate
from backend.app.core.security import validate_youtube_url, validate_file_extension
from backend.app.core.config import settings
from backend.app.services.media.uploader import save_uploaded_media
from backend.app.workers.queue import enqueue_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    youtube_url: Optional[str] = Form(None),
    source_type: str = Form("youtube"),
    rights_declared: bool = Form(True),
    target_clip_count: int = Form(5),
    min_duration: float = Form(60.0),
    target_duration: float = Form(75.0),
    max_duration: float = Form(90.0),
    aspect_ratio: str = Form("9:16"),
    subtitle_style: str = Form("hormozi_yellow"),
    burn_subtitles: bool = Form(True),
    background_music: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Creates a new clipping job from either a YouTube URL or an uploaded video file.
    Validates source access declaration, enforce hard 60s minimum clip duration.
    """
    if not rights_declared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source authorization confirmation is required. You must verify permission to process this content."
        )

    if min_duration < 60.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum clip duration must be at least 60.0 seconds."
        )

    job_id = f"job_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    job_input_dir = settings.inputs_dir / job_id
    job_input_dir.mkdir(parents=True, exist_ok=True)

    title = "Untitled Clipping Job"
    source_filename = None

    if source_type == "youtube":
        if not youtube_url:
            raise HTTPException(status_code=400, detail="YouTube URL is required when source_type is 'youtube'.")
        # Validate YouTube URL against SSRF and allowed hosts
        validate_youtube_url(youtube_url)
        title = f"YouTube Video ({youtube_url.split('v=')[-1][:11]})"
    elif source_type == "upload":
        if not file:
            raise HTTPException(status_code=400, detail="A video file must be provided when source_type is 'upload'.")
        dest_path, original_name, file_size = await save_uploaded_media(file, job_input_dir)
        source_filename = original_name
        title = Path(original_name).stem.replace("_", " ").title()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source_type: {source_type}")

    new_job = Job(
        id=job_id,
        title=title,
        source_type=source_type,
        source_url=youtube_url,
        source_filename=source_filename,
        status="queued",
        stage="queued",
        progress=0,
        status_message="Job queued for processing...",
        target_clip_count=target_clip_count,
        min_duration=max(60.0, min_duration),
        target_duration=target_duration,
        max_duration=max_duration,
        aspect_ratio=aspect_ratio,
        subtitle_style=subtitle_style,
        burn_subtitles=burn_subtitles,
        background_music=background_music,
        rights_declared=rights_declared
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Dispatch to background queue
    enqueue_job(job_id)

    return new_job

@router.get("", response_model=List[JobResponse])
def list_jobs(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Returns list of jobs with optional status filter, sorted by created_at desc."""
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    """Retrieves full details of a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@router.post("/{job_id}/retry", response_model=JobResponse)
def retry_job(job_id: str, db: Session = Depends(get_db)):
    """Retries a failed or cancelled job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    job.status = "queued"
    job.stage = "queued"
    job.progress = 0
    job.status_message = "Job queued for retry..."
    job.error_detail = None
    db.commit()
    db.refresh(job)

    enqueue_job(job_id)
    return job

@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """Cancels a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.status in ("completed", "failed"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a job that is already {job.status}.")

    job.status = "cancelled"
    job.stage = "cancelled"
    job.status_message = "Job cancelled by user."
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Deletes job and cleans up associated output files."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Remove files
    job_out = settings.outputs_dir / job_id
    if job_out.exists():
        import shutil
        shutil.rmtree(job_out, ignore_errors=True)
    job_in = settings.inputs_dir / job_id
    if job_in.exists():
        import shutil
        shutil.rmtree(job_in, ignore_errors=True)

    db.delete(job)
    db.commit()
    return None
