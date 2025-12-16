# Cognisphere Development Guide

## Project Overview

Cognisphere is a full-stack learning application with spaced repetition, intelligent content processing, and cross-platform support.

## Technology Stack

### Desktop Application
- **Framework**: Electron 28
- **Frontend**: React 18 + TypeScript 5
- **Build Tool**: Webpack 5
- **Code Quality**: ESLint + Prettier
- **Auto-Update**: electron-updater

### Python Backend
- **Framework**: Flask 3.0
- **Database**: SQLite + LanceDB (optional)
- **Hardware Detection**: psutil, GPUtil
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Packaging**: PyInstaller

### Mobile Application
- **Framework**: React Native 0.73
- **Phase 1**: Scaffolding only (review-only companion)

## Directory Structure

```
cognisphere/
├── desktop/                    # Electron + React app
│   ├── src/
│   │   ├── electron/          # Main process
│   │   │   ├── main.ts        # App entry point
│   │   │   ├── backend-process.ts  # Python backend management
│   │   │   ├── ipc-handlers.ts     # IPC communication
│   │   │   └── preload.ts          # Preload script
│   │   ├── renderer/          # React renderer
│   │   │   ├── App.tsx        # Main React component
│   │   │   ├── index.tsx      # React entry point
│   │   │   ├── index.html     # HTML template
│   │   │   └── styles.css     # Global styles
│   │   └── utils/             # Shared utilities
│   │       └── types.ts       # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.electron.json
│   ├── webpack.renderer.config.js
│   ├── .eslintrc.json
│   └── .prettierrc
├── backend/                    # Python backend
│   ├── config/                # Configuration modules
│   │   ├── hardware_detection.py  # Hardware detection
│   │   └── tier_selection.py      # Tier auto-selection
│   ├── core/                  # Core business logic
│   │   ├── ingestion/         # Content ingestion
│   │   ├── transformation/    # Content processing
│   │   └── srs/               # Spaced repetition
│   ├── database/              # Database management
│   │   ├── sqlite_manager.py  # SQLite operations
│   │   └── lancedb_manager.py # Vector embeddings
│   ├── models/                # ML models
│   │   └── embedding_model.py
│   ├── data/                  # Data access layer
│   │   └── repository.py
│   ├── sync/                  # Sync functionality
│   │   └── sync_manager.py
│   ├── main.py                # Flask app entry point
│   ├── requirements.txt       # Python dependencies
│   └── cognisphere.spec       # PyInstaller spec
└── mobile/                     # React Native app
    ├── src/
    │   └── App.tsx
    ├── package.json
    ├── app.json
    └── index.js
```

## Development Setup

### Prerequisites

- **Node.js**: 18+ and npm/yarn
- **Python**: 3.9+
- **SQLite**: 3.35+
- **Git**: Latest version

### Desktop App

```bash
cd desktop
npm install
npm run build        # Build both renderer and electron
npm run dev          # Development mode with hot-reload
npm run lint         # Run ESLint
npm run format       # Format code with Prettier
```

### Python Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend starts on `http://127.0.0.1:8765`

### Mobile App

```bash
cd mobile
npm install
# iOS
npm run ios
# Android
npm run android
```

## Database Schema

### SQLite Tables

1. **content_sources**: Imported content (PDFs, videos, articles)
2. **content_chunks**: Chunked content for processing
3. **concepts**: Extracted concepts from content
4. **concept_relations**: Relationships between concepts
5. **cards**: Flashcards for spaced repetition
6. **card_srs_state**: SRS algorithm state per card
7. **review_logs**: History of card reviews
8. **sync_log**: Synchronization tracking

### LanceDB

- **embeddings**: Vector embeddings for semantic search (384 dimensions)

## API Endpoints

### Knowledge Graph API (Phase 2)
- `POST /api/knowledge-graph/query` - Filter depth, search term
- `POST /api/knowledge-graph/related` - Semantic neighbor lookup
- `POST /api/knowledge-graph/integrity-check` - Graph integrity validation
- `POST /api/concepts` - Create/Update concept
- `DELETE /api/concepts/<id>` - Delete concept
- `POST /api/relations` - Create relation

### Graph Visualization
- **Library**: `react-force-graph` (WebGL) with Canvas fallback
- **Controls**:
  - **Search**: Filter graph by concept name
  - **Integrity Check**: Validate graph structure
- **Color Coding**:
  - Green: >80% Mastery
  - Yellow: 50-80% Mastery
  - Orange: 20-50% Mastery
  - Gray: <20% Mastery

### Health & Info
- `GET /health` - Health check
- `GET /api/hardware-info` - System hardware information
- `GET /api/tier-info` - Current performance tier
- `GET /api/database-status` - Database status

### Backend Calls (via IPC)
All backend calls go through Electron IPC:
```typescript
window.electronAPI.callBackend('method-name', params)
```

## Hardware Tiers

The app automatically detects hardware and selects a tier:

| Tier | Requirements | Features |
|------|-------------|----------|
| **Premium** | 16GB+ RAM, GPU | Max performance, GPU acceleration |
| **Standard** | 8-16GB RAM | Standard performance, CPU only |
| **Minimum** | <8GB RAM | Reduced features, optimized |

## Build & Package

### Desktop (Production)

```bash
cd desktop
npm run build
npm run package           # All platforms
npm run package:win       # Windows
npm run package:mac       # macOS
npm run package:linux     # Linux
```

Output: `desktop/dist/`

### Python Backend (Bundling)

```bash
cd backend
pyinstaller cognisphere.spec
```

Output: `backend/dist/cognisphere/`

The bundled Python backend is automatically included in the Electron app during packaging.

## Development Workflow

1. **Make changes** in `desktop/src/` or `backend/`
2. **Test locally**:
   - Desktop: `npm run dev`
   - Backend: `python main.py`
3. **Lint & Format**:
   - Desktop: `npm run lint && npm run format`
4. **Build**: `npm run build`
5. **Commit changes** with descriptive messages

## Code Style

- **TypeScript/JavaScript**: Prettier + ESLint
- **Python**: PEP 8 conventions
- **Indentation**: 2 spaces (TS/JS), 4 spaces (Python)
- **Naming**: camelCase (JS), snake_case (Python)

## Testing

(To be implemented in future phases)

## Troubleshooting

### Desktop won't start
- Check Node.js version: `node --version` (should be 18+)
- Clean install: `rm -rf node_modules package-lock.json && npm install`

### Backend errors
- Check Python version: `python --version` (should be 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check logs: `~/.cognisphere/` directory

### Build issues
- Clear build cache: `rm -rf desktop/dist backend/dist`
- Rebuild: `npm run build`

## Contributing

(Guidelines to be added)

## License

MIT
