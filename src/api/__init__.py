from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import uuid
import asyncio

from ..models import IngestionRequest, SourceType, JobStatus
from ..services.ingestion import IngestionService
from ..utils.logging_config import setup_logging


# Setup logging
setup_logging()
logger = logger = __import__('logging').getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Universal Ingestion Service",
    description="Ingestion pipeline for multiple document sources with vector embeddings",
    version="1.0.0"
)

# Global ingestion service instance (in production, this should be injected)
ingestion_service = IngestionService()


@app.post("/ingest", response_model=dict)
async def ingest_document(request: IngestionRequest, background_tasks: BackgroundTasks):
    """
    Start ingestion of a document from various sources
    
    Supported source types:
    - youtube: YouTube video URLs (transcribed with Whisper)
    - pdf: PDF document URLs or file paths (text extraction with PyMuPDF)
    - web_page: Generic web page URLs (text extraction with BeautifulSoup)
    - markdown: Markdown file URLs or file paths
    - plain_text: Plain text file URLs or file paths
    """
    try:
        # Validate request
        if not request.source_url:
            raise HTTPException(status_code=400, detail="source_url is required")
        
        if request.source_type not in SourceType:
            raise HTTPException(status_code=400, detail=f"Invalid source_type. Must be one of: {list(SourceType)}")
        
        # Start ingestion
        job_id = await ingestion_service.ingest_document(request)
        
        return {
            "job_id": job_id,
            "message": f"Ingestion started for {request.source_type} source",
            "status_endpoint": f"/status/{job_id}",
            "monitor_endpoint": f"/jobs"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/status/{job_id}", response_model=dict)
async def get_job_status(job_id: str):
    """Get the status of an ingestion job"""
    try:
        job = ingestion_service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.id,
            "status": job.status,
            "source_type": job.source_type,
            "source_url": job.source_url,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "document_id": job.document_id,
            "chunk_count": job.chunk_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/jobs", response_model=dict)
async def get_all_jobs(limit: int = Query(100, le=1000)):
    """Get all ingestion jobs"""
    try:
        jobs = ingestion_service.get_all_jobs(limit)
        
        return {
            "jobs": [
                {
                    "job_id": job.id,
                    "status": job.status,
                    "source_type": job.source_type,
                    "source_url": job.source_url,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat(),
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error_message": job.error_message,
                    "document_id": job.document_id,
                    "chunk_count": job.chunk_count
                }
                for job in jobs
            ],
            "total": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/jobs/{job_id}/chunks", response_model=dict)
async def get_document_chunks(job_id: str):
    """Get all chunks for a completed ingestion job"""
    try:
        job = ingestion_service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=f"Job not completed. Current status: {job.status}")
        
        if not job.document_id:
            raise HTTPException(status_code=400, detail="No document ID found for this job")
        
        chunks = ingestion_service.get_document_chunks(job.document_id)
        
        return {
            "document_id": job.document_id,
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "chunk_id": chunk["id"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"],
                    "chunk_hash": chunk["chunk_hash"],
                    "metadata": chunk["metadata"],
                    "created_at": chunk["created_at"].isoformat()
                }
                for chunk in chunks
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chunks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/search", response_model=dict)
async def search_similar(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, le=100, description="Maximum number of results"),
    filter_source_type: Optional[SourceType] = Query(None, description="Filter by source type")
):
    """Search for similar content using vector embeddings"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Build filter conditions if provided
        filter_conditions = None
        if filter_source_type:
            filter_conditions = {"source_type": filter_source_type.value}
        
        results = ingestion_service.search_similar(query, limit, filter_conditions)
        
        return {
            "query": query,
            "results_count": len(results),
            "results": [
                {
                    "chunk_id": result["id"],
                    "document_id": result["document_id"],
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "score": getattr(result, 'score', None),
                    "created_at": result["created_at"].isoformat() if hasattr(result["created_at"], 'isoformat') else result["created_at"]
                }
                for result in results
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sources", response_model=dict)
async def get_supported_sources():
    """Get list of supported source types"""
    return {
        "supported_sources": [
            {
                "type": source_type.value,
                "description": _get_source_description(source_type)
            }
            for source_type in SourceType
        ],
        "examples": {
            "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "pdf": "https://example.com/document.pdf or /path/to/document.pdf",
            "web_page": "https://example.com",
            "markdown": "https://example.com/README.md or /path/to/file.md",
            "plain_text": "https://example.com/text.txt or /path/to/file.txt"
        }
    }


def _get_source_description(source_type: SourceType) -> str:
    """Get description for source type"""
    descriptions = {
        SourceType.YOUTUBE: "YouTube videos with Whisper transcription",
        SourceType.PDF: "PDF documents with PyMuPDF text extraction",
        SourceType.WEB_PAGE: "Web pages with BeautifulSoup text extraction",
        SourceType.MARKDOWN: "Markdown files converted to plain text",
        SourceType.PLAIN_TEXT: "Plain text files"
    }
    return descriptions.get(source_type, "Unknown source type")


@app.get("/stats", response_model=dict)
async def get_system_stats():
    """Get statistics about the ingestion system"""
    try:
        stats = ingestion_service.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/jobs/{job_id}", response_model=dict)
async def cancel_job(job_id: str):
    """Cancel a running job"""
    try:
        job = ingestion_service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail=f"Job already {job.status}")
        
        # Update job status to cancelled
        # Note: This is a simplified implementation
        # In production, you'd want to actually stop the background task
        ingestion_service.db_manager.update_job(job_id, {
            "status": JobStatus.CANCELLED.value,
            "completed_at": datetime.utcnow()
        })
        
        return {"message": f"Job {job_id} cancelled"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Add missing import
from datetime import datetime