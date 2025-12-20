
# Pedagogy Engine – Quiz & Mind Map Transformation

This repository contains a small transformation engine that can:

- Select an LLM backend based on hardware tier (local GGUF via `llama.cpp`, or cloud fallback)
- Generate quizzes (5+ questions, varied types)
- Generate hierarchical mind maps ready for D3.js rendering
- Generate multi-level summaries
- Provide Socratic tutor prompt templates
- Cache/reuse generated artifacts and reuse for near-duplicate content via similarity search

## Quickstart (no external dependencies)

The engine works out-of-the-box in **offline mode** using deterministic heuristics (useful for CI/dev). For better results, configure a cloud key or install local model dependencies.

```bash
python -m pedagogy_engine quiz path/to/chapter.txt
python -m pedagogy_engine mindmap https://example.com/article
python -m pedagogy_engine summary path/to/chapter.txt
python -m pedagogy_engine socratic
```

## Local models (Premium/Standard tiers)

Local inference is implemented via `llama-cpp-python` + GGUF weights.

- Premium: Mistral-7B-Instruct-v0.2 (Q4_K_M)
- Standard: Phi-2 (Q4_K_M)
- Minimum: Cloud fallback

You can override behavior using environment variables:

- `PEDAGOGY_ENGINE_TIER=premium|standard|minimum`
- `PEDAGOGY_ENGINE_MODE=local|cloud|hybrid`
- `PEDAGOGY_ENGINE_MODEL_PATH=/path/to/model.gguf`
- `PEDAGOGY_ENGINE_ALLOW_DOWNLOAD=0|1`

## Cloud fallback

Supported (no SDK required):

- OpenAI: `OPENAI_API_KEY` (+ optional `OPENAI_MODEL`, `OPENAI_BASE_URL`)
- Groq (OpenAI-compatible): `GROQ_API_KEY` (+ optional `GROQ_MODEL`, `GROQ_BASE_URL`)
- Anthropic: `ANTHROPIC_API_KEY` (+ optional `ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`)

## Library usage

```python
from pedagogy_engine import TransformationEngine

engine = TransformationEngine()
quiz = engine.generate_quiz(content_text, num_questions=7)
mindmap = engine.generate_mind_map(article_text)
summaries = engine.generate_summaries(content_text)
```
# FSRS-5 SRS Engine

🧠 **Spaced Repetition System using FSRS-5 Algorithm**

A complete implementation of the Free Spaced Repetition Scheduler (FSRS) version 5 algorithm, designed for optimal learning through scientifically-backed spaced repetition scheduling.

## 🚀 Features

### Core FSRS-5 Algorithm
- **Three-Parameter Model**: Difficulty (D 0-10), Stability (S, days), Retrievability (R 0-1)
- **Four-Grade System**: Again (1), Hard (2), Good (3), Easy (4)
- **Automatic Scheduling**: Calculates optimal review intervals for 90% target retention
- **Adaptive Learning**: Updates card parameters based on user performance

### Smart Session Management
- **Session Optimizer**: Warm-up → Main → Cool-down structure
- **Difficulty-Based Ordering**: Medium difficulty first, hard cards in middle, easy at end
- **Overdue Prioritization**: Old reviews handled first
- **Leech Detection**: Flags problematic cards (>2 lapses or high difficulty)

### Comprehensive Database
- **SQLite Backend**: Persistent storage with proper indexing
- **Complete Logging**: Every review tracked for analytics and sync
- **Deck Management**: Organize cards into logical groups
- **Statistics**: Detailed analytics and performance metrics

### Web Interface
- **Modern UI**: Clean, responsive web interface
- **Real-time Timer**: Track review duration for adaptive scheduling
- **Interactive Review**: Flashcard flip animation with grading buttons
- **Analytics Dashboard**: Visual statistics and leech card management

## 📋 System Requirements

- Python 3.8+
- FastAPI
- SQLite3
- Modern web browser

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd fsrs-srs-engine

# Install dependencies
pip install -r requirements.txt

# Run the server
python backend/api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Web Interface**: http://localhost:8000/web
- **API Docs**: http://localhost:8000/docs

## 📖 Usage

### 1. Create Decks
```python
# Create a deck for your topic
deck = srs_engine.create_deck("Spanish Vocabulary", "Spanish words and phrases")
```

### 2. Add Cards
```python
# Create flashcards
card1 = srs_engine.create_card(deck_id, "Hola", "Hello", "flashcard")
card2 = srs_engine.create_card(deck_id, "Gracias", "Thank you", "flashcard")
```

### 3. Start Review Session
```python
# Begin a review session
session = srs_engine.start_review_session(deck_id)
print(f"Session started with {session['due_cards_count']} cards")
```

### 4. Review Cards
```python
# Review cards with grading
# Grade 1 = Again (complete failure)
# Grade 2 = Hard (correct with difficulty)  
# Grade 3 = Good (correct recall)
# Grade 4 = Easy (too easy)

result = srs_engine.review_card(card_id, grade=3, review_duration=8.5)
print(f"Next review in {result['next_review']['interval_days']:.1f} days")
```

## 🎯 FSRS-5 Algorithm Details

### Parameter Updates

**Difficulty (D)**: 
- Updated based on review performance
- Range: 0.0 (very easy) to 10.0 (very hard)
- Formula: `D_new = D_old + (1-grade) * (4-grade) * f(D_old)`

**Stability (S)**:
- Measures how long memories persist
- Updated exponentially based on grade and difficulty
- Higher grades increase stability dramatically

**Retrievability (R)**:
- Probability of successful recall at given interval
- Calculated as: `R = exp((I - S) / (S * 4))`
- Target: 90% retention at review time

### Leech Detection
Cards are flagged as leeches when:
- Difficulty > 8.5, OR
- Lapses > 2 (forgotten more than twice)

Leech cards are excluded from automatic scheduling and require manual review.

### Session Optimization
```
1. Warm-up (20%): Medium difficulty cards → Build confidence
2. Main (60%): Hard cards → Peak attention period  
3. Cool-down (20%): Easy cards → End on positive note
```

## 📊 API Endpoints

### Deck Management
- `POST /api/decks` - Create new deck
- `GET /api/decks` - List all decks with statistics
- `GET /api/decks/{id}/stats` - Get deck statistics

### Card Management  
- `POST /api/cards` - Create new card
- `GET /api/cards` - List cards (optional deck filter)

### Review Sessions
- `POST /api/sessions/start` - Start review session
- `POST /api/sessions/end` - End current session
- `GET /api/sessions/due-cards` - Get due cards

### Card Review
- `POST /api/review` - Process card review with grade
- `POST /api/review/skip` - Skip card without grading

### Analytics
- `GET /api/analytics/reviews` - Review analytics (last N days)
- `GET /api/analytics/leech-cards` - List leech cards

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test classes
python -m pytest tests/test_fsrs_engine.py::TestFSRS5Algorithm -v
python -m pytest tests/test_fsrs_engine.py::TestSRSEngine -v
```

Test coverage includes:
- FSRS algorithm correctness
- Database operations
- Complete workflow integration
- Edge cases and error handling
- API compatibility

## 📈 Performance Targets

Based on the acceptance criteria, this implementation targets:

- **Retention J7 > 40%**: After 7-day retention should exceed 40%
- **Session Duration**: 20-30 minutes with 15+ cards
- **Scheduling Accuracy**: Matches Anki FSRS output
- **Leech Detection**: Flags problematic cards effectively
- **Database Performance**: Fast queries with proper indexing

## 🔄 Data Sync

The system is designed for multi-device sync:
- **Append-only Review Logs**: No conflicts during synchronization
- **Export/Import**: Complete deck data export for backup/sync
- **State Consistency**: All SRS state properly tracked

## 📝 Database Schema

```sql
-- Cards table
CREATE TABLE cards (
    id TEXT PRIMARY KEY,
    deck_id TEXT NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL, 
    card_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SRS State table
CREATE TABLE card_srs_state (
    card_id TEXT PRIMARY KEY,
    difficulty REAL NOT NULL DEFAULT 5.0,
    stability REAL NOT NULL DEFAULT 1.0,
    retrievability REAL NOT NULL DEFAULT 1.0,
    due_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviews_count INTEGER NOT NULL DEFAULT 0,
    lapses INTEGER NOT NULL DEFAULT 0,
    is_leech BOOLEAN NOT NULL DEFAULT 0
);

-- Review Logs table
CREATE TABLE review_logs (
    id TEXT PRIMARY KEY,
    card_id TEXT NOT NULL,
    grade INTEGER NOT NULL,
    review_duration REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT NOT NULL,
    -- Complete state tracking for sync
    old_difficulty REAL NOT NULL,
    new_difficulty REAL NOT NULL,
    old_stability REAL NOT NULL, 
    new_stability REAL NOT NULL,
    old_retrievability REAL NOT NULL,
    new_retrievability REAL NOT NULL,
    interval REAL NOT NULL
);
```

## 🏗️ Architecture

```
backend/
├── __init__.py           # Package initialization
├── database.py          # SQLite database operations
├── fsrs_algorithm.py    # FSRS-5 algorithm implementation  
├── srs_engine.py        # Core SRS engine coordination
└── api.py              # FastAPI web interface

tests/
└── test_fsrs_engine.py  # Comprehensive test suite

docs/
└── FSRS5_PAPER.md       # Algorithm reference
```

## 📚 References

- **FSRS Paper**: Ye et al. "FSRS: An Algorithm for Automated Scheduling of Flashcards"
- **Implementation Guide**: Based on FSRS-5 specification
- **Database Design**: Optimized for SQLite with proper indexing

## 🤝 Contributing

This is an educational implementation of FSRS-5. The core algorithm follows the published research while being optimized for practical use.

## 📄 License

This implementation is designed for educational and research purposes.

---

**Built with ❤️ for optimal learning through spaced repetition**

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

