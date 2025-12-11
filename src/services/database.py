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


class QuizDB(Base):
    """SQLite model for generated quizzes"""
    __tablename__ = "quizzes"
    
    id = Column(String, primary_key=True)
    source_id = Column(String, nullable=True, index=True)
    quiz_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    model_used = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_quizzes_source_id', 'source_id'),
        Index('idx_quizzes_status', 'status'),
        Index('idx_quizzes_created_at', 'created_at'),
    )


class QuestionDB(Base):
    """SQLite model for quiz questions"""
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True)
    quiz_id = Column(String, nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    question_data = Column(JSON, nullable=False)  # Stores options/answers/pairs
    explanation = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_questions_quiz_id', 'quiz_id'),
    )


class MindMapDB(Base):
    """SQLite model for generated mind maps"""
    __tablename__ = "mindmaps"
    
    id = Column(String, primary_key=True)
    source_id = Column(String, nullable=True, index=True)
    status = Column(String, default="pending")
    model_used = Column(String, nullable=True)
    root_node_id = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_mindmaps_source_id', 'source_id'),
        Index('idx_mindmaps_status', 'status'),
        Index('idx_mindmaps_created_at', 'created_at'),
    )


class MindMapNodeDB(Base):
    """SQLite model for mind map nodes"""
    __tablename__ = "mindmap_nodes"
    
    id = Column(String, primary_key=True)
    mindmap_id = Column(String, nullable=False, index=True)
    parent_id = Column(String, nullable=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    level = Column(Integer, nullable=False)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_mindmap_nodes_mindmap_id', 'mindmap_id'),
        Index('idx_mindmap_nodes_parent_id', 'parent_id'),
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
    
    def get_chunks_by_ids(self, chunk_ids: list) -> list:
        """Get specific chunks by their IDs"""
        with self.get_session() as session:
            chunk_dbs = session.query(ChunkDB).filter(ChunkDB.id.in_(chunk_ids)).all()
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
    
    # Pedagogy engine methods
    def insert_quiz(self, quiz_data: dict) -> str:
        """Insert a quiz and return its ID"""
        with self.get_session() as session:
            quiz_db = QuizDB(**quiz_data)
            session.add(quiz_db)
            session.commit()
            return quiz_db.id
    
    def update_quiz(self, quiz_id: str, updates: dict):
        """Update a quiz"""
        with self.get_session() as session:
            quiz_db = session.query(QuizDB).filter_by(id=quiz_id).first()
            if quiz_db:
                for key, value in updates.items():
                    setattr(quiz_db, key, value)
                session.commit()
    
    def get_quiz(self, quiz_id: str) -> Optional[dict]:
        """Get a quiz by ID"""
        with self.get_session() as session:
            quiz_db = session.query(QuizDB).filter_by(id=quiz_id).first()
            if quiz_db:
                return {
                    "id": quiz_db.id,
                    "source_id": quiz_db.source_id,
                    "quiz_type": quiz_db.quiz_type,
                    "status": quiz_db.status,
                    "model_used": quiz_db.model_used,
                    "metadata": quiz_db.metadata_json,
                    "created_at": quiz_db.created_at,
                    "completed_at": quiz_db.completed_at,
                    "error_message": quiz_db.error_message
                }
            return None
    
    def insert_questions(self, questions_data: list) -> int:
        """Insert multiple questions and return count"""
        with self.get_session() as session:
            question_dbs = [QuestionDB(**question_data) for question_data in questions_data]
            session.add_all(question_dbs)
            session.commit()
            return len(question_dbs)
    
    def get_questions_by_quiz_id(self, quiz_id: str) -> list:
        """Get all questions for a quiz"""
        with self.get_session() as session:
            question_dbs = session.query(QuestionDB).filter_by(quiz_id=quiz_id).all()
            return [
                {
                    "id": question.id,
                    "quiz_id": question.quiz_id,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "question_data": question.question_data,
                    "explanation": question.explanation,
                    "metadata": question.metadata_json,
                    "created_at": question.created_at
                }
                for question in question_dbs
            ]
    
    def insert_mindmap(self, mindmap_data: dict) -> str:
        """Insert a mind map and return its ID"""
        with self.get_session() as session:
            mindmap_db = MindMapDB(**mindmap_data)
            session.add(mindmap_db)
            session.commit()
            return mindmap_db.id
    
    def update_mindmap(self, mindmap_id: str, updates: dict):
        """Update a mind map"""
        with self.get_session() as session:
            mindmap_db = session.query(MindMapDB).filter_by(id=mindmap_id).first()
            if mindmap_db:
                for key, value in updates.items():
                    setattr(mindmap_db, key, value)
                session.commit()
    
    def get_mindmap(self, mindmap_id: str) -> Optional[dict]:
        """Get a mind map by ID"""
        with self.get_session() as session:
            mindmap_db = session.query(MindMapDB).filter_by(id=mindmap_id).first()
            if mindmap_db:
                return {
                    "id": mindmap_db.id,
                    "source_id": mindmap_db.source_id,
                    "status": mindmap_db.status,
                    "model_used": mindmap_db.model_used,
                    "root_node_id": mindmap_db.root_node_id,
                    "metadata": mindmap_db.metadata_json,
                    "created_at": mindmap_db.created_at,
                    "completed_at": mindmap_db.completed_at,
                    "error_message": mindmap_db.error_message
                }
            return None
    
    def insert_mindmap_nodes(self, nodes_data: list) -> int:
        """Insert multiple mind map nodes and return count"""
        with self.get_session() as session:
            node_dbs = [MindMapNodeDB(**node_data) for node_data in nodes_data]
            session.add_all(node_dbs)
            session.commit()
            return len(node_dbs)
    
    def get_mindmap_nodes(self, mindmap_id: str) -> list:
        """Get all nodes for a mind map"""
        with self.get_session() as session:
            node_dbs = session.query(MindMapNodeDB).filter_by(mindmap_id=mindmap_id).all()
            return [
                {
                    "id": node.id,
                    "mindmap_id": node.mindmap_id,
                    "parent_id": node.parent_id,
                    "content": node.content,
                    "summary": node.summary,
                    "level": node.level,
                    "metadata": node.metadata_json,
                    "created_at": node.created_at
                }
                for node in node_dbs
            ]