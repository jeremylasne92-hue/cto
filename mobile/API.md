# API Documentation - SRS Mobile App

This document describes the expected API endpoints that the mobile app will communicate with for syncing data.

## Base URL

Configure in `src/services/api.ts`:
```typescript
private baseURL: string = 'https://api.yourdomain.com/api';
```

## Authentication

All API requests require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Decks

#### GET /decks
Get all decks for the authenticated user.

**Response:**
```json
[
  {
    "id": "deck1",
    "name": "Spanish Vocabulary",
    "description": "Common Spanish words and phrases",
    "totalCards": 150,
    "dueCards": 25,
    "reviewedToday": 10,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-15T12:00:00Z"
  }
]
```

### Cards

#### GET /cards/due
Get all cards due for review.

**Response:**
```json
[
  {
    "id": "card1",
    "deckId": "deck1",
    "front": "Hello",
    "back": "Hola",
    "conceptId": "concept1",
    "lastReviewed": "2024-01-10T10:00:00Z",
    "nextReview": "2024-01-15T10:00:00Z",
    "interval": 5,
    "easeFactor": 2.5,
    "repetitions": 3,
    "lapses": 1
  }
]
```

#### GET /cards?deckId={deckId}
Get all cards for a specific deck.

**Query Parameters:**
- `deckId` (required): The deck ID

**Response:** Same format as `/cards/due`

### Reviews

#### POST /reviews
Submit review grades.

**Request:**
```json
{
  "reviews": [
    {
      "cardId": "card1",
      "grade": 3,
      "timestamp": "2024-01-15T14:30:00Z",
      "duration": 5000
    },
    {
      "cardId": "card2",
      "grade": 4,
      "timestamp": "2024-01-15T14:35:00Z",
      "duration": 3000
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "synced": 2
}
```

### Concepts

#### GET /concepts
Get all concepts in the knowledge graph.

**Response:**
```json
[
  {
    "id": "concept1",
    "name": "Greetings",
    "mastery": 85.5,
    "cardCount": 12,
    "relatedConcepts": ["concept2", "concept3"],
    "position": {
      "x": 100,
      "y": 150
    }
  }
]
```

### Stats

#### GET /stats
Get user statistics.

**Response:**
```json
{
  "totalCardsReviewed": 1250,
  "currentStreak": 15,
  "longestStreak": 42,
  "streakFreezeCount": 3,
  "xp": 2450,
  "level": 25,
  "retentionRate": 87.5,
  "reviewHistory": [
    {
      "date": "2024-01-15",
      "reviewed": 45,
      "correct": 38
    }
  ]
}
```

### Health Check

#### GET /health
Check API availability.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

### Common Error Codes

- `UNAUTHORIZED` (401): Invalid or expired token
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `VALIDATION_ERROR` (400): Invalid request data
- `SERVER_ERROR` (500): Internal server error
- `RATE_LIMIT_EXCEEDED` (429): Too many requests

## Rate Limiting

- Standard endpoints: 100 requests per minute
- Review submission: 1000 requests per hour
- Sync endpoints: 60 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1610000000
```

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response Headers:**
```
X-Total-Count: 250
X-Page-Count: 5
```

## Sync Strategy

### Mobile → Server (Push)

1. Mobile collects unsynced reviews
2. Mobile POSTs to `/reviews`
3. Server processes and stores reviews
4. Server updates card states
5. Mobile marks reviews as synced

### Server → Mobile (Pull)

1. Mobile GETs from `/decks`
2. Mobile GETs from `/cards/due`
3. Mobile GETs from `/concepts`
4. Mobile GETs from `/stats`
5. Mobile updates local SQLite database

### Conflict Resolution

**Strategy:** Last Write Wins (LWW)

- Server review log is source of truth
- Mobile updates are always accepted
- If conflict detected, server state takes precedence
- Mobile recalculates based on server data

## WebSocket Support (Future)

Real-time sync using WebSocket connection:

```
wss://api.yourdomain.com/sync
```

**Message Format:**
```json
{
  "type": "REVIEW_UPDATE",
  "data": {
    "cardId": "card1",
    "grade": 3
  }
}
```

## Security

### HTTPS Only
All API calls must use HTTPS in production.

### Token Expiry
JWT tokens expire after 7 days. Implement token refresh:

#### POST /auth/refresh
**Request:**
```json
{
  "refreshToken": "refresh_token_here"
}
```

**Response:**
```json
{
  "token": "new_jwt_token",
  "refreshToken": "new_refresh_token"
}
```

### CORS
The API should allow CORS from the mobile app domain.

## Testing

### Mock Server

For development, use the mock API responses in Jest tests:

```typescript
jest.mock('../services/api', () => ({
  syncDecks: jest.fn(() => Promise.resolve(mockDecks)),
  syncCards: jest.fn(() => Promise.resolve(mockCards)),
  submitReviews: jest.fn(() => Promise.resolve({ success: true })),
}));
```

### Postman Collection

A Postman collection with all endpoints is available at:
`/docs/postman/SRS-API.postman_collection.json`

## Versioning

API version is included in the base URL:
```
https://api.yourdomain.com/v1/api
```

Breaking changes will increment the version number.

## Support

For API issues:
- Check API status: https://status.yourdomain.com
- Report issues: api-support@yourdomain.com
- API documentation: https://docs.yourdomain.com/api
