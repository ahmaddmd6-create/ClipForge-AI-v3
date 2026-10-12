import json
import logging
import threading
from typing import Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

JOB_QUEUE_KEY = "clipforge:jobs:queue"

def get_redis_client():
    try:
        import redis
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=10, socket_connect_timeout=3)
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis is not available ({e}). Using in-process threading fallback.")
        return None

def enqueue_job(job_id: str):
    """Adds job_id to Redis queue, or dispatches to in-process worker thread if Redis is offline."""
    r = get_redis_client()
    if r:
        try:
            r.rpush(JOB_QUEUE_KEY, job_id)
            logger.info(f"Enqueued job {job_id} to Redis queue.")
            return
        except Exception as e:
            logger.warning(f"Failed to push to Redis: {e}. Falling back to background thread.")

    # Fallback: run worker function in background thread
    from backend.app.worker import process_job
    t = threading.Thread(target=process_job, args=(job_id,), daemon=True)
    t.start()
    logger.info(f"Dispatched job {job_id} to in-process background worker thread.")
