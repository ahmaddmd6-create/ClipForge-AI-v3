import os
import time
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.app.core.config import settings
from backend.app.db.session import SessionLocal, init_db
from backend.app.models.job import Job
from backend.app.models.source_asset import SourceAsset
from backend.app.models.clip import Clip
from backend.app.models.transcript import TranscriptSegment
from backend.app.models.rendering import RenderingAttempt
from backend.app.services.media.inspector import inspect_media_file
from backend.app.services.media.downloader import download_youtube_source
from backend.app.services.transcription.whisper_engine import transcribe_media
from backend.app.services.niche_detection.niche_analyzer import analyze_content_niche
from backend.app.services.clip_selection.selector import find_candidate_clips
from backend.app.services.rendering.renderer import render_clip_video
from backend.app.services.storage.storage_manager import generate_job_manifest

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("clipforge.worker")

def recover_stale_jobs():
    """Detects and marks any jobs interrupted by container/server restarts as failed."""
    db = SessionLocal()
    try:
        stale_jobs = db.query(Job).filter(Job.status.in_(["analyzing", "clipping", "rendering"])).all()
        for j in stale_jobs:
            logger.warning(f"Recovering interrupted job {j.id} from prior session.")
            j.status = "failed"
            j.status_message = "Processing interrupted by worker restart. You may safely retry."
            j.error_detail = "Worker restarted during processing."
        db.commit()
    except Exception as e:
        logger.error(f"Error during stale job recovery: {e}")
    finally:
        db.close()

def process_job(job_id: str):
    """
    Executes the complete end-to-end video processing pipeline for a given job.
    Durable transitions: queued -> analyzing -> clipping -> rendering -> completed
    """
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        logger.error(f"Job {job_id} not found in database.")
        db.close()
        return

    job_output_dir = settings.outputs_dir / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)
    job_input_dir = settings.inputs_dir / job_id
    job_input_dir.mkdir(parents=True, exist_ok=True)

    def update_job_status(pct: int, msg: str, stage: str = None, status: str = None):
        job.progress = pct
        job.status_message = msg
        if stage:
            job.stage = stage
        if status:
            job.status = status
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

    try:
        # Step 1: Intake & Media Acquisition
        source_video_path: Path = None
        subtitle_path: Optional[Path] = None

        if job.source_type == "youtube":
            update_job_status(5, "Acquiring authorized YouTube streams...", stage="downloading", status="analyzing")
            source_video_path, subtitle_path, meta = download_youtube_source(
                url=job.source_url,
                target_dir=job_input_dir,
                progress_callback=lambda p, msg: update_job_status(5 + int(p * 0.15), msg)
            )
            if not job.title or job.title == "Untitled Clipping Job":
                job.title = meta.get("title", job.title)
        else:
            update_job_status(10, "Locating uploaded source file...", stage="intake", status="analyzing")
            candidates = list(job_input_dir.glob("source_video.*"))
            if not candidates:
                raise FileNotFoundError(f"Uploaded source video not found in {job_input_dir}")
            source_video_path = candidates[0]

        # Step 2: Media Inspection via FFprobe
        update_job_status(22, "Inspecting audio/video stream parameters with FFprobe...", stage="inspecting")
        media_info = inspect_media_file(source_video_path)

        # Save or update SourceAsset
        source_asset = db.query(SourceAsset).filter(SourceAsset.job_id == job.id).first()
        if not source_asset:
            source_asset = SourceAsset(
                id=f"asset_{uuid.uuid4().hex[:12]}",
                job_id=job.id,
                file_path=str(source_video_path),
                file_size_bytes=media_info["file_size_bytes"],
                duration_seconds=media_info["duration_seconds"],
                width=media_info["width"],
                height=media_info["height"],
                frame_rate=media_info["frame_rate"],
                video_codec=media_info["video_codec"],
                audio_codec=media_info["audio_codec"],
                has_audio=media_info["has_audio"],
                rotation=media_info["rotation"]
            )
            db.add(source_asset)
            db.commit()

        if not media_info["has_audio"]:
            raise ValueError("The source video does not contain an audio track for speech recognition.")

        # Step 3: Transcription
        update_job_status(30, "Extracting audio and generating timestamped speech transcript...", stage="transcribing")
        transcript_cache = job_input_dir / "transcript.json"
        segments = transcribe_media(
            video_path=source_video_path,
            subtitle_path=subtitle_path,
            cache_path=transcript_cache,
            progress_callback=lambda p, msg: update_job_status(30 + int(p * 0.2), msg)
        )

        if not segments:
            raise ValueError("No speech or dialogue detected in the source video.")

        # Persist transcript segments in DB
        db.query(TranscriptSegment).filter(TranscriptSegment.job_id == job.id).delete()
        for idx, seg in enumerate(segments):
            t_seg = TranscriptSegment(
                id=f"seg_{uuid.uuid4().hex[:12]}",
                job_id=job.id,
                segment_index=idx,
                start_time=seg["start"],
                end_time=seg["end"],
                text=seg["text"]
            )
            db.add(t_seg)
        db.commit()

        # Step 4: Content Niche Analysis
        update_job_status(52, "Analyzing transcript topics, audience and optimal niche...", stage="analyzing")
        full_transcript = " ".join(s["text"] for s in segments)
        niche_analysis = analyze_content_niche(full_transcript, video_title=job.title)

        job.detected_niche = niche_analysis["primary_niche"]
        job.confidence_score = niche_analysis["confidence_score"]
        job.target_audience = niche_analysis["target_audience"]
        job.suitable_platforms = niche_analysis["suitable_platforms"]
        job.key_themes = niche_analysis["key_themes"]
        db.commit()

        # Step 5: Candidate Clip Generation & Ranking
        update_job_status(58, f"Generating candidate moments (target {job.target_clip_count} clips >= 60s)...", stage="clipping")
        candidates = find_candidate_clips(
            segments=segments,
            source_duration=media_info["duration_seconds"],
            target_count=job.target_clip_count,
            min_duration=job.min_duration,
            target_duration=job.target_duration,
            max_duration=job.max_duration
        )

        # Clear existing clip records if retrying
        db.query(Clip).filter(Clip.job_id == job.id).delete()
        created_clips = []
        for c in candidates:
            clip_row = Clip(
                id=f"clip_{uuid.uuid4().hex[:12]}",
                job_id=job.id,
                clip_index=c["clip_index"],
                title=c["title"],
                hook=c["hook"],
                transcript_excerpt=c["text"][:500],
                start_time=c["start_time"],
                end_time=c["end_time"],
                duration=c["duration"],
                aspect_ratio=job.aspect_ratio,
                viral_score=c["viral_score"],
                selection_reason=c["selection_reason"],
                status="candidate"
            )
            db.add(clip_row)
            created_clips.append((clip_row, c["segments"]))
        db.commit()

        # Step 6: Render Each Clip into Vertical Video with Subtitles
        update_job_status(65, f"Rendering {len(created_clips)} vertical clips with {job.subtitle_style} captions...", stage="rendering", status="rendering")
        
        rendered_clips_data = []
        total_clips = len(created_clips)

        for i, (clip_row, c_segs) in enumerate(created_clips):
            clip_num = i + 1
            render_pct = 65 + int((i / total_clips) * 30)
            update_job_status(render_pct, f"Rendering vertical Clip {clip_num}/{total_clips} ({clip_row.duration:.1f}s)...")

            # Create rendering attempt record
            attempt = RenderingAttempt(
                id=f"att_{uuid.uuid4().hex[:12]}",
                job_id=job.id,
                clip_id=clip_row.id,
                attempt_number=1,
                status="rendering",
                started_at=datetime.now(timezone.utc)
            )
            db.add(attempt)
            db.commit()

            start_t = time.time()
            try:
                render_result = render_clip_video(
                    source_video_path=source_video_path,
                    output_dir=job_output_dir,
                    clip_id=clip_row.id,
                    clip_index=clip_num,
                    start_time=clip_row.start_time,
                    end_time=clip_row.end_time,
                    aspect_ratio=job.aspect_ratio,
                    subtitle_style=job.subtitle_style,
                    burn_subtitles=job.burn_subtitles,
                    clip_segments=c_segs
                )

                clip_row.video_path = render_result["video_path"]
                clip_row.thumbnail_path = render_result["thumbnail_path"]
                clip_row.srt_path = render_result["srt_path"]
                clip_row.vtt_path = render_result["vtt_path"]
                clip_row.duration = render_result["duration"]
                clip_row.file_size_mb = render_result["file_size_mb"]
                clip_row.status = "completed"

                attempt.status = "success"
                attempt.ended_at = datetime.now(timezone.utc)
                attempt.render_duration_sec = round(time.time() - start_t, 2)
                db.commit()

                rendered_clips_data.append({
                    "id": clip_row.id,
                    "clip_index": clip_row.clip_index,
                    "title": clip_row.title,
                    "hook": clip_row.hook,
                    "start_time": clip_row.start_time,
                    "end_time": clip_row.end_time,
                    "duration": clip_row.duration,
                    "aspect_ratio": clip_row.aspect_ratio,
                    "viral_score": clip_row.viral_score,
                    "selection_reason": clip_row.selection_reason,
                    "video_path": clip_row.video_path,
                    "thumbnail_path": clip_row.thumbnail_path,
                    "srt_path": clip_row.srt_path,
                    "vtt_path": clip_row.vtt_path,
                    "file_size_mb": clip_row.file_size_mb,
                    "status": "completed"
                })

            except Exception as render_err:
                attempt.status = "failed"
                attempt.error_log = str(render_err)
                attempt.ended_at = datetime.now(timezone.utc)
                clip_row.status = "failed"
                clip_row.error_message = str(render_err)
                db.commit()
                raise render_err

        # Step 7: Generate Manifest
        manifest_path = generate_job_manifest(
            job_id=job.id,
            job_data={
                "title": job.title,
                "source_type": job.source_type,
                "source_url": job.source_url,
                "detected_niche": job.detected_niche,
                "target_audience": job.target_audience,
                "status": "completed",
                "created_at": job.created_at,
                "completed_at": datetime.now(timezone.utc)
            },
            clips_data=rendered_clips_data,
            output_dir=job_output_dir
        )

        # Step 8: Mark Job Completed
        job.status = "completed"
        job.stage = "completed"
        job.progress = 100
        job.status_message = f"Successfully generated and rendered {len(rendered_clips_data)} vertical clips (all 60s+)."
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Job {job.id} completed successfully with {len(rendered_clips_data)} clips.")

    except Exception as e:
        logger.exception(f"Job {job.id} failed: {e}")
        job.status = "failed"
        job.stage = "failed"
        job.error_detail = str(e)
        job.status_message = f"Failed: {str(e)}"
        db.commit()
    finally:
        db.close()

def run_worker_loop():
    """Main worker daemon polling Redis or sleeping."""
    logger.info("ClipForge AI Worker started. Initializing database and recovering stale jobs...")
    init_db()
    recover_stale_jobs()

    from backend.app.workers.queue import get_redis_client, JOB_QUEUE_KEY
    redis_client = get_redis_client()

    if not redis_client:
        logger.info("Redis not configured or offline. Worker running in idle standby (in-process threads will handle jobs).")
        while True:
            time.sleep(10)

    logger.info(f"Worker connected to Redis. Polling '{JOB_QUEUE_KEY}'...")
    while True:
        try:
            item = redis_client.blpop(JOB_QUEUE_KEY, timeout=5)
            if item:
                _, job_id = item
                logger.info(f"Worker received job: {job_id}")
                process_job(job_id)
        except Exception as e:
            if "timeout" in str(e).lower():
                continue
            logger.error(f"Error in worker polling loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_worker_loop()
