# Social Learning Platform

A comprehensive social learning platform with user profiles, metrics tracking, skill management, and public API support for social interactions.

## Features

### User Profiles
- Customizable user profiles with bio, interests, and learning style
- Granular privacy controls for each profile field
- Public and private visibility modes

### Skills Management
- Track mastery levels for multiple skills
- Public/private visibility per skill
- Visual skill comparison between users
- Skill progress tracking with percentage indicators

### Learning Metrics
- Automatic calculation of study hours from review logs
- XP and streak tracking (integrates with gamification service when available)
- Certification tracking
- Real-time metrics dashboard

### Social Features
- Follow/unfollow other users
- View followers and following lists
- Compare skills with other users
- Public profile API for external access

## Architecture

### Backend
- **Flask REST API** - RESTful API endpoints for all profile operations
- **SQLite Database** - Lightweight database with optimized schema
- **Profile Service** - Business logic layer with privacy enforcement
- **IPC Bridge** - Electron integration for desktop app

### Frontend
- **Desktop (Electron + React)** - Full-featured desktop application
- **Mobile (React Native)** - Public profile viewer for mobile devices

## API Endpoints

### Authenticated Endpoints (require `X-User-Id` header)

#### POST /api/profile/upsert
Update user profile information.

```json
{
  "bio": "Software developer passionate about learning",
  "interests": "python,machine learning,web development",
  "learning_style": "visual"
}
```

#### POST /api/profile/privacy
Update privacy settings for profile fields.

```json
{
  "privacy_bio": 0,
  "privacy_interests": 1,
  "privacy_learning_style": 0
}
```

Privacy values:
- `0` - Public (visible to everyone)
- `1` - Private (hidden from public profile)
- `2` - Completely private (future use)

#### POST /api/profile/skills/update
Update user skills and mastery levels.

```json
{
  "skills": [
    {
      "skill_id": "python-basics",
      "skill_name": "Python Basics",
      "mastery": 0.85,
      "visibility": "public"
    },
    {
      "skill_id": "advanced-algorithms",
      "skill_name": "Advanced Algorithms",
      "mastery": 0.6,
      "visibility": "private"
    }
  ]
}
```

#### POST /api/profile/metrics
Refresh and aggregate user metrics from review logs and gamification service.

Returns:
```json
{
  "user_id": 1,
  "hours_studied": 42.5,
  "xp_total": 1250,
  "streak_days": 7,
  "certifications": ["Python Fundamentals", "Web Development"],
  "updated_at": "2025-12-15T10:30:00"
}
```

#### POST /api/profile/compare
Compare skills with another user.

```json
{
  "compare_with_id": 2
}
```

Returns:
```json
{
  "user1": { "id": 1, "handle": "alice" },
  "user2": { "id": 2, "handle": "bob" },
  "common_skills": [
    {
      "skill_id": "python",
      "skill_name": "Python",
      "user1_mastery": 0.85,
      "user2_mastery": 0.70,
      "difference": 0.15
    }
  ],
  "user1_unique_skills": [...],
  "user2_unique_skills": [...]
}
```

#### POST /api/profile/follow
Follow another user by their handle.

```json
{
  "handle": "learner123"
}
```

#### POST /api/profile/unfollow
Unfollow a user by their handle.

```json
{
  "handle": "learner123"
}
```

#### GET /api/profile/me
Get full profile for authenticated user (includes private data).

### Public Endpoints

#### GET /public/profile/:handle
Get public profile for any user by handle. Only returns non-private fields and public skills.

Example: `/public/profile/john_doe`

Returns:
```json
{
  "handle": "john_doe",
  "visibility_default": "public",
  "bio": "Learning enthusiast",
  "skills": [
    {
      "skill_id": "python",
      "skill_name": "Python",
      "mastery": 0.85
    }
  ],
  "metrics": {
    "hours_studied": 42.5,
    "xp_total": 1250,
    "streak_days": 7,
    "certifications": ["Python Fundamentals"]
  },
  "follower_count": 15
}
```

Note: Fields marked as private in privacy settings will not be included in the response.

## Privacy Modes

The platform supports granular privacy controls:

1. **Public** (default) - Field visible to everyone via public API
2. **Private** - Field hidden from public API, only visible to authenticated user
3. **Skills Visibility** - Per-skill public/private toggle

Privacy is enforced at the service layer to prevent leakage of private data.

## Database Schema

### users
- `id` - Primary key
- `handle` - Unique username
- `visibility_default` - Default visibility setting
- `created_at`, `updated_at` - Timestamps

### user_profiles
- `user_id` - Foreign key to users
- `bio`, `interests`, `learning_style` - Profile fields
- `privacy_bio`, `privacy_interests`, `privacy_learning_style` - Privacy flags
- `created_at`, `updated_at` - Timestamps

### user_metrics
- `user_id` - Foreign key to users
- `hours_studied` - Total study hours (derived from review_logs)
- `xp_total` - Total XP (from gamification service)
- `streak_days` - Current streak (from gamification service)
- `certifications_json` - JSON array of certifications
- `updated_at` - Last update timestamp

### user_skills
- `user_id` - Foreign key to users
- `skill_id` - Skill identifier
- `skill_name` - Display name
- `mastery` - Proficiency level (0.0 to 1.0)
- `visibility` - public/private
- `created_at`, `updated_at` - Timestamps

### user_follows
- `follower_id` - User who follows
- `followee_id` - User being followed
- `created_at` - Follow timestamp
- Constraint: Cannot follow yourself
- Unique constraint prevents duplicate follows

### review_logs
- `user_id` - Foreign key to users
- `duration_minutes` - Study session duration
- `created_at` - Session timestamp

## Running the Application

### Backend
```bash
cd /home/engine/project
python main.py
```

Server runs on `http://localhost:5000`

### Desktop App
```bash
cd desktop
npm install
npm start
```

### Mobile App
```bash
cd mobile
npm install
npm run android  # or npm run ios
```

## Testing

Run unit tests:
```bash
python -m unittest tests/test_profile_service.py
```

## Development

### Adding New Skills
Skills can be added through the desktop UI or API. Each skill requires:
- Unique `skill_id` (kebab-case recommended)
- Display `skill_name`
- `mastery` level between 0.0 and 1.0
- `visibility` setting (public/private)

### Integrating Gamification Service
The profile service accepts an optional `gamification_service` parameter. If provided, it should implement:
- `get_xp(user_id)` - Returns total XP for user
- `get_streak(user_id)` - Returns current streak days

### Deep Linking (Mobile)
The mobile app supports deep links for public profiles:
```
app://profile/john_doe
```

Configure in your app's manifest/info.plist accordingly.

## Security Considerations

1. **Privacy Enforcement** - All private data filtering happens at the service layer
2. **Public API** - `/public/profile` endpoint enforces privacy rules automatically
3. **Follow Prevention** - Users cannot follow themselves (database constraint)
4. **Duplicate Follow Prevention** - Unique constraint prevents duplicate follows
5. **Input Validation** - All API endpoints validate input data

## Future Enhancements

- Profile pictures and avatars
- Skill endorsements from followers
- Learning goals and milestones
- Activity feed for followed users
- Skill recommendations based on interests
- OAuth integration for social login
