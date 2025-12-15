# Development Guide

## Project Structure

```
/home/engine/project/
├── backend/
│   ├── database/
│   │   └── sqlite_manager.py      # Database layer with schema
│   ├── core/
│   │   └── social/
│   │       └── profile_service.py # Business logic layer
│   ├── api/
│   │   └── profile.py             # Flask REST API endpoints
│   └── ipc_bridge.py              # Electron IPC integration
├── desktop/
│   └── src/
│       ├── renderer/
│       │   ├── App.tsx            # Main desktop app
│       │   └── components/        # React components
│       └── types/
│           └── profile.ts         # TypeScript type definitions
├── mobile/
│   └── src/
│       └── screens/
│           └── PublicProfileScreen.tsx  # Mobile profile viewer
├── tests/
│   └── test_profile_service.py    # Unit tests
├── main.py                        # Flask application entry point
├── README.md                      # User documentation
└── DEVELOPMENT.md                 # This file
```

## Technology Stack

### Backend
- **Python 3.x** - Core language
- **Flask** - Web framework
- **SQLite** - Database
- **flask-cors** - CORS support for API

### Frontend
- **React** - Desktop UI framework
- **TypeScript** - Type-safe JavaScript
- **React Native** - Mobile framework
- **Electron** - Desktop app wrapper

## Setting Up Development Environment

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
pip install flask flask-cors
python main.py
```

The API will be available at `http://localhost:5000`

### Desktop Setup
```bash
cd desktop
npm install
npm run dev
```

### Mobile Setup
```bash
cd mobile
npm install
npx react-native run-android  # or run-ios
```

## Database Management

### Schema Initialization
The database schema is automatically initialized when `SQLiteManager` is instantiated. The `init_database()` method creates all tables, indexes, and views.

### Manual Database Operations
```python
from backend.database.sqlite_manager import SQLiteManager

db = SQLiteManager('app.db')

# Create a user
user_id = db.create_user('testuser', 'public')

# Add profile data
db.upsert_profile(user_id, bio='Test bio', interests='coding')

# Add skills
db.upsert_skill(user_id, 'python', 'Python', 0.85, 'public')

# Log study time
db.add_review_log(user_id, 60)  # 60 minutes
```

### Views
The database includes helper views:
- `public_skill_summaries` - Pre-filtered public skills for efficient querying

## API Development

### Adding New Endpoints

1. Add the route to `backend/api/profile.py`:
```python
@profile_bp.route('/api/profile/new-feature', methods=['POST'])
@require_user_id
def new_feature(user_id):
    data = request.json or {}
    # Implementation
    return jsonify(result), 200
```

2. Add corresponding service method in `backend/core/social/profile_service.py`:
```python
def new_feature_logic(self, user_id: int, param: str) -> Dict[str, Any]:
    # Business logic here
    return result
```

3. Update IPC bridge if needed in `backend/ipc_bridge.py`:
```python
def _handle_new_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return self.profile_service.new_feature_logic(
        data.get('user_id'),
        data.get('param')
    )
```

### Authentication
Currently using simple header-based authentication with `X-User-Id`. For production:
- Implement JWT tokens
- Add session management
- Integrate OAuth providers

## Testing

### Running Tests
```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_profile_service.py

# Run with coverage
pip install coverage
coverage run -m unittest discover tests
coverage report
```

### Writing Tests
Tests use temporary SQLite databases that are cleaned up after each test:

```python
def setUp(self):
    self.db_fd, self.db_path = tempfile.mkstemp()
    self.db = SQLiteManager(self.db_path)
    self.service = ProfileService(self.db)

def tearDown(self):
    os.close(self.db_fd)
    os.unlink(self.db_path)
```

### Test Coverage
Key areas to test:
- Privacy enforcement (private data not leaked)
- Follow/unfollow lifecycle
- Skill comparison accuracy
- Metrics aggregation
- Edge cases (duplicate follows, self-follow prevention)

## Privacy Implementation

### Service Layer Enforcement
Privacy is enforced in `ProfileService.get_public_profile()`:

```python
if profile:
    if not profile.get('privacy_bio'):
        result['bio'] = profile.get('bio')
    if not profile.get('privacy_interests'):
        result['interests'] = profile.get('interests')
```

### Skills Privacy
Skills have per-item visibility:
```python
def get_user_skills(self, user_id: int, include_private: bool = False):
    if include_private:
        # Return all skills
    else:
        # Only return skills with visibility='public'
```

### Adding New Private Fields
1. Add privacy flag to `user_profiles` table
2. Update `upsert_profile()` to handle the flag
3. Update `get_public_profile()` to respect the flag
4. Add tests for privacy enforcement

## Frontend Development

### Desktop Components
- `ProfileDashboard` - Main profile view with metrics
- `SkillsManager` - Skill editing interface
- `FollowersTab` - Social connections management
- `ComparisonModal` - Skill comparison UI

### API Integration
Components use `fetch` to call API endpoints:

```typescript
const response = await fetch('http://localhost:5000/api/profile/me', {
  headers: { 'X-User-Id': userId.toString() }
});
const data = await response.json();
```

### Mobile Deep Linking
Configure deep links in your app:

**iOS (Info.plist)**:
```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>app</string>
    </array>
  </dict>
</array>
```

**Android (AndroidManifest.xml)**:
```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="app" android:host="profile" />
</intent-filter>
```

## Performance Optimization

### Database Indexes
The schema includes indexes on frequently queried columns:
- `user_follows(follower_id)`
- `user_follows(followee_id)`
- `user_skills(user_id)`
- `review_logs(user_id)`

### Query Optimization
Use views for complex queries:
```sql
CREATE VIEW public_skill_summaries AS
SELECT user_id, skill_id, skill_name, mastery
FROM user_skills
WHERE visibility = 'public'
```

### Caching Strategy
Consider implementing:
- Redis for session storage
- Cache public profiles with TTL
- Aggregate metrics on background schedule

## Error Handling

### API Errors
```python
try:
    result = profile_service.some_operation()
    return jsonify(result), 200
except ValueError as e:
    return jsonify({'error': str(e)}), 400
except Exception as e:
    return jsonify({'error': 'Internal server error'}), 500
```

### Database Errors
```python
try:
    with self.get_connection() as conn:
        # Database operations
except sqlite3.IntegrityError:
    # Handle constraint violations
except sqlite3.OperationalError:
    # Handle database locks, etc.
```

## Deployment

### Production Considerations
1. **Database**: Migrate to PostgreSQL for production
2. **Authentication**: Implement JWT tokens
3. **HTTPS**: Use SSL certificates
4. **Rate Limiting**: Add API rate limits
5. **Logging**: Implement structured logging
6. **Monitoring**: Add health checks and metrics

### Environment Variables
```bash
export DATABASE_URL=postgresql://user:pass@host/db
export SECRET_KEY=your-secret-key
export API_PORT=5000
export DEBUG=false
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
```

## Troubleshooting

### Common Issues

**Database locked error**:
- SQLite doesn't handle concurrent writes well
- Use connection pooling or migrate to PostgreSQL

**CORS errors in browser**:
- Ensure flask-cors is properly configured
- Check allowed origins in CORS settings

**IPC bridge not responding**:
- Verify the bridge is initialized in main process
- Check message channel names match exactly

**Skills not appearing in public profile**:
- Verify skill visibility is set to 'public'
- Check privacy flags in user_profiles table

## Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for public methods

### TypeScript/React
- Use functional components with hooks
- Prefer interfaces over types
- Use explicit return types for functions
- Follow React best practices (memo, useCallback for optimization)

## Contributing

1. Create feature branch from `main`
2. Write tests for new features
3. Ensure all tests pass
4. Update documentation
5. Submit pull request with clear description

## Support

For questions or issues:
- Check the README.md first
- Review test cases for usage examples
- Consult API endpoint documentation
