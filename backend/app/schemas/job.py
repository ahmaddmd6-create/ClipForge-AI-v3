from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class JobCreate(BaseModel):
    youtube_url: Optional[str] = None
    source_type: str = Field(default="youtube", pattern="^(youtube|upload)$")
    rights_declared: bool = Field(default=True, description="Confirmation that user is authorized to process this video")
    target_clip_count: int = Field(default=5, ge=1, le=10)
    min_duration: float = Field(default=60.0, ge=60.0, description="Minimum clip duration, hard minimum 60s")
    target_duration: float = Field(default=75.0, ge=60.0, le=120.0)
    max_duration: float = Field(default=90.0, ge=60.0, le=180.0)
    aspect_ratio: str = Field(default="9:16", pattern="^(9:16|16:9|1:1)$")
    subtitle_style: str = Field(default="hormozi_yellow")
    burn_subtitles: bool = True
    background_music: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    target_clip_count: Optional[int] = None
    min_duration: Optional[float] = None
    target_duration: Optional[float] = None
    aspect_ratio: Optional[str] = None
    subtitle_style: Optional[str] = None
    burn_subtitles: Optional[bool] = None

class SourceAssetResponse(BaseModel):
    id: str
    file_path: str
    file_size_bytes: int
    duration_seconds: float
    width: int
    height: int
    frame_rate: float
    video_codec: str
    audio_codec: str
    has_audio: bool
    rotation: int

    model_config = ConfigDict(from_attributes=True)

class ClipSummaryResponse(BaseModel):
    id: str
    clip_index: int
    title: str
    hook: str
    start_time: float
    end_time: float
    duration: float
    aspect_ratio: str
    viral_score: int
    selection_reason: str
    status: str
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    file_size_mb: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id: str
    title: str
    source_type: str
    source_url: Optional[str] = None
    source_filename: Optional[str] = None
    status: str
    stage: str
    progress: int
    status_message: str
    error_detail: Optional[str] = None
    target_clip_count: int
    min_duration: float
    target_duration: float
    max_duration: float
    aspect_ratio: str
    subtitle_style: str
    burn_subtitles: bool
    background_music: Optional[str] = None
    rights_declared: bool
    detected_niche: Optional[str] = None
    target_audience: Optional[str] = None
    key_themes: Optional[str] = None
    suitable_platforms: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    source_asset: Optional[SourceAssetResponse] = None
    clips: List[ClipSummaryResponse] = []

    model_config = ConfigDict(from_attributes=True)
