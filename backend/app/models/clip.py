import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Clip(Base):
    __tablename__ = "clips"

    id = Column(String(64), primary_key=True, index=True)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    clip_index = Column(Integer, nullable=False)
    title = Column(String(255), default="Viral Clip")
    hook = Column(Text, default="")
    transcript_excerpt = Column(Text, default="")
    
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    aspect_ratio = Column(String(16), default="9:16")
    
    viral_score = Column(Integer, default=80)
    selection_reason = Column(Text, default="")
    status = Column(String(32), default="candidate", index=True)  # candidate, rendering, completed, failed
    
    # Rendered artifact paths
    video_path = Column(String(512), nullable=True)
    thumbnail_path = Column(String(512), nullable=True)
    srt_path = Column(String(512), nullable=True)
    vtt_path = Column(String(512), nullable=True)
    file_size_mb = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    job = relationship("Job", back_populates="clips")
