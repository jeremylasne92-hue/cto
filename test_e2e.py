#!/usr/bin/env python3
"""
Simple end-to-end test script for the Universal Ingestion Service
Tests markdown ingestion as an example of the full pipeline
"""

import asyncio
import tempfile
import os
import sys
import logging

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import IngestionRequest, SourceType, IngestionConfig
from services.ingestion import IngestionService


async def test_markdown_ingestion():
    """Test end-to-end markdown ingestion"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create test markdown content
    markdown_content = """# Universal Ingestion Service Test

This is a test document for the universal ingestion service.

## Overview

The service processes multiple source types including:
- YouTube videos with transcription
- PDF documents  
- Web pages
- Markdown files
- Plain text files

## Features

### Semantic Chunking
The service uses NLTK for sentence splitting and semantic grouping to create coherent chunks.

### Vector Embeddings  
Embeddings are generated using sentence-transformers and stored in LanceDB for similarity search.

### Duplicate Detection
SHA256 hashes ensure content uniqueness across sources and chunks.

## Conclusion

This test demonstrates the complete ingestion pipeline working correctly.
"""
    
    # Create temporary markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
        temp_file.write(markdown_content)
        temp_file_path = temp_file.name
    
    try:
        logger.info(f"Testing ingestion of markdown file: {temp_file_path}")
        
        # Initialize ingestion service
        config = {
            "db_path": "test_e2e.db",
            "lancedb_path": "test_e2e_lancedb",
            "chunking_config": {
                "max_chunk_size": 300,
                "chunk_overlap": 50,
                "min_chunk_size": 50,
                "similarity_threshold": 0.6
            }
        }
        
        service = IngestionService(config)
        
        # Create ingestion request
        request = IngestionRequest(
            source_type=SourceType.MARKDOWN,
            source_url=temp_file_path,
            config=IngestionConfig(
                max_chunk_size=300,
                chunk_overlap=50,
                min_chunk_size=50,
                similarity_threshold=0.6
            )
        )
        
        # Start ingestion
        job_id = await service.ingest_document(request)
        logger.info(f"Started ingestion job: {job_id}")
        
        # Wait for completion (simulate async monitoring)
        max_wait = 30  # seconds
        wait_interval = 1  # seconds
        waited = 0
        
        while waited < max_wait:
            job = service.get_job_status(job_id)
            logger.info(f"Job status: {job.status}, progress: {job.progress:.2f}")
            
            if job.status in ["completed", "failed", "cancelled"]:
                break
            
            await asyncio.sleep(wait_interval)
            waited += wait_interval
        
        # Check final result
        final_job = service.get_job_status(job_id)
        logger.info(f"Final job status: {final_job.status}")
        
        if final_job.status == "completed":
            logger.info(f"Document ID: {final_job.document_id}")
            logger.info(f"Chunk count: {final_job.chunk_count}")
            
            # Get chunks
            if final_job.document_id:
                chunks = service.get_document_chunks(final_job.document_id)
                logger.info(f"Retrieved {len(chunks)} chunks from database")
                
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    logger.info(f"Chunk {i}: {chunk['content'][:100]}...")
                
                # Test search functionality
                search_results = service.search_similar("semantic chunking", limit=5)
                logger.info(f"Search found {len(search_results)} similar chunks")
                
                if search_results:
                    logger.info(f"Best match: {search_results[0]['content'][:100]}...")
            
            # Get system stats
            stats = service.get_stats()
            logger.info(f"System stats: {stats['total_jobs']} total jobs")
            
            logger.info("✅ End-to-end test completed successfully!")
            return True
            
        else:
            logger.error(f"❌ Job failed with status: {final_job.status}")
            if final_job.error_message:
                logger.error(f"Error: {final_job.error_message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            os.unlink(temp_file_path)
            service.db_manager.close()
            
            # Clean up test databases
            for db_file in ["test_e2e.db", "test_e2e_lancedb.db", "_lancedb.landb"]:
                if os.path.exists(db_file):
                    os.remove(db_file)
                    
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


async def main():
    """Run the end-to-end test"""
    print("🚀 Starting Universal Ingestion Service End-to-End Test")
    print("=" * 60)
    
    success = await test_markdown_ingestion()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)