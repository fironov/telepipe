from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    stored_name = Column(String, nullable=False, unique=True)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
