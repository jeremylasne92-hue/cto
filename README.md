# Universal Content Ingestion Pipeline

A comprehensive content ingestion system supporting multiple content sources with local parsing, semantic chunking, and vector-based search.

## Features

### Phase 1 - Core Ingestion Pipeline

1. **Source Detection & Routing**
   - Automatic content type detection (URL, File, Text)
   - Smart routing to appropriate parser
   - Metadata extraction (title, author, duration, date)

2. **Content Extraction**
   - **YouTube**: Video transcription using yt-dlp with subtitle extraction
   - **PDF**: Text, images, tables, and structure extraction using PyMuPDF and pdfplumber
   - **Web Scraping**: HTML parsing with BeautifulSoup4, preserving formatting and links
   - **EPUB**: Chapter extraction with navigation preservation using ebooklib
   - **DOCX**: Text, images, tables, and comments extraction with python-docx
   - **Markdown/Plain Text**: Direct parsing with structure preservation

3. **Semantic Chunking**
   - Smart content splitting (512 tokens with 50-token overlap)
   - Context preservation (chunk type, position, media references)
   - Special handling for code blocks, tables, and structured content

4. **Embedding Generation**
   - Local embedding using all-MiniLM-L6-v2 (384 dimensions)
   - LanceDB for efficient vector storage and semantic search
   - Hash-based deduplication

5. **Content Integrity**
   - SHA-256 hashing of source files
   - Duplicate detection
   - Hash storage in metadata

6. **Ingestion Queue**
   - Concurrent ingestion support
   - Real-time progress tracking with ETA
   - Pause/cancel capability
   - User-friendly error messages

## Architecture

```
backend/
├── app/
│   ├── api/              # FastAPI routes
│   ├── core/             # Core utilities (chunker, embedder, etc.)
│   ├── models/           # SQLAlchemy models
│   ├── services/         # Business logic
│   │   └── extractors/   # Content extractors for each format
│   ├── config.py
│   ├── database.py
│   └── main.py
└── requirements.txt

frontend/
├── public/
├── src/
│   ├── components/       # React components
│   ├── services/         # API client
│   ├── types/            # TypeScript types
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── tsconfig.json
```

## Installation

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the backend server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000
The backend API will be available at http://localhost:8000

## Usage

### Ingesting Content

1. **URL Ingestion** (YouTube or Web Pages)
   - Select "URL" tab
   - Enter the URL
   - Click "Ingest"

2. **File Upload** (PDF, EPUB, DOCX, Markdown, etc.)
   - Select "File" tab
   - Choose your file (up to 50MB)
   - Click "Ingest"

3. **Text Paste**
   - Select "Text" tab
   - Paste your content
   - Click "Ingest"

### Monitoring Progress

- View real-time progress in the "Ingestion Jobs" section
- Progress bar shows percentage complete
- Status indicators: pending, detecting, extracting, chunking, embedding, storing, completed, failed
- Cancel running jobs if needed

### Viewing Sources

- Navigate to the "Sources" tab
- View all ingested content with metadata
- Delete sources when no longer needed

### Semantic Search

- Navigate to the "Search" tab
- Enter your search query
- View semantically similar content chunks
- Results ranked by relevance

## Database Schema

### content_sources
- `id`: Primary key
- `file_path`: Path to source file (if applicable)
- `source_type`: Type of content (youtube, pdf, web, etc.)
- `title`: Extracted title
- `author`: Extracted author
- `hash`: SHA-256 hash for duplicate detection
- `created_at`: Timestamp
- `metadata`: JSON field for additional metadata

### content_chunks
- `id`: Primary key
- `chunk_id`: Unique chunk identifier (hash)
- `source_id`: Foreign key to content_sources
- `text`: Chunk text content
- `chunk_type`: Type of chunk (text, markdown_section, code, table, etc.)
- `position`: Original position in source
- `chunk_order`: Sequential order
- `metadata`: JSON field for chunk-specific metadata

### ingestion_jobs
- `id`: Primary key
- `source_id`: Foreign key to content_sources
- `status`: Job status
- `progress`: Progress (0.0 to 1.0)
- `error_message`: Error details if failed
- `created_at`: Job start time
- `updated_at`: Last update time
- `metadata`: JSON field for job metadata

## API Endpoints

### Ingestion
- `POST /api/v1/ingest/url` - Ingest from URL
- `POST /api/v1/ingest/file` - Upload and ingest file
- `POST /api/v1/ingest/text` - Ingest pasted text

### Jobs
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/{job_id}` - Get job status
- `DELETE /api/v1/jobs/{job_id}` - Cancel job

### Sources
- `GET /api/v1/sources` - List all sources
- `GET /api/v1/sources/{source_id}` - Get source details
- `DELETE /api/v1/sources/{source_id}` - Delete source

### Search
- `POST /api/v1/search` - Semantic search

## Configuration

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./content_ingestion.db
LANCE_DB_PATH=./lancedb_data
UPLOAD_DIR=./uploads
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_FILE_SIZE=52428800
```

## Requirements Met

✅ YouTube video ingestion with transcription  
✅ PDF parsing with text, images, and structure  
✅ Web page scraping with content extraction  
✅ EPUB, DOCX, Markdown support  
✅ Embeddings generated and stored in LanceDB  
✅ Semantic search functionality  
✅ SHA-256 hash verification for duplicates  
✅ UI with progress tracking and cancel option  
✅ Handles 50MB+ files efficiently  

## Future Enhancements (Phase 2)

- Playlist/collection management
- Content sharing capabilities
- Advanced filtering and sorting
- Batch operations
- Export functionality
- Enhanced metadata extraction
- Audio transcription with Whisper
- OCR for images in PDFs
