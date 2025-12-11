import asyncio
import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..adapters import AdapterFactory
from ..adapters.base import BaseAdapter
from .database import DatabaseManager
from .chunking import ChunkingService
from .vector_db import VectorService
from ..models import (
    IngestionConfig, IngestionRequest, Job, Document, Chunk,
    JobStatus, DocumentStatus, SourceType
)


class IngestionService:
    """Main service for document ingestion pipeline"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.adapter_factory = AdapterFactory()
        self.db_manager = DatabaseManager(self.config.get("db_path", "ingestion.db"))
        self.chunking_service = ChunkingService(self.config.get("chunking_config", {}))
        self.vector_service = VectorService(
            self.config.get("lancedb_path", "lancedb"),
            self.config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        )
        
        # Create database tables
        self.db_manager.create_tables()
        
        # Initialize vector service
        self.vector_service.initialize()
    
    async def ingest_document(self, request: IngestionRequest) -> str:
        """
        Start ingestion of a document as a background job
        
        Returns:
            Job ID for tracking the ingestion progress
        """
        job_id = str(uuid.uuid4())
        
        # Create job record
        job_data = {
            "id": job_id,
            "source_type": request.source_type,
            "source_url": request.source_url,
            "status": JobStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "progress": 0.0
        }
        
        self.db_manager.insert_job(job_data)
        
        # Start background ingestion task
        asyncio.create_task(self._ingest_document_async(job_id, request))
        
        return job_id
    
    async def _ingest_document_async(self, job_id: str, request: IngestionRequest):
        """Background task for document ingestion"""
        try:
            self.logger.info(f"Starting ingestion job {job_id} for {request.source_url}")
            
            # Update job status to running
            self.db_manager.update_job(job_id, {
                "status": JobStatus.RUNNING.value,
                "started_at": datetime.utcnow(),
                "progress": 0.1
            })
            
            # Get appropriate adapter
            adapter = self.adapter_factory.get_adapter(
                request.source_type, 
                self.config.get("adapter_configs", {})
            )
            
            # Validate source
            if not adapter.validate_source(request.source_url):
                raise ValueError(f"Invalid {request.source_type} source: {request.source_url}")
            
            # Update progress
            self.db_manager.update_job(job_id, {"progress": 0.2})
            
            # Extract content using adapter
            document = await adapter.adapt(request.source_url)
            
            # Check for duplicates using hash
            existing_doc = self.db_manager.get_document_by_hash(document.hash_sha256)
            if existing_doc:
                self.logger.info(f"Document already exists (hash: {document.hash_sha256})")
                self.db_manager.update_job(job_id, {
                    "status": JobStatus.COMPLETED.value,
                    "completed_at": datetime.utcnow(),
                    "progress": 1.0,
                    "document_id": existing_doc["id"],
                    "chunk_count": 0
                })
                return
            
            # Update progress
            self.db_manager.update_job(job_id, {"progress": 0.4})
            
            # Persist document to database
            doc_id = str(uuid.uuid4())
            doc_data = {
                "id": doc_id,
                "source_type": document.source_type,
                "content": document.content,
                "metadata_json": document.metadata.dict(),
                "hash_sha256": document.hash_sha256,
                "status": DocumentStatus.PROCESSING.value
            }
            
            self.db_manager.insert_document(doc_data)
            document.id = doc_id
            
            # Update progress
            self.db_manager.update_job(job_id, {"progress": 0.6, "document_id": doc_id})
            
            # Chunk document
            chunks = self.chunking_service.chunk_document(
                doc_id, 
                document.content, 
                document.metadata.dict()
            )
            
            if not chunks:
                raise ValueError("Failed to chunk document or document too short")
            
            # Set timestamps for chunks
            now = datetime.utcnow()
            for chunk in chunks:
                chunk["created_at"] = now
            
            # Persist chunks to database
            chunks_data = []
            for chunk in chunks:
                chunk_data = {
                    "id": chunk["id"],
                    "document_id": chunk["document_id"],
                    "content": chunk["content"],
                    "chunk_index": chunk["chunk_index"],
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"],
                    "chunk_hash": chunk["chunk_hash"],
                    "metadata_json": chunk["metadata"],
                    "created_at": chunk["created_at"]
                }
                chunks_data.append(chunk_data)
            
            self.db_manager.insert_chunks(chunks_data)
            
            # Update progress
            self.db_manager.update_job(job_id, {"progress": 0.8})
            
            # Generate embeddings and store in vector DB
            success = self.vector_service.upsert_chunks(chunks)
            if not success:
                raise ValueError("Failed to store embeddings in vector database")
            
            # Mark document as completed
            self.db_manager.update_job(job_id, {"progress": 0.9})
            self.db_manager.update_job(job_id, {
                "status": JobStatus.COMPLETED.value,
                "completed_at": datetime.utcnow(),
                "progress": 1.0,
                "chunk_count": len(chunks)
            })
            
            self.logger.info(f"Successfully completed ingestion job {job_id}: {len(chunks)} chunks")
            
        except Exception as e:
            self.logger.error(f"Ingestion job {job_id} failed: {e}")
            self.db_manager.update_job(job_id, {
                "status": JobStatus.FAILED.value,
                "completed_at": datetime.utcnow(),
                "error_message": str(e)
            })
    
    def get_job_status(self, job_id: str) -> Optional[Job]:
        """Get the status of an ingestion job"""
        job_data = self.db_manager.get_job(job_id)
        if job_data:
            return Job(**job_data)
        return None
    
    def get_all_jobs(self, limit: int = 100) -> list:
        """Get all ingestion jobs"""
        jobs_data = self.db_manager.get_all_jobs(limit)
        return [Job(**job_data) for job_data in jobs_data]
    
    def get_document_chunks(self, document_id: str) -> list:
        """Get all chunks for a document"""
        return self.db_manager.get_chunks_by_document_id(document_id)
    
    def search_similar(self, query: str, limit: int = 10, filter_conditions: Optional[Dict[str, Any]] = None) -> list:
        """Search for similar content using embeddings"""
        return self.vector_service.search_similar(query, limit, filter_conditions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the ingestion system"""
        try:
            # Get database stats
            all_jobs = self.db_manager.get_all_jobs()
            total_jobs = len(all_jobs)
            completed_jobs = len([j for j in all_jobs if j["status"] == JobStatus.COMPLETED.value])
            failed_jobs = len([j for j in all_jobs if j["status"] == JobStatus.FAILED.value])
            
            # Get vector DB stats
            vector_stats = self.vector_service.get_stats()
            
            return {
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
                "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0,
                "vector_database": vector_stats,
                "supported_sources": list(SourceType),
                "chunking_config": self.chunking_service.config,
                "embedding_model": self.vector_service.model_name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}