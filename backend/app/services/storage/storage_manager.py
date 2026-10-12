import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def generate_job_manifest(
    job_id: str,
    job_data: Dict[str, Any],
    clips_data: List[Dict[str, Any]],
    output_dir: Path
) -> Path:
    """Creates standardized manifest.json in the job output folder."""
    manifest_path = output_dir / "manifest.json"
    manifest = {
        "job_id": job_id,
        "title": job_data.get("title", "ClipForge Job"),
        "source_type": job_data.get("source_type"),
        "source_url": job_data.get("source_url"),
        "detected_niche": job_data.get("detected_niche"),
        "target_audience": job_data.get("target_audience"),
        "status": job_data.get("status"),
        "created_at": str(job_data.get("created_at")),
        "completed_at": str(job_data.get("completed_at")),
        "total_clips": len(clips_data),
        "clips": [
            {
                "id": c.get("id"),
                "clip_index": c.get("clip_index"),
                "title": c.get("title"),
                "hook": c.get("hook"),
                "start_time": c.get("start_time"),
                "end_time": c.get("end_time"),
                "duration": c.get("duration"),
                "aspect_ratio": c.get("aspect_ratio"),
                "viral_score": c.get("viral_score"),
                "selection_reason": c.get("selection_reason"),
                "video_file": Path(c.get("video_path")).name if c.get("video_path") else None,
                "thumbnail_file": Path(c.get("thumbnail_path")).name if c.get("thumbnail_path") else None,
                "srt_file": Path(c.get("srt_path")).name if c.get("srt_path") else None,
                "vtt_file": Path(c.get("vtt_path")).name if c.get("vtt_path") else None,
                "file_size_mb": c.get("file_size_mb", 0.0),
                "status": c.get("status")
            }
            for c in clips_data
        ]
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest_path

def get_storage_stats() -> Dict[str, Any]:
    """Calculates disk space, directory stats, and job/clip counts."""
    storage_root = settings.storage_path
    outputs_dir = settings.outputs_dir
    inputs_dir = settings.inputs_dir

    total_bytes, used_bytes, free_bytes = shutil.disk_usage(storage_root)

    total_used_mb = 0.0
    for p in storage_root.rglob("*"):
        if p.is_file():
            try:
                total_used_mb += p.stat().st_size / (1024 * 1024)
            except Exception:
                pass

    total_jobs = 0
    total_clips = 0
    try:
        from backend.app.db.session import SessionLocal
        from backend.app.models.job import Job
        from backend.app.models.clip import Clip
        db = SessionLocal()
        total_jobs = db.query(Job).count()
        total_clips = db.query(Clip).filter(Clip.status == "completed").count()
        db.close()
    except Exception:
        pass

    return {
        "storage_root": str(storage_root),
        "outputs_directory": str(outputs_dir),
        "inputs_directory": str(inputs_dir),
        "total_used_mb": round(total_used_mb, 2),
        "available_disk_gb": round(free_bytes / (1024 ** 3), 2),
        "total_disk_gb": round(total_bytes / (1024 ** 3), 2),
        "total_jobs": total_jobs,
        "total_clips": total_clips,
        "retention_days": settings.output_retention_days,
        "max_concurrent_jobs": settings.max_concurrent_jobs,
        "cpu_threads": settings.cpu_threads,
        "transcription_provider": settings.transcription_provider,
        "whisper_model": settings.whisper_model,
        "whisper_compute_type": settings.whisper_compute_type,
        "ai_provider": settings.ai_provider
    }
