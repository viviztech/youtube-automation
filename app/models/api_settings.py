from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base


class APISettings(Base):
    __tablename__ = "api_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False, default="")
    label = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_secret = Column(Boolean, default=True)
    group = Column(String(64), default="general")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
