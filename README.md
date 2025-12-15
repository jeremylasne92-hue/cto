# Knowledge Graph System - Phase 2

A comprehensive knowledge graph system with visual representation, mastery tracking, and multi-platform support.

## Features

- **Backend**: Flask-based REST API with SQLite database
- **Desktop**: Electron + React with D3 force-directed graph visualization
- **Mobile**: React Native read-only companion app
- **Mastery Tracking**: Color-coded progress visualization
- **Integrity Checks**: Automated validation of graph structure
- **Layout Persistence**: Save and restore graph layouts

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server runs on `http://localhost:5000`

### Desktop

```bash
cd desktop
npm install
npm run dev
```

### Mobile

```bash
cd mobile
npm install
npm run ios    # or npm run android
```

## Architecture

```
knowledge-graph/
├── backend/                 # Flask REST API
│   ├── api/                # Flask blueprints
│   ├── core/graph/         # Knowledge graph service
│   ├── database/           # SQLite manager
│   └── tests/              # Unit tests
├── desktop/                # Electron + React app
│   └── src/
│       ├── electron/       # IPC handlers, preload
│       └── renderer/       # React components
└── mobile/                 # React Native app
    └── src/
        ├── screens/        # Mobile screens
        └── services/       # API client
```

## Key Technologies

- **Backend**: Python, Flask, SQLite
- **Desktop**: TypeScript, React, Electron, D3, react-force-graph, Three.js
- **Mobile**: React Native, TypeScript
- **Testing**: pytest (backend), Jest (frontend)

## Documentation

- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development guide with API examples
- [ACCEPTANCE_CRITERIA.md](./ACCEPTANCE_CRITERIA.md) - Feature checklist

## API Endpoints

- `POST /api/knowledge-graph/query` - Query graph with filters
- `POST /api/knowledge-graph/related` - Get related concepts
- `POST /api/knowledge-graph/integrity-check` - Run integrity checks
- `POST /api/concepts` - Create/update concepts
- `DELETE /api/concepts/<id>` - Delete concept
- `POST /api/relations` - Create relations

## Mastery Color System

- 🟢 **Green (>80%)**: Mastered
- 🟡 **Yellow (50-80%)**: Learning
- 🟠 **Orange (20-50%)**: Beginner
- ⚫ **Gray (<20%)**: Not Started

## Testing

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Desktop tests (if configured)
cd desktop
npm test
```

## License

MIT
