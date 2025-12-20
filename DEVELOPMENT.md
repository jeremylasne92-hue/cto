
# Development Guide - Profile & Social API Phase 2

This document provides detailed technical information for developers working on the Social Learning Platform.

## 🏗️ Architecture Deep Dive

### Backend Architecture

#### 1. Database Layer (`backend/database/sqlite_manager.py`)
- **SQLiteManager**: Thread-safe database manager using thread-local connections
- **Connection Management**: Automatic connection pooling and transaction handling
- **Helper Views**: Pre-computed views for efficient public data access
- **Cascade Deletion**: Automatic cleanup of related records

**Key Features:**
- Thread-safe operations with `threading.local()`
- Context managers for automatic transaction handling
- JSON field parsing for interests and certifications
- Optimized queries with proper indexing

#### 2. Business Logic Layer (`backend/core/social/profile_service.py`)
- **ProfileService**: Central business logic coordinator
- **Privacy Engine**: Automatic data filtering based on user settings
- **Metrics Aggregation**: Smart calculation from review logs
- **Social Logic**: Follow/unfollow with privacy validation

**Privacy Enforcement Strategy:**
```python
def get_user_profile(self, user_id: int, include_private: bool = False):
    if include_private:
        # Full access for authenticated user
        return self._get_full_profile(user_id)
    else:
        # Filtered access for public API
        return self._get_filtered_profile(user_id)
```

#### 3. API Layer (`backend/api/profile.py`)
- **Blueprint Pattern**: Modular Flask blueprint for profile endpoints
- **Request Validation**: Input validation and sanitization
- **Error Handling**: Comprehensive error responses
- **CORS Support**: Cross-origin requests for web/mobile clients

### Database Schema Design

#### Privacy-First Design
The database schema is designed with privacy as a primary concern:

1. **Field-Level Privacy**: Each privacy-sensitive field has a corresponding boolean flag
2. **Skill Visibility**: Individual skills marked as public/private at the record level
3. **Helper Views**: Pre-filtered views for public data access
4. **Cascade Protection**: Foreign key constraints ensure data integrity

#### Performance Optimizations
- **Indexes**: Automatic indexes on frequently queried columns
- **Views**: Materialized views for public skill summaries
- **JSON Fields**: Efficient storage of arrays (interests, certifications)
- **Connection Pooling**: Reused database connections

## 🔒 Privacy Implementation Details

### Multi-Layer Privacy Protection

#### Layer 1: Database Level
```sql
-- Helper view for public skills only
CREATE VIEW public_user_skills AS
SELECT user_id, skill_id, mastery_level, updated_at
FROM user_skills
WHERE visibility = TRUE;
```

#### Layer 2: Service Level
```python
def get_public_skills(self, handle: str) -> List[Dict]:
    # Only query from public view
    return self.db.execute_query(
        "SELECT skill_id, mastery_level FROM public_user_skills WHERE user_id = ?",
        (user_id,)
    )
```

#### Layer 3: API Level
```python
@profile_bp.route('/public/<handle>')
def get_public_profile(handle):
    # API endpoint that only exposes public data
    profile = profile_service.get_public_profile_by_handle(handle)
    # Never includes private fields
    return jsonify({'profile': profile})
```

### Privacy Testing Strategy
Comprehensive tests ensure no private data leakage:

```python
def test_private_skills_never_leak(self, profile_service, test_users):
    """Critical security test"""
    # Add both public and private skills
    profile_service.update_skill(user_id, 'public_skill', 3, visibility=True)
    profile_service.update_skill(user_id, 'private_skill', 4, visibility=False)
    
    # Get public skills
    public_skills = profile_service.db.get_user_skills(user_id, public_only=True)
    
    # Verify private skills are filtered out
    skill_ids = [skill['skill_id'] for skill in public_skills]
    assert 'private_skill' not in skill_ids
```

## 📊 Metrics Aggregation Engine

### Smart Streak Calculation
The streak calculation accounts for realistic learning patterns:

```python
def _calculate_streak(self, user_id: int, max_days: int = 365) -> int:
    # Get study sessions
    sessions = self._get_study_sessions(user_id, max_days)
    
    # Allow for weekend gaps
    consecutive_days = self._count_consecutive_days(sessions, allow_weekends=True)
    
    return consecutive_days
```

### XP Aggregation
Smart XP calculation that considers:
- Base XP from review logs
- Bonus multipliers for consistency
- Cap on daily XP to prevent gaming

### Hours Calculation
Accurate time tracking:
- Converts minutes to hours
- Accounts for partial sessions
- Handles timezone differences

## 🎯 Skill Comparison Algorithm

### Similarity Scoring
The skill comparison uses multiple factors:

1. **Common Skills**: Skills both users possess
2. **Skill Levels**: Relative mastery levels
3. **Learning Gaps**: Opportunities for growth
4. **Recommendations**: AI-powered learning suggestions

### Recommendation Engine
```python
def _generate_learning_recommendations(self, user1_skills, user2_skills):
    recommendations = []
    
    for skill, user1_level in user1_skills.items():
        user2_level = user2_skills.get(skill, 0)
        
        if user1_level > user2_level + 2:  # Significant gap
            recommendations.append({
                'skill_id': skill,
                'recommended_for': user2_id,
                'reason': f'{user1_level - user2_level} levels ahead',
                'type': 'learning_opportunity'
            })
    
    return recommendations[:5]  # Top 5 recommendations
```

## 🧪 Testing Framework

### Test Categories

#### 1. Security Tests (Critical)
- **Privacy Leakage Tests**: Ensure no private data exposure
- **Access Control Tests**: Verify proper authorization
- **Input Validation Tests**: Test against injection attacks

#### 2. Business Logic Tests
- **Profile CRUD Operations**: Test all create/read/update/delete operations
- **Social Features**: Follow/unfollow lifecycle tests
- **Metrics Calculation**: Verify accuracy of aggregation logic

#### 3. Integration Tests
- **API Endpoint Tests**: Test full request/response cycles
- **Database Integration**: Test transaction handling and rollbacks
- **Cross-Platform Tests**: Test desktop and mobile compatibility

### Running Tests
```bash
# Run all tests with coverage
pytest backend/tests/ -v --cov=backend/ --cov-report=html

# Run specific security test
pytest backend/tests/test_profile_service.py::TestProfileService::test_private_skills_never_leak -v

# Run performance tests
pytest backend/tests/test_profile_service.py -k "performance" -v
```

## 💻 Desktop Application Architecture

### Electron + React Structure
```
desktop/
├── src/
│   ├── main/              # Electron main process
│   │   ├── main.js        # Window management, IPC
│   │   └── preload.js     # Secure bridge to renderer
│   └── renderer/          # React application
│       ├── App.tsx        # Main application component
│       ├── components/    # Reusable components
│       └── services/      # API communication
```

### State Management
- **React State**: Local component state for UI interactions
- **API State**: Centralized API state management
- **Persistence**: Local storage for user preferences

### IPC Bridge (Desktop Security)
```javascript
// Secure communication between main and renderer
preload.js exposes only necessary APIs:
- save-file: Save profile data locally
- open-file: Import profile data
- get-app-version: App version info
```

## 📱 Mobile Application Architecture

### React Navigation Structure
```
mobile/
├── src/
│   ├── navigation/
│   │   ├── AppNavigator.js    # Main navigation setup
│   │   └── tabNavigator.js    # Bottom tab configuration
│   ├── screens/
│   │   ├── PublicProfileScreen.js    # Read-only public profiles
│   │   ├── ProfileScreen.js          # Editable user profile
│   │   └── HomeScreen.js             # Dashboard
│   └── services/
│       └── api.js                    # API communication
```

### Deep Linking Support
```javascript
// Handle deep links for public profiles
const handleDeepLink = (url) => {
  const match = url.match(/profile\/(\w+)/);
  if (match) {
    navigation.navigate('PublicProfile', { handle: match[1] });
  }
};
```

### Async Storage
- **User Preferences**: Local storage for app settings
- **Recent Profiles**: Cached recently viewed profiles
- **Offline Support**: Basic offline functionality

## 🔧 Development Workflow

### Code Style Guidelines

#### Python
- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type annotations for better IDE support
- **Docstrings**: Comprehensive docstrings for all public methods
- **Error Handling**: Always handle exceptions gracefully

#### JavaScript/TypeScript
- **ESLint**: Use configured linting rules
- **Prettier**: Consistent code formatting
- **Type Safety**: Prefer TypeScript for type checking
- **Component Structure**: Functional components with hooks

### Database Migrations

When schema changes are needed:

1. **Backup**: Always backup production data
2. **Migration Scripts**: Create reversible migration scripts
3. **Testing**: Test migrations on development data
4. **Rollback Plan**: Have a plan to revert if needed

Example migration:
```python
def migrate_add_privacy_fields():
    """Add privacy fields to existing profiles"""
    db.execute("""
        ALTER TABLE user_profiles 
        ADD COLUMN privacy_bio BOOLEAN DEFAULT TRUE
    """)
    # Update existing records
    db.execute("""
        UPDATE user_profiles 
        SET privacy_bio = CASE WHEN bio != '' THEN TRUE ELSE FALSE END
    """)
```

### API Development

#### Endpoint Design Principles
1. **RESTful**: Follow REST conventions
2. **Consistent**: Use consistent response formats
3. **Documented**: Include comprehensive API documentation
4. **Versioned**: Use URL versioning for breaking changes

#### Response Format Standard
```python
{
    "success": true|false,
    "data": {},           # Response data (if successful)
    "error": "string",    # Error message (if failed)
    "message": "string"   # Additional context
}
```

## 🚀 Performance Optimization

### Database Performance
- **Indexing**: Index foreign keys and frequently queried columns
- **Query Optimization**: Use EXPLAIN to analyze query performance
- **Connection Pooling**: Reuse database connections
- **Batch Operations**: Use batch inserts/updates when possible

### API Performance
- **Response Caching**: Cache frequently accessed public profiles
- **Pagination**: Implement pagination for large datasets
- **Compression**: Enable gzip compression for responses
- **Rate Limiting**: Implement rate limiting for public endpoints

### Frontend Performance
- **Lazy Loading**: Load components and data on demand
- **Memoization**: Use React.memo and useMemo for expensive operations
- **Virtual Scrolling**: For large lists (followers, skills)
- **Progressive Loading**: Load critical content first

## 🔍 Monitoring & Debugging

### Logging Strategy
```python
import logging

# Structured logging with context
logger.info("User profile updated", extra={
    'user_id': user_id,
    'fields_updated': list(fields.keys()),
    'privacy_changes': privacy_changes
})
```

### Health Checks
```python
@profile_bp.route('/health')
def health_check():
    try:
        # Test database connection
        db.execute_query("SELECT 1")
        
        # Test external dependencies
        # (gamification service, etc.)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error("Health check failed", exc_info=True)
        return jsonify({'status': 'unhealthy'}), 503
```

### Debug Endpoints
- **Profile Debug**: `GET /api/profile/debug/<user_id>` - Full profile data
- **Database Stats**: `GET /api/profile/debug/stats` - Database statistics
- **Privacy Test**: `GET /api/profile/debug/privacy/<user_id>` - Privacy filtering test

## 🔐 Security Considerations

### Input Validation
```python
def validate_skill_data(data):
    schema = {
        'skill_id': {'type': 'string', 'minlength': 1, 'maxlength': 50},
        'mastery_level': {'type': 'integer', 'min': 1, 'max': 5},
        'visibility': {'type': 'boolean'}
    }
    return validate(schema, data)
```

### SQL Injection Prevention
- **Parameterized Queries**: Always use parameterized statements
- **Input Sanitization**: Clean user inputs before database operations
- **Connection Security**: Use secure database connections

### API Security
- **Rate Limiting**: Prevent abuse of public endpoints
- **CORS Configuration**: Restrict origins for production
- **Input Size Limits**: Prevent large payload attacks

## 📋 Development Checklist

### Before Committing
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Privacy tests specifically pass
- [ ] Documentation updated
- [ ] No sensitive data in logs
- [ ] Error handling implemented
- [ ] Performance tested

### For Privacy Changes
- [ ] Privacy tests updated and passing
- [ ] Database views updated
- [ ] Public API filtering verified
- [ ] Migration scripts created
- [ ] Security review completed

### For New Features
- [ ] Database schema updated
- [ ] Business logic implemented
- [ ] API endpoints created
- [ ] Frontend components updated
- [ ] Unit tests written
- [ ] Integration tests updated
- [ ] Documentation added

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Issues
```python
# Check connection status
def debug_db_connection():
    try:
        result = db.execute_query("SELECT 1")
        print("Database connection: OK")
    except Exception as e:
        print(f"Database connection failed: {e}")
```

#### Privacy Filter Not Working
```python
# Debug privacy filtering
def debug_privacy_filter(user_id):
    full_profile = get_profile(user_id, include_private=True)
    public_profile = get_profile(user_id, include_private=False)
    
    print("Full profile fields:", list(full_profile.keys()))
    print("Public profile fields:", list(public_profile.keys()))
```

#### Performance Issues
```python
# Analyze slow queries
def debug_slow_queries():
    # Enable query logging
    db.execute("PRAGMA compile_options")
    
    # Check index usage
    result = db.execute_query("EXPLAIN QUERY PLAN SELECT * FROM user_skills WHERE user_id = ?", (1,))
    print("Query plan:", result)
```

This development guide provides comprehensive technical details for maintaining and extending the Social Learning Platform. Always refer to this when implementing new features or debugging issues.

---


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

