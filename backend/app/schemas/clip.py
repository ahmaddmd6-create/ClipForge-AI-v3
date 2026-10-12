from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict

class ClipUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    aspect_ratio: Optional[str] = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time is not None and self.end_time is not None:
            if self.start_time >= self.end_time:
                raise ValueError("start_time must be less than end_time")
            if (self.end_time - self.start_time) < 60.0:
                raise ValueError("Clip duration must be at least 60.0 seconds")
        return self

class ClipDetailResponse(BaseModel):
    id: str
    job_id: str
    clip_index: int
    title: str
    hook: str
    transcript_excerpt: str
    start_time: float
    end_time: float
    duration: float
    aspect_ratio: str
    viral_score: int
    selection_reason: str
    status: str
    video_path: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    srt_url: Optional[str] = None
    vtt_url: Optional[str] = None
    file_size_mb: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
