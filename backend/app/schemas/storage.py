from typing import Optional
from pydantic import BaseModel

class StorageStatsResponse(BaseModel):
    storage_root: str
    outputs_directory: str
    inputs_directory: str
    total_used_mb: float
    available_disk_gb: float
    total_disk_gb: float
    total_jobs: int = 0
    total_clips: int = 0
    retention_days: int
    max_concurrent_jobs: int
    cpu_threads: int
    transcription_provider: str
    whisper_model: str
    whisper_compute_type: str
    ai_provider: str
