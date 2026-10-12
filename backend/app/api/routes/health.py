import subprocess
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
from backend.app.core.config import settings

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check():
    """Liveness probe returning application and environment status."""
    return {
        "status": "healthy",
        "service": "ClipForge AI Core API",
        "environment": settings.app_env,
        "whisper_model": settings.whisper_model,
        "max_concurrent_jobs": settings.max_concurrent_jobs
    }

@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe checking database connectivity and FFmpeg availability."""
    # 1. Database check
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

    # 2. FFmpeg check
    try:
        res = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            raise Exception("FFmpeg command returned non-zero status.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"FFmpeg binary unavailable: {str(e)}"
        )

    return {
        "status": "ready",
        "database": "connected",
        "ffmpeg": "available"
    }
