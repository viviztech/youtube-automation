import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class YouTubeUpload(Base):
    __tablename__ = "youtube_uploads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("video_projects.id"), nullable=False, unique=True)
    youtube_video_id = Column(String(50), nullable=True)
    youtube_url = Column(String(200), nullable=True)
    yt_title = Column(String(300), nullable=True)
    yt_description = Column(Text, nullable=True)
    yt_tags = Column(Text, nullable=True)
    yt_category_id = Column(String(10), default="22")
    privacy_status = Column(String(20), default="public")
    video_file_path = Column(String(500), nullable=True)
    # pending | uploading | done | failed
    status = Column(String(30), default="pending")
    error_msg = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("VideoProject", back_populates="upload")
