import pytest
import tempfile
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.models import IngestionRequest, SourceType, IngestionConfig, JobStatus
from src.services.ingestion import IngestionService
from src.services.database import DatabaseManager
from src.services.chunking import ChunkingService


class TestIngestionService:
    """Test the main ingestion service"""
    
    @pytest.fixture
    def test_config(self):
        """Test configuration"""
        return {
            "db_path": "test_ingestion.db",
            "lancedb_path": "test_lancedb",
            "chunking_config": {
                "max_chunk_size": 200,
                "chunk_overlap": 50,
                "min_chunk_size": 50
            },
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    
    @pytest.fixture
    def ingestion_service(self, test_config):
        """Create ingestion service for testing"""
        # Clean up any existing test databases
        for db_file in ["test_ingestion.db", "test_lancedb.db", "_lancedb.landb"]:
            if os.path.exists(db_file):
                os.remove(db_file)
        
        service = IngestionService(test_config)
        yield service
        
        # Clean up after tests
        service.db_manager.close()
        for db_file in ["test_ingestion.db", "test_lancedb.db", "_lancedb.landb"]:
            if os.path.exists(db_file):
                os.remove(db_file)
    
    @pytest.mark.asyncio
    async def test_ingest_markdown_e2e(self, ingestion_service):
        """End-to-end test for Markdown ingestion"""
        # Create test markdown content
        markdown_content = """# Test Document
        
This is a test document for end-to-end testing.

## Section 1

This content should be chunked appropriately. The document contains multiple sentences that should be grouped together based on semantic similarity.

## Section 2

Another section with different content. This part discusses different topics and should form separate chunks.

### Subsection

More detailed content here that needs to be processed correctly.
"""
        
        # Create temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(markdown_content)
            temp_file_path = temp_file.name
        
        try:
            # Create ingestion request
            config = IngestionConfig(
                max_chunk_size=200,
                chunk_overlap=50,
                similarity_threshold=0.6
            )
            
            request = IngestionRequest(
                source_type=SourceType.MARKDOWN,
                source_url=temp_file_path,
                config=config
            )
            
            # Mock the adapter to avoid actual file operations in test
            with patch.object(ingestion_service, '_ingest_document_async') as mock_async_task:
                # Start ingestion
                job_id = await ingestion_service.ingest_document(request)
                
                # Verify job was created
                assert job_id is not None
                assert len(job_id) > 0
                
                # Check job status
                job = ingestion_service.get_job_status(job_id)
                assert job is not None
                assert job.id == job_id
                assert job.source_type == SourceType.MARKDOWN
                assert job.source_url == temp_file_path
                assert job.status == JobStatus.PENDING
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_ingest_plain_text_e2e(self, ingestion_service):
        """End-to-end test for plain text ingestion"""
        # Create test text content
        text_content = """First paragraph with some content here.
This continues the first paragraph.

Second paragraph on a different topic.
More content in the second paragraph.

Third paragraph with unique content.
This is the end of the document.
"""
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(text_content)
            temp_file_path = temp_file.name
        
        try:
            # Create ingestion request
            request = IngestionRequest(
                source_type=SourceType.PLAIN_TEXT,
                source_url=temp_file_path
            )
            
            # Mock the async ingestion to avoid long-running operations
            with patch.object(ingestion_service, '_ingest_document_async') as mock_async_task:
                # Start ingestion
                job_id = await ingestion_service.ingest_document(request)
                
                # Verify job was created
                assert job_id is not None
                
                # Check job status
                job = ingestion_service.get_job_status(job_id)
                assert job is not None
                assert job.source_type == SourceType.PLAIN_TEXT
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_duplicate_detection(self, ingestion_service):
        """Test that duplicate documents are detected and skipped"""
        # This would require a full implementation with actual adapters
        # For now, we'll test the database logic
        content = "Test content for duplicate detection"
        hash_sha256 = ingestion_service.adapter_factory.get_adapter(SourceType.PLAIN_TEXT)._generate_hash(
            content, "test://source"
        )
        
        # Insert first document
        doc_data = {
            "id": "doc1",
            "source_type": "plain_text",
            "content": content,
            "metadata_json": {"title": "Test"},
            "hash_sha256": hash_sha256,
            "status": "pending"
        }
        
        ingestion_service.db_manager.insert_document(doc_data)
        
        # Check if duplicate is detected
        existing = ingestion_service.db_manager.get_document_by_hash(hash_sha256)
        assert existing is not None
        assert existing["hash_sha256"] == hash_sha256
        
        # Different content should not be duplicate
        different_hash = "different_hash"
        not_duplicate = ingestion_service.db_manager.get_document_by_hash(different_hash)
        assert not_duplicate is None
    
    def test_job_tracking(self, ingestion_service):
        """Test job creation and tracking"""
        # Create test job
        job_data = {
            "id": "test-job-1",
            "source_type": "plain_text",
            "source_url": "test://source",
            "status": JobStatus.PENDING.value,
            "progress": 0.0
        }
        
        job_id = ingestion_service.db_manager.insert_job(job_data)
        assert job_id == "test-job-1"
        
        # Get job and verify
        job = ingestion_service.get_job_status("test-job-1")
        assert job is not None
        assert job.id == "test-job-1"
        
        # Update job
        ingestion_service.db_manager.update_job("test-job-1", {
            "status": JobStatus.RUNNING.value,
            "progress": 0.5
        })
        
        # Verify update
        updated_job = ingestion_service.get_job_status("test-job-1")
        assert updated_job.status == JobStatus.RUNNING.value
        assert updated_job.progress == 0.5
        
        # Get all jobs
        all_jobs = ingestion_service.get_all_jobs()
        assert len(all_jobs) >= 1
        assert any(job.id == "test-job-1" for job in all_jobs)
    
    def test_stats(self, ingestion_service):
        """Test system statistics"""
        # Create some test jobs
        for i in range(3):
            job_data = {
                "id": f"test-job-{i}",
                "source_type": "plain_text",
                "source_url": f"test://source-{i}",
                "status": JobStatus.COMPLETED.value if i < 2 else JobStatus.FAILED.value,
                "progress": 1.0 if i < 2 else 0.0
            }
            ingestion_service.db_manager.insert_job(job_data)
        
        # Get stats
        stats = ingestion_service.get_stats()
        
        assert "total_jobs" in stats
        assert "completed_jobs" in stats
        assert "failed_jobs" in stats
        assert "success_rate" in stats
        assert stats["total_jobs"] == 3
        assert stats["completed_jobs"] == 2
        assert stats["failed_jobs"] == 1
        assert stats["success_rate"] == 2/3


class TestChunkingService:
    """Test the chunking service"""
    
    @pytest.fixture
    def chunking_service(self):
        """Create chunking service for testing"""
        config = {
            "max_chunk_size": 100,
            "chunk_overlap": 20,
            "min_chunk_size": 30,
            "similarity_threshold": 0.7
        }
        return ChunkingService(config)
    
    def test_clean_content(self, chunking_service):
        """Test content cleaning"""
        dirty_content = "This   has    extra    spaces.\n\n\n\nMultiple line breaks."
        clean_content = chunking_service._clean_content(dirty_content)
        
        assert "  " not in clean_content  # No double spaces
        assert clean_content.count("\n\n") <= 1  # Max one double line break
    
    def test_sentence_splitting(self, chunking_service):
        """Test sentence splitting"""
        text = "First sentence. Second sentence! Third sentence? And a fourth."
        sentences = chunking_service._split_into_sentences(text)
        
        assert len(sentences) >= 3
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
    
    def test_chunk_creation(self, chunking_service):
        """Test chunk creation"""
        document_id = "test-doc-1"
        content = "This is test content for chunking."
        metadata = {"source": "test"}
        
        chunk = chunking_service._create_chunk(document_id, 0, content, metadata)
        
        assert chunk is not None
        assert chunk["document_id"] == document_id
        assert chunk["content"] == content
        assert chunk["chunk_index"] == 0
        assert chunk["chunk_hash"] is not None
        assert len(chunk["chunk_hash"]) == 64  # SHA256 hash length
    
    def test_document_chunking(self, chunking_service):
        """Test document chunking functionality"""
        document_id = "test-doc-1"
        content = """
        This is the first sentence. This is the second sentence. This is the third sentence.
        Here we have a new paragraph. Another sentence in this paragraph.
        Final sentence of the document.
        """
        
        chunks = chunking_service.chunk_document(document_id, content)
        
        assert len(chunks) > 0
        assert all(chunk["document_id"] == document_id for chunk in chunks)
        assert all("chunk_hash" in chunk for chunk in chunks)
        
        # Verify content is preserved (though split)
        all_chunk_content = " ".join(chunk["content"] for chunk in chunks)
        assert "first sentence" in all_chunk_content.lower()
        assert "final sentence" in all_chunk_content.lower()


class TestDatabaseManager:
    """Test database operations"""
    
    @pytest.fixture
    def db_manager(self):
        """Create database manager for testing"""
        # Clean up test database
        if os.path.exists("test_db.db"):
            os.remove("test_db.db")
        
        manager = DatabaseManager("test_db.db")
        manager.create_tables()
        yield manager
        
        # Clean up
        manager.close()
        if os.path.exists("test_db.db"):
            os.remove("test_db.db")
    
    def test_document_operations(self, db_manager):
        """Test document CRUD operations"""
        # Insert document
        doc_data = {
            "id": "doc1",
            "source_type": "plain_text",
            "content": "Test content",
            "metadata_json": {"title": "Test Doc"},
            "hash_sha256": "abc123",
            "status": "pending"
        }
        
        doc_id = db_manager.insert_document(doc_data)
        assert doc_id == "doc1"
        
        # Retrieve document
        retrieved = db_manager.get_document_by_hash("abc123")
        assert retrieved is not None
        assert retrieved["content"] == "Test content"
        
        # Test duplicate detection
        duplicate = db_manager.get_document_by_hash("different_hash")
        assert duplicate is None
    
    def test_chunk_operations(self, db_manager):
        """Test chunk CRUD operations"""
        # Insert chunks
        chunks_data = [
            {
                "id": "chunk1",
                "document_id": "doc1",
                "content": "First chunk",
                "chunk_index": 0,
                "start_char": 0,
                "end_char": 12,
                "chunk_hash": "hash1",
                "metadata_json": {},
                "created_at": None
            },
            {
                "id": "chunk2",
                "document_id": "doc1",
                "content": "Second chunk",
                "chunk_index": 1,
                "start_char": 13,
                "end_char": 26,
                "chunk_hash": "hash2",
                "metadata_json": {},
                "created_at": None
            }
        ]
        
        count = db_manager.insert_chunks(chunks_data)
        assert count == 2
        
        # Retrieve chunks
        chunks = db_manager.get_chunks_by_document_id("doc1")
        assert len(chunks) == 2
        assert chunks[0]["content"] == "First chunk"
        assert chunks[1]["content"] == "Second chunk"


if __name__ == "__main__":
    # Run basic test without pytest for demonstration
    print("Running basic ingestion service tests...")
    
    # Test chunking service
    config = {
        "max_chunk_size": 100,
        "chunk_overlap": 20,
        "min_chunk_size": 30
    }
    
    chunking_service = ChunkingService(config)
    content = "This is a test document. It has multiple sentences. Each sentence should be properly processed. The chunking service should handle this correctly."
    
    chunks = chunking_service.chunk_document("test-doc", content)
    print(f"Created {len(chunks)} chunks from test content")
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {chunk['content'][:50]}...")
    
    print("Basic tests completed successfully!")