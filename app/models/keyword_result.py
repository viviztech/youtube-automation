from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from app.database import Base


class KeywordResult(Base):
    __tablename__ = "keyword_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(300), nullable=False)
    source = Column(String(30), nullable=False)  # youtube | google_trends
    search_volume = Column(String(50), nullable=True)
    competition = Column(String(30), nullable=True)
    trend_score = Column(Float, nullable=True)
    related_terms = Column(Text, nullable=True)  # JSON array as string
    niche = Column(String(100), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    is_trending = Column(Boolean, default=False)
