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