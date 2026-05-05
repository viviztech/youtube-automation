import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class VideoProject(Base):
    __tablename__ = "video_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(300), nullable=False)
    niche = Column(String(100), nullable=True)
    topic = Column(String(300), nullable=False)
    style = Column(String(100), nullable=True)
    # scripted | voiced | edited | ready | uploaded | failed
    status = Column(String(30), default="scripted")
    tags = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    script = relationship("Script", back_populates="project", uselist=False)
    voiceover = relationship("VoiceoverJob", back_populates="project", uselist=False)
    upload = relationship("YouTubeUpload", back_populates="project", uselist=False)
