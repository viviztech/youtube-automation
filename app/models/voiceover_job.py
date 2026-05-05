import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class VoiceoverJob(Base):
    __tablename__ = "voiceover_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("video_projects.id"), nullable=False, unique=True)
    voice_id = Column(String(100), nullable=True)
    voice_name = Column(String(100), nullable=True)
    audio_path = Column(String(500), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    # pending | processing | done | failed
    status = Column(String(30), default="pending")
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("VideoProject", back_populates="voiceover")
