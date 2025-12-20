from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("content_sources.id"), nullable=True)
    status = Column(String, default="pending")
    progress = Column(Float, default=0.0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    source = relationship("ContentSource", back_populates="jobs")
