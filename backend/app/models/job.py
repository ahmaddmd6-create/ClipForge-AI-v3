import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), default="Untitled Clipping Job")
    source_type = Column(String(32), nullable=False)  # "youtube" or "upload"
    source_url = Column(String(512), nullable=True)
    source_filename = Column(String(255), nullable=True)
    
    # Status and progress
    status = Column(String(32), default="queued", index=True)
    stage = Column(String(64), default="queued")
    progress = Column(Integer, default=0)
    status_message = Column(Text, default="Job initialized")
    error_detail = Column(Text, nullable=True)

    # User settings
    target_clip_count = Column(Integer, default=5)
    min_duration = Column(Float, default=60.0)
    target_duration = Column(Float, default=75.0)
    max_duration = Column(Float, default=90.0)
    aspect_ratio = Column(String(16), default="9:16")
    subtitle_style = Column(String(64), default="hormozi_yellow")
    burn_subtitles = Column(Boolean, default=True)
    background_music = Column(String(64), nullable=True)
    rights_declared = Column(Boolean, default=True)

    # AI Analysis results
    detected_niche = Column(String(128), nullable=True)
    target_audience = Column(String(255), nullable=True)
    key_themes = Column(Text, nullable=True)
    suitable_platforms = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    source_asset = relationship("SourceAsset", back_populates="job", uselist=False, cascade="all, delete-orphan")
    clips = relationship("Clip", back_populates="job", cascade="all, delete-orphan", order_by="Clip.clip_index")
    transcript_segments = relationship("TranscriptSegment", back_populates="job", cascade="all, delete-orphan")
    rendering_attempts = relationship("RenderingAttempt", back_populates="job", cascade="all, delete-orphan")
