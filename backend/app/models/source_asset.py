import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class SourceAsset(Base):
    __tablename__ = "source_assets"

    id = Column(String(64), primary_key=True, index=True)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(BigInteger, default=0)
    duration_seconds = Column(Float, default=0.0)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    frame_rate = Column(Float, default=30.0)
    video_codec = Column(String(32), default="h264")
    audio_codec = Column(String(32), default="aac")
    has_audio = Column(Boolean, default=True)
    rotation = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="source_asset")
