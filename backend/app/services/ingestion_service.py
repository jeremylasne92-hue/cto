from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import ContentSource, ContentChunk, IngestionJob
from app.core.source_detector import SourceDetector
from app.core.hasher import ContentHasher
from app.core.chunker import SemanticChunker
from app.core.embedder import EmbeddingGenerator
from app.core.vector_store import VectorStore
from app.services.extractor_factory import ExtractorFactory
import traceback


class IngestionService:
    
    def __init__(self, db: Session):
        self.db = db
        self.chunker = SemanticChunker()
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
    
    def ingest(self, source: str, file_path: Optional[str] = None, job_id: Optional[int] = None) -> ContentSource:
        job = None
        if job_id:
            job = self.db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        
        try:
            if job:
                job.status = "detecting"
                job.progress = 0.1
                self.db.commit()
            
            source_type, metadata = SourceDetector.detect(source, file_path)
            
            if job:
                job.progress = 0.2
                self.db.commit()
            
            content_hash = self._generate_hash(source, file_path, source_type, metadata)
            
            existing = self.db.query(ContentSource).filter(ContentSource.hash == content_hash).first()
            if existing:
                if job:
                    job.status = "completed"
                    job.progress = 1.0
                    job.source_id = existing.id
                    self.db.commit()
                return existing
            
            if job:
                job.status = "extracting"
                job.progress = 0.3
                self.db.commit()
            
            extractor = ExtractorFactory.get_extractor(source_type)
            extracted_metadata = extractor.extract_metadata(source if source_type in ['youtube', 'web'] else file_path)
            content_data = extractor.extract(source if source_type in ['youtube', 'web'] else file_path, metadata)
            
            if job:
                job.progress = 0.5
                self.db.commit()
            
            content_source = ContentSource(
                file_path=file_path,
                source_type=source_type,
                title=content_data.get('title', ''),
                author=content_data.get('author', ''),
                hash=content_hash,
                metadata=extracted_metadata
            )
            self.db.add(content_source)
            self.db.commit()
            self.db.refresh(content_source)
            
            if job:
                job.source_id = content_source.id
                job.status = "chunking"
                job.progress = 0.6
                self.db.commit()
            
            chunks = self._chunk_content(content_data, source_type)
            
            if job:
                job.status = "embedding"
                job.progress = 0.7
                self.db.commit()
            
            embeddings = self.embedder.generate_batch([chunk['text'] for chunk in chunks])
            
            if job:
                job.progress = 0.8
                self.db.commit()
            
            for chunk, embedding in zip(chunks, embeddings):
                content_chunk = ContentChunk(
                    chunk_id=chunk['chunk_id'],
                    source_id=content_source.id,
                    text=chunk['text'],
                    chunk_type=chunk['chunk_type'],
                    position=chunk['position'],
                    chunk_order=chunk['chunk_order'],
                    metadata=chunk.get('metadata', {})
                )
                self.db.add(content_chunk)
            
            self.db.commit()
            
            if job:
                job.status = "storing"
                job.progress = 0.9
                self.db.commit()
            
            self.vector_store.add_embeddings(chunks, embeddings, content_source.id)
            
            if job:
                job.status = "completed"
                job.progress = 1.0
                self.db.commit()
            
            return content_source
        
        except Exception as e:
            if job:
                job.status = "failed"
                job.error_message = str(e)
                self.db.commit()
            raise e
    
    def _generate_hash(self, source: str, file_path: Optional[str], source_type: str, metadata: Dict[str, Any]) -> str:
        if file_path:
            return ContentHasher.hash_file(file_path)
        elif source_type == 'youtube' or source_type == 'web':
            return ContentHasher.hash_url(source)
        else:
            return ContentHasher.hash_text(source)
    
    def _chunk_content(self, content_data: Dict[str, Any], source_type: str):
        text = content_data.get('text', '')
        
        if source_type == 'markdown':
            return self.chunker.chunk_with_structure(text, 'markdown')
        else:
            return self.chunker.chunk_text(text, source_type)
    
    def search(self, query: str, limit: int = 10, source_id: Optional[int] = None):
        query_embedding = self.embedder.generate(query)
        results = self.vector_store.search(query_embedding, limit, source_id)
        return results
    
    def delete_source(self, source_id: int):
        source = self.db.query(ContentSource).filter(ContentSource.id == source_id).first()
        if source:
            self.vector_store.delete_by_source(source_id)
            self.db.delete(source)
            self.db.commit()
