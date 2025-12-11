# Universal Ingestion Service with Pedagogy Engine

A comprehensive document ingestion pipeline service that processes multiple source types, normalizes content, chunks documents semantically, and stores embeddings for vector similarity search. Now includes an AI-driven pedagogy engine for generating quizzes and mind maps from ingested content.

## Features

### Supported Source Types
- **YouTube Videos**: Audio extraction with pytube + Whisper transcription
- **PDF Documents**: Text extraction with PyMuPDF 
- **Web Pages**: Content extraction with requests + BeautifulSoup
- **Markdown Files**: Markdown to plain text conversion
- **Plain Text Files**: Direct text processing

### Core Capabilities
- **SHA256 Hash Verification**: Per-source and per-chunk deduplication
- **Semantic Chunking**: Configurable overlap using NLTK sentence splits + similarity-based grouping
- **Vector Embeddings**: sentence-transformers all-MiniLM-L6-v2 embeddings
- **Vector Storage**: LanceDB for efficient similarity search
- **Background Processing**: FastAPI background tasks for async ingestion
- **REST API**: Complete CRUD interface for job management

### Pedagogy Engine (NEW)
- **Quiz Generation**: MCQ, Fill-in-the-Blank, and Matching questions from ingested content
- **Mind Map Generation**: Hierarchical concept maps with configurable depth and branching
- **Hybrid Model Selection**: Automatic selection between local models (Mistral-7B, Phi-2) and cloud API
- **Hardware-Aware**: Benchmarks CPU, RAM, and GPU to select optimal model
- **Smart Fallback**: Automatically falls back to cloud API when local resources insufficient
- **See [PEDAGOGY_ENGINE.md](PEDAGOGY_ENGINE.md) for detailed documentation**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Source        │    │   Normalized     │    │   Semantic      │
│   Adapters      │───▶│   Document       │───▶│   Chunking      │
│                 │    │   Schema         │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Search        │    │   Vector DB      │    │   Embeddings    │
│   API           │◀───│   (LanceDB)      │◀───│   Generation    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites

**System Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg python3-dev

# macOS
brew install ffmpeg

# Windows
# Download ffmpeg from https://ffmpeg.org/download.html
```

**Python Dependencies:**
```bash
pip install -r requirements.txt
```

**NLTK Data (automatically downloaded):**
- punkt (sentence tokenizer)
- punkt_tab (enhanced sentence tokenizer)

### Environment Setup

Create `.env` file:
```bash
# Database
SQLITE_DB_PATH=ingestion.db
LANCEDB_PATH=lancedb

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Chunking
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=100
MIN_CHUNK_SIZE=100
SIMILARITY_THRESHOLD=0.7

# YouTube
YOUTUBE_WHISPER_MODEL=base
YOUTUBE_DEVICE=auto

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## Usage

### Starting the Service

```bash
# Development mode
python main.py

# Production mode
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Start Ingestion
```http
POST /ingest
Content-Type: application/json

{
    "source_type": "markdown",
    "source_url": "/path/to/document.md",
    "config": {
        "max_chunk_size": 1000,
        "chunk_overlap": 100,
        "similarity_threshold": 0.7
    }
}
```

#### Check Job Status
```http
GET /status/{job_id}
```

#### List All Jobs
```http
GET /jobs?limit=100
```

#### Get Document Chunks
```http
GET /jobs/{job_id}/chunks
```

#### Search Similar Content
```http
GET /search?query=machine learning&limit=10&filter_source_type=pdf
```

#### System Statistics
```http
GET /stats
```

#### Generate Quiz (Pedagogy Engine)
```http
POST /pedagogy/quiz
Content-Type: application/json

{
    "source_id": "doc-123",
    "config": {
        "quiz_type": "mcq",
        "num_questions": 5,
        "difficulty": "medium",
        "include_explanations": true
    }
}
```

#### Get Quiz
```http
GET /pedagogy/quiz/{quiz_id}
```

#### Generate Mind Map
```http
POST /pedagogy/mindmap
Content-Type: application/json

{
    "source_id": "doc-123",
    "config": {
        "max_depth": 4,
        "max_children_per_node": 7,
        "include_summaries": true
    }
}
```

#### Get Mind Map
```http
GET /pedagogy/mindmap/{mindmap_id}
```

#### Check Model Status
```http
GET /pedagogy/models/status
```

### Example Usage

#### Ingest a PDF
```bash
curl -X POST "http://localhost:8000/ingest" \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "pdf",
       "source_url": "https://arxiv.org/pdf/1706.03762.pdf"
     }'
```

#### Search for Content
```bash
curl "http://localhost:8000/search?query=transformer%20architecture"
```

## Configuration

### Chunking Parameters

```python
config = {
    "max_chunk_size": 1000,        # Max characters per chunk
    "chunk_overlap": 100,          # Overlap between chunks  
    "min_chunk_size": 100,         # Minimum chunk size
    "similarity_threshold": 0.7    # Semantic similarity threshold
}
```

### Embedding Model

The service uses `sentence-transformers/all-MiniLM-L6-v2` by default, which:
- Has 384 dimensions
- Is optimized for sentence embeddings
- Provides good balance of speed and quality

### Hash Verification

SHA256 hashes are generated for:
- **Document Level**: `hash(content + source_url)`
- **Chunk Level**: `hash(chunk_content)`

This enables:
- Duplicate document detection
- Chunk deduplication
- Content integrity verification

## Resource Requirements

### Minimum System Requirements
- **CPU**: 2+ cores recommended for parallel processing
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 10GB+ for models and data
- **Network**: Stable internet for YouTube downloads

### Model Downloads

**Whisper Models (YouTube):**
- `tiny`: ~39 MB - Fast, lower quality
- `base`: ~74 MB - Balanced speed/quality  
- `small`: ~244 MB - Better quality
- `medium`: ~769 MB - High quality
- `large`: ~1550 MB - Best quality

**Sentence Transformers:**
- all-MiniLM-L6-v2: ~91 MB

**Total Download**: ~200-1600 MB depending on Whisper model choice

### Processing Times

| Source Type | Processing Time (1MB content) |
|-------------|-------------------------------|
| Plain Text | < 1 second |
| Markdown | < 1 second |
| Web Page | 1-5 seconds |
| PDF | 5-10 seconds |
| YouTube (5min video) | 30-120 seconds |

## Testing

### Run All Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --cov=src

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### End-to-End Test Example

```python
import asyncio
from src.models import IngestionRequest, SourceType
from src.services.ingestion import IngestionService

async def test_ingestion():
    service = IngestionService()
    
    request = IngestionRequest(
        source_type=SourceType.MARKDOWN,
        source_url="path/to/document.md"
    )
    
    job_id = await service.ingest_document(request)
    
    # Check status
    job = service.get_job_status(job_id)
    print(f"Job status: {job.status}")
    
    # Get chunks when complete
    if job.status == "completed":
        chunks = service.get_document_chunks(job.document_id)
        print(f"Generated {len(chunks)} chunks")

# Run test
asyncio.run(test_ingestion())
```

## API Reference

### Models

#### IngestionRequest
```python
{
    "source_type": "youtube|pdf|web_page|markdown|plain_text",
    "source_url": "string",
    "config": {
        "max_chunk_size": 1000,
        "chunk_overlap": 100,
        "similarity_threshold": 0.7
    }
}
```

#### Job Status
```python
{
    "job_id": "uuid",
    "status": "pending|running|completed|failed|cancelled",
    "source_type": "string",
    "source_url": "string",
    "progress": 0.0-1.0,
    "document_id": "uuid|null",
    "chunk_count": "int|null",
    "error_message": "string|null"
}
```

### Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Resource Not Found
- `500`: Internal Server Error

Error responses include detailed messages:
```json
{
    "detail": "Detailed error message explaining what went wrong"
}
```

## Development

### Project Structure
```
src/
├── adapters/          # Source adapters
│   ├── base.py       # Base adapter class
│   ├── youtube.py    # YouTube + Whisper
│   ├── pdf.py        # PDF processing
│   ├── web_page.py   # Web scraping
│   ├── markdown.py   # Markdown conversion
│   └── plain_text.py # Text processing
├── api/              # FastAPI endpoints
├── models/           # Pydantic models
├── services/         # Core business logic
│   ├── database.py   # SQLite operations
│   ├── chunking.py   # Semantic chunking
│   ├── vector_db.py  # Vector embeddings
│   └── ingestion.py  # Main pipeline
└── config/           # Configuration
```

### Adding New Adapters

1. Create adapter class inheriting from `BaseAdapter`
2. Implement required methods:
   - `get_source_type()`: Return source type enum
   - `validate_source(url)`: Validate URL/path
   - `extract_content(url)`: Extract content + metadata
3. Register in `AdapterFactory`

```python
from .base import BaseAdapter
from ..models import SourceType

class CustomAdapter(BaseAdapter):
    def get_source_type(self):
        return SourceType.CUSTOM
    
    def validate_source(self, source_url: str) -> bool:
        return source_url.startswith("custom://")
    
    async def extract_content(self, source_url: str):
        content = "extracted content"
        metadata = {"title": "Custom Source"}
        return content, metadata
```

## Troubleshooting

### Common Issues

**Whisper Model Download Failures:**
```bash
# Manually download model
python -c "import whisper; whisper.load_model('base')"
```

**FFmpeg Not Found:**
```bash
# Check installation
ffmpeg -version

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Set path if needed
export PATH=$PATH:/usr/local/bin
```

**Memory Issues with Large Documents:**
- Reduce `max_chunk_size`
- Increase `timeout_seconds`
- Process documents in batches

**Vector Search Performance:**
- Adjust `nprobes` parameter in vector_db.py
- Optimize LanceDB configuration
- Consider using smaller embedding models

### Logging

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

Logs include:
- Ingestion progress tracking
- Error details with stack traces
- Performance metrics
- Database operations

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  ingestion-svc:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SQLITE_DB_PATH=/data/ingestion.db
      - LANCEDB_PATH=/data/lancedb
    volumes:
      - ./data:/data
    restart: unless-stopped
```

### Scaling Considerations

- Use multiple API workers: `uvicorn --workers 4`
- Implement Redis for job queue (instead of in-memory)
- Use PostgreSQL for production database
- Set up monitoring and alerting
- Consider GPU acceleration for embeddings

## License

MIT License - see LICENSE file for details.