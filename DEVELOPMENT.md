# Knowledge Graph Development Guide

## Overview

The Knowledge Graph system provides a comprehensive solution for managing and visualizing interconnected concepts with user mastery tracking. This guide covers the API usage, visualization controls, and development patterns.

## Architecture

### Backend Components

1. **SQLiteManager** (`backend/database/sqlite_manager.py`)
   - Extended SQLite management with migration-safe guards
   - Tables: `concepts`, `relations`, `concept_mastery`, `concept_layout_cache`, `concept_embeddings`

2. **KnowledgeGraphService** (`backend/core/graph/knowledge_graph_service.py`)
   - Core business logic for graph operations
   - CRUD operations with validation
   - Integrity checking and semantic search
   - Mastery aggregation from review logs

3. **LanceDBManager** (`backend/core/graph/lance_db_manager.py`)
   - Vector embedding storage and semantic neighbor lookup
   - Simplified implementation using SQLite for demonstration

4. **Flask API** (`backend/api/knowledge_graph.py`)
   - RESTful endpoints for all graph operations
   - D3-ready node/edge payloads
   - Error handling and validation

### Desktop Components

1. **IPC Handlers** (`desktop/src/electron/ipc-handlers.ts`)
   - Communication bridge between main and renderer processes
   - HTTP API calls to backend
   - Hardware capability detection

2. **React Hook** (`desktop/src/renderer/hooks/useKnowledgeGraph.ts`)
   - State management for graph data
   - API integration and error handling
   - Type definitions for graph structures

3. **Main Panel** (`desktop/src/renderer/components/KnowledgeGraphPanel.tsx`)
   - D3.js visualization with WebGL/Canvas fallback
   - Interactive concept editing
   - Color-coded mastery levels

### Mobile Components

1. **Mobile Screen** (`mobile/src/screens/KnowledgeGraphScreen.tsx`)
   - Read-only knowledge graph viewer
   - Concept detail navigation
   - Mastery color indicators

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
Currently no authentication required. User identification via `user_id` parameter.

### Endpoints

#### Knowledge Graph Query
```http
POST /api/query
```

**Request Body:**
```json
{
  "depth": 2,
  "search_term": "machine learning",
  "concept_ids": [1, 2, 3],
  "user_id": "user123",
  "use_webgl": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "nodes": [...],
    "links": [...],
    "stats": {
      "total_concepts": 10,
      "total_relations": 15,
      "mastery_distribution": {
        "green": 3,
        "yellow": 4,
        "orange": 2,
        "gray": 1
      }
    }
  },
  "meta": {
    "search_term": "machine learning",
    "depth": 2,
    "use_webgl": true
  }
}
```

#### Create Concept
```http
POST /api/concepts
```

**Request Body:**
```json
{
  "name": "Machine Learning",
  "description": "Algorithms that learn from data",
  "content": "Detailed content about ML...",
  "parent_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "name": "Machine Learning",
    "description": "Algorithms that learn from data",
    "content": "Detailed content about ML...",
    "parent_id": 1,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

#### Update Concept
```http
PUT /api/concepts/{id}
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Delete Concept
```http
DELETE /api/concepts/{id}?force=false
```

#### Create Relation
```http
POST /api/concepts/{source_id}/relations
```

**Request Body:**
```json
{
  "target_concept_id": 5,
  "relation_type": "prerequisite",
  "strength": 2.5
}
```

#### Search Concepts
```http
POST /api/search
```

**Request Body:**
```json
{
  "query": "neural networks",
  "limit": 10
}
```

#### Find Related Concepts
```http
POST /api/related
```

**Request Body:**
```json
{
  "concept_id": 1,
  "limit": 10
}
```

#### Integrity Check
```http
POST /api/integrity-check
```

**Request Body:**
```json
{
  "concept_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "total_issues": 0,
    "issues": {
      "orphans": [],
      "cycles": [],
      "broken_references": [],
      "duplicate_ids": [],
      "strength_anomalies": []
    },
    "checked_at": "2025-01-01T00:00:00Z"
  }
}
```

#### Update Mastery
```http
POST /api/mastery/{user_id}/{concept_id}
```

**Request Body (Option 1 - Direct mastery):**
```json
{
  "mastery_percentage": 85.5
}
```

**Request Body (Option 2 - From review scores):**
```json
{
  "review_scores": [0.6, 0.7, 0.8, 0.9]
}
```

## Database Schema

### Core Tables

#### concepts
```sql
CREATE TABLE concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_id INTEGER REFERENCES concepts(id)
);
```

#### relations
```sql
CREATE TABLE relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_concept_id INTEGER NOT NULL,
    target_concept_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL DEFAULT 'prerequisite',
    strength REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_concept_id) REFERENCES concepts(id),
    FOREIGN KEY (target_concept_id) REFERENCES concepts(id)
);
```

### Mastery Tables

#### concept_mastery
```sql
CREATE TABLE concept_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    concept_id INTEGER NOT NULL,
    mastery_percentage REAL DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    last_assessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, concept_id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);
```

#### concept_layout_cache
```sql
CREATE TABLE concept_layout_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_id INTEGER NOT NULL,
    layout_data TEXT NOT NULL, -- JSON string
    layout_algorithm TEXT DEFAULT 'force-directed',
    zoom_level REAL DEFAULT 1.0,
    viewport_x REAL DEFAULT 0.0,
    viewport_y REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(concept_id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);
```

### Vector Storage

#### concept_embeddings
```sql
CREATE TABLE concept_embeddings (
    concept_id INTEGER PRIMARY KEY,
    embedding_vector TEXT NOT NULL, -- JSON array
    embedding_model TEXT DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);
```

## D3 Visualization Guide

### Node Structure
```typescript
interface GraphNode {
  id: number;
  name: string;
  description: string;
  content: string;
  parent_id?: number;
  created_at: string;
  updated_at: string;
  mastery: number;           // 0-100
  review_count: number;
  last_assessed?: string;
  color: 'green' | 'yellow' | 'orange' | 'gray';
  prerequisites?: number[];   // IDs of prerequisite concepts
  dependencies?: number[];    // IDs of concepts that depend on this
  val?: number;               // Node size (auto-calculated)
  fontSize?: number;          // Font size (auto-calculated)
}
```

### Link Structure
```typescript
interface GraphLink {
  source: number;      // Source concept ID
  target: number;      // Target concept ID
  type: string;        // Relation type (e.g., 'prerequisite')
  strength: number;    // Relation strength (0-5)
  created_at: string;
}
```

### Mastery Color System

- **Green**: 80-100% mastery (Mastered)
- **Yellow**: 50-80% mastery (Learning)
- **Orange**: 20-50% mastery (Struggling)
- **Gray**: 0-20% mastery (Not Started)

### WebGL vs Canvas

The system automatically selects the rendering mode:

1. **WebGL Rendering** (Preferred for Premium tier)
   - Better performance for large graphs
   - Hardware-accelerated
   - Use `react-force-graph-2d` with WebGL enabled

2. **Canvas Rendering** (Fallback for Standard tier)
   - Compatible with older hardware
   - Lower memory usage
   - Fallback when WebGL unavailable

### Interactive Features

#### Node Interactions
- **Click**: Select concept, show details in sidebar
- **Hover**: Highlight connected concepts
- **Drag**: Manual repositioning

#### Keyboard Shortcuts
- **Delete**: Remove selected concept
- **Escape**: Clear selection
- **F**: Focus on selected node

#### Filtering Options
- By mastery level (All, Green, Yellow, Orange, Gray)
- By search term
- By concept ID list

#### Layout Controls
- Force-directed layout (default)
- Zoom and pan
- Reset view

## Development Workflow

### Running the Backend

1. **Install dependencies:**
   ```bash
   pip install flask flask-cors
   ```

2. **Run the server:**
   ```bash
   python main.py
   ```

3. **Run tests:**
   ```bash
   python -m pytest tests/test_knowledge_graph_service.py -v
   ```

### Running the Desktop App

1. **Install dependencies:**
   ```bash
   cd desktop
   npm install
   ```

2. **Start development mode:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

### Running the Mobile App

1. **Install dependencies:**
   ```bash
   cd mobile
   npm install
   ```

2. **Run on iOS/Android:**
   ```bash
   npx react-native run-ios    # iOS
   npx react-native run-android # Android
   ```

## Integration Patterns

### Adding New Concept Types
```python
# Extend the concept creation validation
def create_specialized_concept(self, concept_type: str, **kwargs):
    if concept_type == "lesson":
        kwargs['content_template'] = self._get_lesson_template()
    elif concept_type == "quiz":
        kwargs['assessment_data'] = self._get_quiz_structure()
    
    return self.create_concept(**kwargs)
```

### Custom Relation Types
```python
# Add new relation types to the schema
VALID_RELATION_TYPES = [
    'prerequisite',
    'dependency',
    'related_to',
    'contradicts',
    'supports'
]
```

### Mastery Calculation Customization
```python
# Override mastery calculation in service
def calculate_mastery(self, user_id: str, concept_id: int, review_data: dict):
    # Custom algorithm based on review patterns
    weights = {
        'accuracy': 0.4,
        'speed': 0.2,
        'consistency': 0.2,
        'recency': 0.2
    }
    
    mastery_score = sum(
        review_data[metric] * weight
        for metric, weight in weights.items()
    )
    
    return mastery_score * 100
```

## Performance Considerations

### Large Graph Optimization
- Implement graph clustering for >1000 nodes
- Use level-of-detail rendering
- Enable graph lazy loading

### Database Optimization
- Regular VACUUM operations
- Index optimization on frequently queried columns
- Connection pooling for high concurrency

### Memory Management
- Implement graph data caching
- Use virtualization for large lists
- Monitor memory usage in mobile apps

## Troubleshooting

### Common Issues

1. **Database Migration Errors**
   ```bash
   # Reset database (⚠️ destroys all data)
   rm knowledge_graph.db
   python -c "from backend.core.graph.knowledge_graph_service import KnowledgeGraphService; KnowledgeGraphService().db_manager.migrate_database()"
   ```

2. **IPC Communication Failures**
   - Check Electron main process initialization
   - Verify preload script loading
   - Check API endpoint accessibility

3. **WebGL Performance Issues**
   - Force Canvas mode via hardware detection
   - Reduce graph complexity for testing
   - Check GPU driver compatibility

### Debug Mode
```bash
export DEBUG=true
python main.py
```

Enable debug logging in desktop app:
```typescript
const DEBUG = true;
if (DEBUG) {
  console.log('Graph data:', graphData);
}
```

## Testing Strategy

### Unit Tests
- Concept CRUD operations
- Relation validation
- Integrity check algorithms
- Mastery calculation

### Integration Tests
- API endpoint responses
- Database migration behavior
- IPC communication flow

### End-to-End Tests
- User workflow testing
- Graph visualization interactions
- Mobile navigation flows

## Contributing Guidelines

1. **Code Style**: Follow existing patterns and naming conventions
2. **Testing**: Add unit tests for new features
3. **Documentation**: Update API docs for new endpoints
4. **Migration Safety**: Ensure backward compatibility
5. **Performance**: Consider scalability implications

## Deployment

### Backend Deployment
- Use environment variables for configuration
- Implement proper logging and monitoring
- Set up database backup strategy

### Desktop App Distribution
- Code signing for production builds
- Auto-update mechanism
- Performance monitoring

### Mobile App Store Deployment
- Platform-specific optimizations
- App store compliance
- Privacy policy updates