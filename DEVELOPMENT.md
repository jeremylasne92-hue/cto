# Knowledge Graph Development Guide

## Overview

The Knowledge Graph system is a Phase 2 implementation that provides visual representation and management of learning concepts with mastery tracking across backend, desktop, and mobile clients.

## Architecture

### Backend

The backend is built with Flask and SQLite, providing RESTful APIs for graph operations.

#### Key Components

1. **SQLiteManager** (`backend/database/sqlite_manager.py`)
   - Manages database schema with migration-safe guards
   - Tables: concepts, relations, review_logs, concept_mastery, concept_layout_cache
   - Provides CRUD operations with proper indexing

2. **KnowledgeGraphService** (`backend/core/graph/knowledge_graph_service.py`)
   - Core business logic for graph operations
   - Validation: rejects duplicate names, prevents orphan relations
   - Mastery aggregation from review logs
   - Integrity checks: orphans, cycles, broken refs
   - D3-ready payload generation with color-coded mastery

3. **Flask Blueprints** (`backend/api/knowledge_graph.py`)
   - `/api/knowledge-graph/query` - Query graph with filters
   - `/api/knowledge-graph/related` - Get related concepts
   - `/api/knowledge-graph/integrity-check` - Run integrity checks
   - `/api/concepts` - CRUD for concepts
   - `/api/relations` - CRUD for relations

#### Running the Backend

```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

Environment variables:
- `PORT` - Server port (default: 5000)
- `HOST` - Server host (default: 127.0.0.1)
- `DATABASE_PATH` - SQLite database path (default: data/knowledge_graph.db)

### Desktop Client

Built with Electron + React + TypeScript, featuring D3-based graph visualization.

#### Key Components

1. **IPC Bridge** (`desktop/src/electron/ipc-handlers.ts`, `preload.ts`)
   - Bridges renderer to backend HTTP API
   - Supports all HTTP verbs with query params
   - Hardware detection for WebGL capability

2. **React Components**
   - `KnowledgeGraphPanel` - Main graph visualization
   - `ConceptSidebar` - Concept details and editing
   - `GraphControls` - Filters and search
   - `MasteryLegend` - Color-coded mastery legend

3. **Custom Hook** (`useKnowledgeGraph.ts`)
   - Manages graph state and API calls
   - Auto-refresh support
   - Layout persistence

#### Running the Desktop Client

```bash
cd desktop
npm install
npm run dev
```

#### D3 Graph Controls

- **Pan**: Click and drag background
- **Zoom**: Mouse wheel
- **Select Node**: Click on node
- **Edit Node**: Right-click or use sidebar
- **Create Relation**: Use sidebar after selecting node
- **3D Mode**: Toggle in controls (requires WebGL)
- **Filters**: Search, depth, prerequisites, dependencies, mastery levels

### Mobile Client

React Native read-only view with concept browsing and neighbor inspection.

#### Running the Mobile Client

```bash
cd mobile
npm install
npm run ios    # or npm run android
```

## Database Schema

### concepts
- `id` (TEXT, PRIMARY KEY) - UUID
- `name` (TEXT, UNIQUE) - Concept name
- `description` (TEXT) - Description
- `metadata` (TEXT) - JSON metadata
- `created_at`, `updated_at` (TIMESTAMP)

### relations
- `id` (TEXT, PRIMARY KEY) - UUID
- `source_id`, `target_id` (TEXT) - Foreign keys to concepts
- `relation_type` (TEXT) - 'prerequisite', 'dependency', 'related'
- `strength` (REAL) - 0.0-1.0
- `metadata` (TEXT) - JSON metadata

### concept_mastery
- `user_id` (INTEGER) - Foreign key to users
- `concept_id` (TEXT) - Foreign key to concepts
- `mastery_percent` (REAL) - 0-100
- `review_count` (INTEGER)
- `last_assessed` (TIMESTAMP)

### concept_layout_cache
- `concept_id` (TEXT, PRIMARY KEY)
- `x`, `y`, `z` (REAL) - Layout coordinates

## Mastery Color System

The system uses color-coded mastery levels:

- **Green (#10b981)**: > 80% - Mastered
- **Yellow (#fbbf24)**: 50-80% - Learning
- **Orange (#f97316)**: 20-50% - Beginner
- **Gray (#6b7280)**: < 20% - Not Started

Mastery is calculated from the most recent 20 review logs (or all if fewer), giving a weighted average of correct answers.

## API Examples

### Query Graph

```bash
POST /api/knowledge-graph/query
Content-Type: application/json

{
  "user_id": 1,
  "depth": 3,
  "search_term": "python",
  "use_webgl": true
}
```

### Create Concept

```bash
POST /api/concepts
Content-Type: application/json

{
  "name": "Python Basics",
  "description": "Introduction to Python programming",
  "metadata": {"category": "programming"}
}
```

### Create Relation

```bash
POST /api/relations
Content-Type: application/json

{
  "source_id": "concept-uuid-1",
  "target_id": "concept-uuid-2",
  "relation_type": "prerequisite",
  "strength": 0.8
}
```

### Run Integrity Check

```bash
POST /api/knowledge-graph/integrity-check
```

## Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

Or run individual test:

```bash
python -m pytest tests/test_knowledge_graph_service.py -v
```

### Test Coverage

- Concept creation with duplicate name rejection
- Relation creation with orphan prevention
- Self-loop prevention
- Cascade deletion
- Mastery aggregation and color assignment
- Integrity check for orphans and cycles
- Graph filtering (search, depth, mastery)
- Layout persistence

## Development Tips

1. **Database Migrations**: The SQLiteManager includes migration-safe guards. New columns/tables are added idempotently using `IF NOT EXISTS` and `add_column_safe`.

2. **WebGL Fallback**: The desktop client detects GPU availability and falls back to Canvas rendering if WebGL is unavailable.

3. **Layout Persistence**: Graph layouts are auto-saved every 5 seconds to maintain user-arranged positions.

4. **Integrity Checks**: Run periodic integrity checks to detect orphan relations, cycles, and broken references.

5. **Performance**: For large graphs (>1000 nodes), use depth filtering and search to reduce rendering load.

## Future Enhancements

- LanceDB integration for semantic concept search
- Real-time collaboration features
- Advanced relation strength calculation based on co-review patterns
- Graph analytics and insights
- Export/import functionality
- Concept templates and categories
