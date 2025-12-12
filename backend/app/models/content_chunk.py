from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class ContentChunk(Base):
    __tablename__ = "content_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True, nullable=False)
    source_id = Column(Integer, ForeignKey("content_sources.id"), nullable=False)
    text = Column(Text, nullable=False)
    chunk_type = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    chunk_order = Column(Integer, nullable=False)
    metadata = Column(JSON, default={})
    
    source = relationship("ContentSource", back_populates="chunks")
