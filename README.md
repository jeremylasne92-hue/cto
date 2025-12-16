# Social Learning Platform - Profile & Social API Phase 2

A comprehensive social learning platform that enables users to create profiles, track learning metrics, manage skills with privacy controls, and connect with other learners through a follow system and skill comparison features.

## 🚀 Features

### Profile Management
- **User Profiles**: Complete profile system with bio, interests, and learning style
- **Privacy Controls**: Granular privacy settings for each profile field
- **Skill Management**: Add, update, and manage skills with visibility settings
- **Metrics Tracking**: Hours studied, XP points, streaks, and certifications

### Social Learning
- **Follow/Unfollow System**: Connect with other learners
- **Skill Comparison**: Compare skills with other users and get learning recommendations
- **Public Profiles**: Share profile data with privacy controls
- **Followers/Following Lists**: Manage social connections

### Privacy & Security
- **Field-level Privacy**: Control visibility of bio, interests, and learning style
- **Skill Privacy**: Choose which skills are public vs private
- **Public API**: Safe external access to public profile data
- **Data Filtering**: Automatic privacy filtering for public endpoints

## 🏗️ Architecture

### Backend
- **Flask API**: RESTful endpoints for all profile operations
- **SQLite Database**: Lightweight database with optimized schema
- **Profile Service**: Business logic layer for profile operations
- **Privacy Engine**: Automatic data filtering based on privacy settings

### Desktop Application
- **Electron + React**: Cross-platform desktop app
- **Tabbed Interface**: Profile, Skills, Social, and Compare sections
- **Real-time Updates**: Live profile editing and social interactions

### Mobile Application
- **React Native**: iOS and Android compatibility
- **Navigation Stack**: Smooth navigation between screens
- **Deep Linking**: Handle profile links from external sources
- **Read-only Profiles**: Public profile viewing on mobile

## 📋 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    handle TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_private BOOLEAN DEFAULT FALSE
);
```

### User Profiles Table
```sql
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY,
    bio TEXT DEFAULT '',
    interests TEXT DEFAULT '[]', -- JSON array
    learning_style TEXT DEFAULT '',
    privacy_bio BOOLEAN DEFAULT TRUE,
    privacy_interests BOOLEAN DEFAULT TRUE,
    privacy_learning_style BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### User Skills Table
```sql
CREATE TABLE user_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill_id TEXT NOT NULL,
    mastery_level INTEGER DEFAULT 0,
    visibility BOOLEAN DEFAULT TRUE, -- TRUE = public, FALSE = private
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, skill_id)
);
```

### User Metrics Table
```sql
CREATE TABLE user_metrics (
    user_id INTEGER PRIMARY KEY,
    hours_studied REAL DEFAULT 0.0,
    xp_total INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    certifications TEXT DEFAULT '[]', -- JSON array
    last_study_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### User Follows Table
```sql
CREATE TABLE user_follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id INTEGER NOT NULL,
    followee_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (followee_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(follower_id, followee_id)
);
```

### Review Logs Table (for metrics aggregation)
```sql
CREATE TABLE review_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    study_duration REAL DEFAULT 0.0, -- in minutes
    xp_earned INTEGER DEFAULT 0,
    study_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 🔧 API Endpoints

### Profile Management

#### POST `/api/profile/upsert`
Create or update a user profile.

**Request Body:**
```json
{
    "user_id": 1,
    "handle": "johndoe",
    "bio": "Learning enthusiast",
    "interests": ["Python", "Machine Learning"],
    "learning_style": "Visual",
    "is_private": false
}
```

**Response:**
```json
{
    "success": true,
    "message": "Profile upserted successfully",
    "profile": {
        "user": {...},
        "profile": {...},
        "skills": [...],
        "metrics": {...}
    }
}
```

#### POST `/api/profile/privacy`
Update profile privacy settings.

**Request Body:**
```json
{
    "user_id": 1,
    "privacy_settings": {
        "privacy_bio": true,
        "privacy_interests": false,
        "privacy_learning_style": true
    }
}
```

#### POST `/api/profile/skills/update`
Update user skills with visibility settings.

**Request Body:**
```json
{
    "user_id": 1,
    "skills": [
        {
            "skill_id": "python",
            "mastery_level": 4,
            "visibility": true
        },
        {
            "skill_id": "javascript",
            "mastery_level": 3,
            "visibility": false
        }
    ]
}
```

#### POST `/api/profile/metrics`
Get or update user metrics.

**Request Body:**
```json
{
    "user_id": 1,
    "update_from_logs": true
}
```

### Social Features

#### POST `/api/profile/follow`
Follow a user.

**Request Body:**
```json
{
    "follower_id": 1,
    "followee_id": 2
}
```

**Response:**
```json
{
    "success": true,
    "message": "Successfully followed user"
}
```

#### POST `/api/profile/unfollow`
Unfollow a user.

**Request Body:**
```json
{
    "follower_id": 1,
    "followee_id": 2
}
```

#### GET `/api/profile/followers/<user_id>`
Get user's followers.

#### GET `/api/profile/following/<user_id>`
Get users that this user is following.

### Skill Comparison

#### POST `/api/profile/compare`
Compare skills between two users.

**Request Body:**
```json
{
    "user1_id": 1,
    "user2_id": 2
}
```

**Response:**
```json
{
    "success": true,
    "comparison": {
        "common_skills": [...],
        "user1_unique_skills": [...],
        "user2_unique_skills": [...],
        "recommendations": [...],
        "summary": {
            "total_common": 5,
            "user1_unique_count": 2,
            "user2_unique_count": 3,
            "overlap_percentage": 50.0
        }
    }
}
```

### Public API

#### GET `/api/profile/public/<handle>`
Get public profile by handle (external API).

**Response:**
```json
{
    "success": true,
    "profile": {
        "handle": "johndoe",
        "bio": "Learning enthusiast",
        "interests": ["Python", "Machine Learning"],
        "learning_style": "Visual",
        "metrics": {
            "hours_studied": 125.5,
            "xp_total": 2500,
            "streak_days": 7,
            "certifications": ["Python Basics", "Data Analysis"]
        },
        "skills": [
            {
                "skill_id": "python",
                "mastery_level": 4
            }
        ],
        "social": {
            "followers_count": 42,
            "following_count": 28
        }
    }
}
```

### Health Check

#### GET `/api/profile/health`
Health check endpoint.

## 🔒 Privacy Modes & Security

### Privacy Levels

1. **Public**: Visible to everyone via public API
2. **Private**: Only visible to authenticated user
3. **Followers Only**: Visible to users who follow you

### Privacy Controls

#### Field-level Privacy
- **Bio**: Control visibility of user bio
- **Interests**: Control visibility of interest tags
- **Learning Style**: Control visibility of learning style preference

#### Skill-level Privacy
- **Individual Skills**: Choose which skills are public vs private
- **Automatic Filtering**: Public API automatically filters private skills
- **Database Integrity**: Private skills remain in database but are filtered out

### Security Features

1. **No Private Data Leakage**: Public endpoints never return private data
2. **Follow Validation**: Prevent duplicate follows and self-follows
3. **Cascade Deletion**: User deletion removes all related data
4. **Input Validation**: All inputs are validated and sanitized

## 🧪 Testing

### Unit Tests
Comprehensive test suite covering:

- **Privacy Enforcement**: Ensure private data never leaks to public API
- **Follow Lifecycle**: Test follow/unfollow operations and prevent duplicates
- **Skill Comparison**: Verify comparison logic and recommendations
- **Metrics Aggregation**: Test metrics calculation from review logs
- **Database Integrity**: Verify cascade deletion and data consistency

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest backend/tests/ -v --cov=backend/

# Run specific test categories
pytest backend/tests/test_profile_service.py::TestProfileService::test_private_skills_never_leak -v
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Flask application
python main.py
```

### Desktop App Setup
```bash
cd desktop
npm install
npm run dev
```

### Mobile App Setup
```bash
cd mobile
npm install
npm start
```

## 📱 Usage Examples

### Creating a Profile
```javascript
// Create new user profile
const response = await fetch('/api/profile/upsert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        handle: 'learner123',
        bio: 'Passionate about learning new technologies',
        interests: ['Python', 'AI', 'Web Development'],
        learning_style: 'Hands-on',
        is_private: false
    })
});

const profile = await response.json();
```

### Adding Skills with Privacy
```javascript
// Add public and private skills
await fetch('/api/profile/skills/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 1,
        skills: [
            {
                skill_id: 'python',
                mastery_level: 4,
                visibility: true  // Public skill
            },
            {
                skill_id: 'company_secret',
                mastery_level: 5,
                visibility: false  // Private skill
            }
        ]
    })
});
```

### Following a User
```javascript
// Follow another user
await fetch('/api/profile/follow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        follower_id: 1,
        followee_id: 2
    })
});
```

### Comparing Skills
```javascript
// Compare skills with another user
const comparison = await fetch('/api/profile/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user1_id: 1,
        user2_id: 2
    })
});

const result = await comparison.json();
console.log(`You have ${result.comparison.summary.overlap_percentage}% skill overlap!`);
```

### Accessing Public Profile
```javascript
// Get public profile data (for external integrations)
const publicProfile = await fetch('/api/profile/public/learner123');
const profile = await publicProfile.json();

// This will only include data marked as public
// Private skills, bio, and other fields are automatically filtered
```

## 🛠️ Development

### Project Structure
```
/home/engine/project
├── backend/
│   ├── database/
│   │   └── sqlite_manager.py      # Database layer
│   ├── core/
│   │   └── social/
│   │       └── profile_service.py  # Business logic
│   └── api/
│       └── profile.py             # REST API endpoints
├── desktop/
│   ├── src/
│   │   ├── main/                  # Electron main process
│   │   └── renderer/              # React renderer
│   └── package.json
├── mobile/
│   ├── src/
│   │   ├── navigation/            # React Navigation
│   │   └── screens/               # Mobile screens
│   └── package.json
├── tests/
│   └── backend/tests/             # Unit tests
└── main.py                        # Flask app entry point
```

### Key Classes

#### SQLiteManager
- Handles all database operations
- Manages connections and transactions
- Provides helper methods for common queries

#### ProfileService
- Business logic for profile operations
- Privacy enforcement
- Social features (follow/unfollow)
- Skill comparison algorithms

### Adding New Features

1. **Database Changes**: Update `sqlite_manager.py` with new tables/methods
2. **Business Logic**: Add methods to `profile_service.py`
3. **API Endpoints**: Add routes to `profile.py`
4. **Frontend Updates**: Update desktop/mobile components
5. **Tests**: Add comprehensive tests in `backend/tests/`

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add unit tests for new functionality
3. Update documentation for API changes
4. Ensure privacy controls are properly implemented
5. Test all endpoints with various privacy configurations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation above
- Review the unit tests for usage examples
- Examine the privacy enforcement tests for security implementation

---

**Note**: This implementation ensures that private skills, bio, and other sensitive information never leak to public endpoints. The privacy system is enforced at multiple levels for maximum security.