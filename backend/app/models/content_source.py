from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ContentSource(Base):
    __tablename__ = "content_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=True)
    source_type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    hash = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    chunks = relationship("ContentChunk", back_populates="source", cascade="all, delete-orphan")
    jobs = relationship("IngestionJob", back_populates="source")
