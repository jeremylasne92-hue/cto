# Quick Start Guide

Get started with the Universal Content Ingestion Pipeline in 5 minutes.

## Prerequisites Check

```bash
python3 check_requirements.py
```

## Installation (Choose one method)

### Method 1: Automatic Setup (Recommended)

```bash
./start.sh
```

This script will:
- Set up Python virtual environment
- Install all dependencies
- Start both backend and frontend servers

### Method 2: Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend (in a new terminal):**
```bash
cd frontend
npm install
npm start
```

### Method 3: Docker

```bash
docker-compose up
```

## Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## First Steps

### 1. Ingest Text Content

1. Open http://localhost:3000
2. Click "Text" tab
3. Paste some text
4. Click "Ingest"
5. Watch the progress bar

### 2. Try YouTube Ingestion

1. Click "URL" tab
2. Paste a YouTube URL: `https://www.youtube.com/watch?v=VIDEO_ID`
3. Click "Ingest"
4. Wait for transcription extraction

### 3. Upload a File

1. Click "File" tab
2. Choose a PDF, EPUB, DOCX, or Markdown file
3. Click "Ingest"
4. Monitor progress

### 4. Search Your Content

1. Click "Search" tab
2. Enter a search query
3. View semantically similar results

## Try the Demo

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

## Run Tests

```bash
cd backend
source venv/bin/activate
pytest
```

## Common Issues

**"Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check `REACT_APP_API_URL` in `frontend/.env`

**"Module not found"**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**"Port already in use"**
- Backend: Change port in `uvicorn app.main:app --port 8001`
- Frontend: Change port: `PORT=3001 npm start`

## What's Next?

- Read [SETUP.md](SETUP.md) for detailed configuration
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Review [README.md](README.md) for full feature list

## Support

For issues:
1. Check troubleshooting in [SETUP.md](SETUP.md)
2. Run demo script to verify installation
3. Check API docs at http://localhost:8000/docs
