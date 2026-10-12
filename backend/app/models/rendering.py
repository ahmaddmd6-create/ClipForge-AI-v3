import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class RenderingAttempt(Base):
    __tablename__ = "rendering_attempts"

    id = Column(String(64), primary_key=True, index=True)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    clip_id = Column(String(64), nullable=True)
    attempt_number = Column(Integer, default=1)
    status = Column(String(32), default="pending")  # pending, rendering, success, failed
    error_log = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    render_duration_sec = Column(Float, default=0.0)

    job = relationship("Job", back_populates="rendering_attempts")
