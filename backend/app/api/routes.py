from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.models import ContentSource, IngestionJob
from app.services.ingestion_service import IngestionService
from app.config import settings
import os
import shutil

router = APIRouter()


class IngestionRequest(BaseModel):
    source: str
    source_type: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    source_id: Optional[int] = None


class IngestionResponse(BaseModel):
    job_id: int
    status: str
    message: str


class SourceResponse(BaseModel):
    id: int
    source_type: str
    title: str
    author: str
    hash: str
    created_at: str
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    id: int
    status: str
    progress: float
    error_message: Optional[str] = None
    source_id: Optional[int] = None
    
    class Config:
        from_attributes = True


def run_ingestion(job_id: int, source: str, file_path: Optional[str], db: Session):
    service = IngestionService(db)
    try:
        service.ingest(source, file_path, job_id)
    except Exception as e:
        print(f"Ingestion failed: {str(e)}")


@router.post("/ingest/url", response_model=IngestionResponse)
async def ingest_url(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job = IngestionJob(status="pending", metadata={"source": request.source})
    db.add(job)
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(run_ingestion, job.id, request.source, None, db)
    
    return IngestionResponse(
        job_id=job.id,
        status="pending",
        message="Ingestion started"
    )


@router.post("/ingest/file", response_model=IngestionResponse)
async def ingest_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed")
    
    file_path = os.path.join(settings.upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    job = IngestionJob(status="pending", metadata={"file_path": file_path})
    db.add(job)
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(run_ingestion, job.id, file_path, file_path, db)
    
    return IngestionResponse(
        job_id=job.id,
        status="pending",
        message="File uploaded and ingestion started"
    )


@router.post("/ingest/text", response_model=IngestionResponse)
async def ingest_text(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job = IngestionJob(status="pending", metadata={"text": request.source})
    db.add(job)
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(run_ingestion, job.id, request.source, None, db)
    
    return IngestionResponse(
        job_id=job.id,
        status="pending",
        message="Text ingestion started"
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.get("/jobs", response_model=List[JobStatusResponse])
async def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(IngestionJob).offset(skip).limit(limit).all()
    return jobs


@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in ["pending", "detecting", "extracting", "chunking", "embedding", "storing"]:
        job.status = "cancelled"
        db.commit()
        return {"message": "Job cancelled"}
    
    return {"message": "Job cannot be cancelled"}


@router.get("/sources", response_model=List[SourceResponse])
async def list_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sources = db.query(ContentSource).offset(skip).limit(limit).all()
    return sources


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(ContentSource).filter(ContentSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.delete("/sources/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    service = IngestionService(db)
    service.delete_source(source_id)
    return {"message": "Source deleted"}


@router.post("/search")
async def search(request: SearchRequest, db: Session = Depends(get_db)):
    service = IngestionService(db)
    results = service.search(request.query, request.limit, request.source_id)
    return {"results": results}
