# Cognisphere

A full-stack learning application with spaced repetition and intelligent content processing.

## Architecture

Cognisphere is built with:
- **Desktop**: Electron + React + TypeScript
- **Backend**: Python with modular architecture
- **Mobile**: React Native (Phase 1: review-only companion)
- **Database**: SQLite + LanceDB for embeddings

## Project Structure

```
cognisphere/
├── desktop/          # Electron + React frontend
│   ├── src/
│   │   ├── electron/   # Electron main process
│   │   ├── renderer/   # React components
│   │   └── utils/      # Shared utilities
│   └── package.json
├── backend/          # Python backend
│   ├── core/
│   │   ├── ingestion/      # Content ingestion
│   │   ├── transformation/ # Content processing
│   │   └── srs/            # Spaced repetition system
│   ├── models/       # Model management
│   ├── data/         # Data access layer
│   ├── sync/         # Sync functionality
│   ├── database/     # Database schemas and migrations
│   ├── config/       # Configuration and hardware detection
│   └── requirements.txt
└── mobile/           # React Native app
    └── package.json
```

## Development Setup

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.9+
- Git

### Desktop App Setup

```bash
cd desktop
npm install
npm run dev
```

This will start the Electron app in development mode with hot-reload.

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Mobile Setup (Phase 1 - Scaffolding Only)

```bash
cd mobile
npm install
# Development to continue in future phases
```

## Building for Production

### Desktop

```bash
cd desktop
npm run build
npm run package
```

This creates distributable installers in `desktop/dist/`.

### Backend

The Python backend is bundled automatically when packaging the desktop app:

```bash
cd backend
pyinstaller cognisphere.spec
```

## Database

The application uses:
- **SQLite**: Primary database for content, cards, and review logs
- **LanceDB**: Vector database for embeddings (all-MiniLM-L6-v2)

Database schema is initialized on first launch.

## Hardware Tiers

The app automatically detects hardware capabilities and selects an appropriate tier:
- **Premium**: 16GB+ RAM, GPU available
- **Standard**: 8-16GB RAM
- **Minimum**: <8GB RAM

Models are downloaded based on the selected tier.

## IPC Communication

The desktop app uses Electron IPC to communicate with the Python backend:
- Frontend → Backend: Commands sent via IPC channels
- Backend → Frontend: Results returned via IPC responses

## License

[License information to be added]
