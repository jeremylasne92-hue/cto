from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Integer, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
import os
import json
from typing import Optional


Base = declarative_base()


class DocumentDB(Base):
    """SQLite model for documents"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=False)
    hash_sha256 = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_documents_hash', 'hash_sha256'),
        Index('idx_documents_source_type', 'source_type'),
        Index('idx_documents_created_at', 'created_at'),
    )


class ChunkDB(Base):
    """SQLite model for document chunks"""
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    chunk_hash = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_chunks_document_id', 'document_id'),
        Index('idx_chunks_hash', 'chunk_hash'),
    )


class JobDB(Base):
    """SQLite model for background jobs"""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False)
    source_url = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)
    
    # Results
    document_id = Column(String, nullable=True, index=True)
    chunk_count = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_jobs_status', 'status'),
        Index('idx_jobs_created_at', 'created_at'),
    )


class DatabaseManager:
    """Manager for SQLite database operations"""
    
    def __init__(self, db_path: str = "ingestion.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close the database connection"""
        self.engine.dispose()
    
    def insert_document(self, doc_data: dict) -> str:
        """Insert a document and return its ID"""
        with self.get_session() as session:
            doc_db = DocumentDB(**doc_data)
            session.add(doc_db)
            session.commit()
            return doc_db.id
    
    def get_document_by_hash(self, hash_sha256: str) -> Optional[dict]:
        """Get document by SHA256 hash"""
        with self.get_session() as session:
            doc_db = session.query(DocumentDB).filter_by(hash_sha256=hash_sha256).first()
            if doc_db:
                return {
                    "id": doc_db.id,
                    "source_type": doc_db.source_type,
                    "content": doc_db.content,
                    "metadata": doc_db.metadata_json,
                    "hash_sha256": doc_db.hash_sha256,
                    "created_at": doc_db.created_at,
                    "status": doc_db.status
                }
            return None
    
    def insert_chunks(self, chunks_data: list) -> int:
        """Insert multiple chunks and return count"""
        with self.get_session() as session:
            chunk_dbs = [ChunkDB(**chunk_data) for chunk_data in chunks_data]
            session.add_all(chunk_dbs)
            session.commit()
            return len(chunk_dbs)
    
    def get_chunks_by_document_id(self, document_id: str) -> list:
        """Get all chunks for a document"""
        with self.get_session() as session:
            chunk_dbs = session.query(ChunkDB).filter_by(document_id=document_id).all()
            return [
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "chunk_hash": chunk.chunk_hash,
                    "metadata": chunk.metadata_json,
                    "created_at": chunk.created_at
                }
                for chunk in chunk_dbs
            ]
    
    def insert_job(self, job_data: dict) -> str:
        """Insert a job and return its ID"""
        with self.get_session() as session:
            job_db = JobDB(**job_data)
            session.add(job_db)
            session.commit()
            return job_db.id
    
    def update_job(self, job_id: str, updates: dict):
        """Update a job"""
        with self.get_session() as session:
            job_db = session.query(JobDB).filter_by(id=job_id).first()
            if job_db:
                for key, value in updates.items():
                    setattr(job_db, key, value)
                session.commit()
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get a job by ID"""
        with self.get_session() as session:
            job_db = session.query(JobDB).filter_by(id=job_id).first()
            if job_db:
                return {
                    "id": job_db.id,
                    "source_type": job_db.source_type,
                    "source_url": job_db.source_url,
                    "status": job_db.status,
                    "created_at": job_db.created_at,
                    "started_at": job_db.started_at,
                    "completed_at": job_db.completed_at,
                    "error_message": job_db.error_message,
                    "progress": job_db.progress,
                    "document_id": job_db.document_id,
                    "chunk_count": job_db.chunk_count
                }
            return None
    
    def get_all_jobs(self, limit: int = 100) -> list:
        """Get all jobs (most recent first)"""
        with self.get_session() as session:
            job_dbs = session.query(JobDB).order_by(JobDB.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": job.id,
                    "source_type": job.source_type,
                    "source_url": job.source_url,
                    "status": job.status,
                    "created_at": job.created_at,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at,
                    "error_message": job.error_message,
                    "progress": job.progress,
                    "document_id": job.document_id,
                    "chunk_count": job.chunk_count
                }
                for job in job_dbs
            ]