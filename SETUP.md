# Setup Guide

This guide will help you set up and run the Universal Content Ingestion Pipeline.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- pip (Python package manager)
- npm (Node package manager)

## Quick Start

### Option 1: Using the Start Script (Recommended)

```bash
./start.sh
```

This script will automatically:
1. Set up Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Start both servers

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Run the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at http://localhost:8000

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Start the frontend server:
```bash
npm start
```

The frontend UI will be available at http://localhost:3000

### Option 3: Using Docker Compose

```bash
docker-compose up
```

This will start both backend and frontend in containers.

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
```

### Running the Demo

```bash
cd backend
source venv/bin/activate
python demo.py
```

This will demonstrate:
- Text ingestion
- Markdown file ingestion
- Duplicate detection
- Semantic search

## Verifying the Installation

1. Backend Health Check:
```bash
curl http://localhost:8000/health
```

Expected response: `{"status":"healthy"}`

2. Frontend: Open http://localhost:3000 in your browser

3. API Documentation: Visit http://localhost:8000/docs for interactive API documentation

## Configuration

### Backend Configuration (.env)

```env
DATABASE_URL=sqlite:///./content_ingestion.db
LANCE_DB_PATH=./lancedb_data
UPLOAD_DIR=./uploads
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_FILE_SIZE=52428800  # 50MB
```

### Frontend Configuration (.env)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## First Steps

1. **Ingest Content**:
   - Navigate to the "Ingest Content" tab
   - Choose your content type (URL, File, or Text)
   - Submit for ingestion

2. **Monitor Progress**:
   - Watch the progress bar in the Jobs section
   - Jobs update in real-time

3. **View Sources**:
   - Navigate to the "Sources" tab
   - See all ingested content
   - Delete sources if needed

4. **Search**:
   - Navigate to the "Search" tab
   - Enter a search query
   - View semantically similar content

## Supported Content Types

### URLs
- YouTube videos (with transcription from subtitles)
- Web pages (with content extraction)

### Files
- PDF (text, images, tables)
- EPUB (chapters, navigation)
- DOCX (text, images, tables, comments)
- Markdown (.md)
- Plain text (.txt)

### Direct Input
- Paste any text content directly

## Troubleshooting

### Backend Issues

1. **Import errors**:
   - Make sure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Database errors**:
   - Delete `content_ingestion.db` and restart
   - Check write permissions in backend directory

3. **Embedding model download**:
   - First run will download the model (~80MB)
   - Requires internet connection
   - Stored in `~/.cache/torch/sentence_transformers/`

### Frontend Issues

1. **Cannot connect to backend**:
   - Verify backend is running on port 8000
   - Check REACT_APP_API_URL in .env

2. **Build errors**:
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` again

### Performance Issues

1. **Large files**:
   - Files over 50MB may take longer to process
   - Consider splitting large documents

2. **Slow embedding generation**:
   - First-time model download required
   - CPU-based inference (no GPU required)
   - Batch processing is used for efficiency

## Development

### Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core utilities
│   │   ├── models/       # Database models
│   │   └── services/     # Business logic
│   ├── tests/            # Unit tests
│   └── requirements.txt
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/   # React components
│       ├── services/     # API client
│       └── types/        # TypeScript types
└── README.md
```

### Adding New Extractors

1. Create a new extractor in `backend/app/services/extractors/`
2. Inherit from `BaseExtractor`
3. Implement `extract()` and `extract_metadata()` methods
4. Add to `ExtractorFactory` in `extractor_factory.py`
5. Update `SourceDetector` if needed

### Database Migrations

Using Alembic (if you need to modify the schema):

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at http://localhost:8000/docs
3. Run the demo script to verify setup
4. Check logs in the terminal

## Next Steps

- Explore advanced search features
- Try different content types
- Monitor ingestion progress
- Build playlists (coming in Phase 2)
