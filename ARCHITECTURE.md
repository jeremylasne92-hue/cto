# Architecture Documentation

## System Overview

The Universal Content Ingestion Pipeline is a full-stack application designed to ingest, process, and search various types of content using semantic embeddings.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────────┐ │
│  │ Ingestion  │  │  Sources   │  │  Semantic Search      │ │
│  │ Form       │  │  List      │  │  Interface            │ │
│  └────────────┘  └────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  API Layer                           │   │
│  │  /ingest/{url,file,text} | /jobs | /sources | /search │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Ingestion Service                       │   │
│  │  • Source Detection                                  │   │
│  │  • Content Extraction (via Extractors)              │   │
│  │  • Semantic Chunking                                 │   │
│  │  • Embedding Generation                              │   │
│  │  • Storage Management                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  ┌──────────────────┐         ┌─────────────────────────┐  │
│  │   SQLite DB      │         │      LanceDB            │  │
│  │  • Sources       │         │  • Vector Embeddings    │  │
│  │  • Chunks        │         │  • Semantic Search      │  │
│  │  • Jobs          │         │                         │  │
│  └──────────────────┘         └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology Stack:**
- React 18 with TypeScript
- Axios for API communication
- Inline CSS for styling

**Components:**

1. **IngestionForm**
   - Purpose: User interface for content submission
   - Features: URL/File/Text input modes
   - Interactions: Calls backend ingestion endpoints

2. **JobsList**
   - Purpose: Real-time job monitoring
   - Features: Progress bars, status indicators, cancel functionality
   - Updates: Polls backend every 2 seconds

3. **SourcesList**
   - Purpose: Display ingested content
   - Features: Grid view, delete functionality, metadata display

4. **SearchInterface**
   - Purpose: Semantic search UI
   - Features: Query input, result ranking, similarity scores

### 2. Backend Layer

**Technology Stack:**
- FastAPI (async web framework)
- SQLAlchemy (ORM)
- Pydantic (data validation)
- Background Tasks for async processing

**Core Modules:**

#### Source Detector
```python
Purpose: Identify content type and route to appropriate extractor
Inputs: URL, file path, or text content
Outputs: Source type and metadata dictionary
Logic:
  - YouTube: Regex pattern matching for video URLs
  - Web: URL validation
  - File: Extension-based detection
  - Text: Default fallback
```

#### Content Extractors

Base architecture using Strategy Pattern:
```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(source, metadata) -> Dict
    @abstractmethod
    def extract_metadata(source) -> Dict
```

**Implemented Extractors:**

1. **YouTubeExtractor**
   - Uses: yt-dlp for video info and subtitle extraction
   - Extracts: Title, author, transcription, duration
   - Fallback: Description if no subtitles available

2. **PDFExtractor**
   - Uses: PyMuPDF (text) + pdfplumber (tables)
   - Extracts: Text, images, tables, metadata
   - Preserves: Document structure, page numbers

3. **WebExtractor**
   - Uses: BeautifulSoup4 with lxml parser
   - Extracts: Main content, title, author, links
   - Filters: Scripts, styles, navigation elements

4. **EPUBExtractor**
   - Uses: ebooklib
   - Extracts: Chapters, navigation, metadata
   - Preserves: Chapter hierarchy

5. **DOCXExtractor**
   - Uses: python-docx
   - Extracts: Text, tables, images, comments
   - Metadata: Author, title, creation date

6. **MarkdownExtractor**
   - Uses: markdown library
   - Extracts: Raw markdown + HTML conversion
   - Preserves: Heading structure, frontmatter

7. **TextExtractor**
   - Direct text processing
   - No special parsing

#### Semantic Chunker

**Algorithm:**
```
1. Split text into tokens (words)
2. Create chunks of configurable size (default: 512 tokens)
3. Add overlap between chunks (default: 50 tokens)
4. Generate unique chunk IDs (SHA-256 hash)
5. Preserve metadata (position, order, type)

Special handling:
  - Markdown: Split by headings
  - Code: Fixed line count chunks
  - Tables: Keep intact as special chunks
```

**Chunking Strategy:**
```
Chunk 1: [Tokens 0-512]
Chunk 2: [Tokens 462-974]  (50-token overlap)
Chunk 3: [Tokens 924-1436] (50-token overlap)
...
```

#### Embedding Generator

**Singleton Pattern Implementation:**
```python
Model: sentence-transformers/all-MiniLM-L6-v2
Dimensions: 384
Processing: Batch encoding for efficiency
Caching: Model loaded once, reused for all requests
```

**Process:**
```
Text → Tokenization → Neural Network → 384-dim vector
```

#### Vector Store (LanceDB)

**Schema:**
```python
{
  "chunk_id": string (unique identifier),
  "source_id": int32 (reference to source),
  "text": string (chunk content),
  "vector": list<float32>[384] (embedding),
  "chunk_type": string (type of content),
  "chunk_order": int32 (sequential position)
}
```

**Search Algorithm:**
```
1. Generate query embedding
2. Compute cosine similarity with all vectors
3. Return top K results sorted by distance
4. Optional: Filter by source_id
```

#### Content Hasher

**Purpose:** Duplicate detection and content integrity

**Hashing Strategy:**
- Files: SHA-256 of file bytes
- URLs: SHA-256 of URL string
- Text: SHA-256 of content string

**Duplicate Detection:**
```
1. Calculate content hash
2. Query database for existing hash
3. If exists: Return existing source
4. If not: Proceed with ingestion
```

### 3. Data Flow

#### Ingestion Flow

```
User Input (URL/File/Text)
    ↓
API Endpoint (/ingest/*)
    ↓
Create IngestionJob (status: pending)
    ↓
Background Task Started
    ↓
Source Detection (status: detecting)
    ↓
Calculate Content Hash
    ↓
Check for Duplicates
    ↓
    ├─ Duplicate Found → Return existing source
    └─ New Content → Continue
        ↓
Content Extraction (status: extracting)
    ↓
Create ContentSource record
    ↓
Semantic Chunking (status: chunking)
    ↓
Generate Embeddings (status: embedding)
    ↓
Store in SQLite (chunks metadata)
    ↓
Store in LanceDB (embeddings) (status: storing)
    ↓
Complete (status: completed)
```

#### Search Flow

```
User Query
    ↓
Generate Query Embedding (384-dim vector)
    ↓
LanceDB Vector Search (cosine similarity)
    ↓
Retrieve Top K Results
    ↓
Return to User (text + metadata + distance)
```

### 4. Database Schema

#### SQLite (Relational Data)

**content_sources**
```sql
CREATE TABLE content_sources (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    source_type TEXT NOT NULL,
    title TEXT,
    author TEXT,
    hash TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);
```

**content_chunks**
```sql
CREATE TABLE content_chunks (
    id INTEGER PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,
    source_id INTEGER REFERENCES content_sources(id),
    text TEXT NOT NULL,
    chunk_type TEXT NOT NULL,
    position INTEGER NOT NULL,
    chunk_order INTEGER NOT NULL,
    metadata JSON
);
```

**ingestion_jobs**
```sql
CREATE TABLE ingestion_jobs (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES content_sources(id),
    status TEXT DEFAULT 'pending',
    progress REAL DEFAULT 0.0,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);
```

#### LanceDB (Vector Data)

**embeddings table**
```
Schema: Apache Arrow
Fields:
  - chunk_id: string
  - source_id: int32
  - text: string
  - vector: fixed_size_list<float32>[384]
  - chunk_type: string
  - chunk_order: int32

Index: IVF-PQ for fast similarity search
```

### 5. API Design

**RESTful Endpoints:**

```
POST   /api/v1/ingest/url      - Ingest from URL
POST   /api/v1/ingest/file     - Upload and ingest file
POST   /api/v1/ingest/text     - Ingest text content
GET    /api/v1/jobs            - List all jobs
GET    /api/v1/jobs/{id}       - Get job status
DELETE /api/v1/jobs/{id}       - Cancel job
GET    /api/v1/sources         - List all sources
GET    /api/v1/sources/{id}    - Get source details
DELETE /api/v1/sources/{id}    - Delete source
POST   /api/v1/search          - Semantic search
GET    /                       - Root endpoint
GET    /health                 - Health check
```

**Response Format:**
```json
{
  "job_id": 123,
  "status": "completed",
  "progress": 1.0,
  "source_id": 456
}
```

### 6. Performance Considerations

**Scalability:**
- Background task processing for non-blocking ingestion
- Batch embedding generation for efficiency
- LanceDB optimized for large-scale vector search

**Memory Management:**
- Streaming file uploads
- Chunking prevents loading entire documents in memory
- Generator patterns for large datasets

**Concurrency:**
- FastAPI async support
- Multiple concurrent ingestion jobs
- Non-blocking I/O operations

**Optimization Opportunities:**
- Add Redis for job queue management
- Celery for distributed task processing
- GPU acceleration for embedding generation
- PostgreSQL for better concurrent write performance

### 7. Error Handling

**Levels:**
1. **API Level**: HTTP status codes, error responses
2. **Service Level**: Try-catch blocks, job status updates
3. **Extractor Level**: Graceful degradation, fallback options

**Job Status Flow:**
```
pending → detecting → extracting → chunking → embedding → storing → completed
                ↓
              failed (with error_message)
                ↓
            cancelled (user action)
```

### 8. Security Considerations

**Current Implementation:**
- CORS enabled (configure for production)
- File size limits (50MB default)
- No authentication (add for production)

**Production Recommendations:**
- Add JWT authentication
- Rate limiting
- Input sanitization
- HTTPS only
- Environment-based CORS configuration

### 9. Future Architecture Enhancements

**Phase 2 Features:**
- Playlist/Collection management
- User authentication and multi-tenancy
- Real-time collaboration
- Advanced filtering and faceted search
- Content versioning
- Webhook integrations

**Scalability Improvements:**
- Microservices architecture
- Message queue (RabbitMQ/Kafka)
- Distributed storage (S3/MinIO)
- Kubernetes deployment
- CDN for static content

## Deployment Architecture

**Development:**
```
Local machine → SQLite + LanceDB local files
```

**Docker:**
```
docker-compose → Backend + Frontend containers → Shared volumes
```

**Production (Recommended):**
```
Load Balancer
    ↓
FastAPI instances (scaled horizontally)
    ↓
PostgreSQL (primary + replicas)
    ↓
LanceDB (distributed storage)
    ↓
Redis (caching + job queue)
```
