import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Script(Base):
    __tablename__ = "scripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("video_projects.id"), nullable=False, unique=True)
    prompt_used = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=True)
    model_used = Column(String(60), default="claude-sonnet-4-6")
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("VideoProject", back_populates="script")
