# Flashcard Sync Engine - Multi-Device Support

Basic synchronization between desktop and mobile companion via REST API.

## Architecture

- **Desktop**: SQLite + Python backend
- **Mobile**: React Native + SQLite cache  
- **Server**: REST API (Phase 2: WebSocket)
- **Protocol**: REST API (Phase 2: upgrade to CRDT + WebSocket)

## Sync Flow

### Desktop → Mobile
- Cards sync
- Quiz/mind maps
- Metadata (read-only on mobile)

### Mobile → Desktop  
- Review logs
- Grades
- Timestamps

## API Endpoints

- `GET /api/cards/due` - Fetch due cards for review
- `POST /api/reviews` - Submit review grades + timestamps
- `GET /api/decks` - List decks
- `GET /api/content` - Fetch ingested content metadata
- `POST /api/sync/pull` - Pull all changes since last sync
- `POST /api/sync/push` - Push local changes to server

## Database Schema

### Sync Table
```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY,
    object_type TEXT NOT NULL,
    object_id INTEGER NOT NULL,
    operation TEXT NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    synced BOOLEAN DEFAULT FALSE
);
```

## Sync Strategy

- **Conflict Resolution**: Last-Write-Wins (LWW)
- **Review Logs**: Append-only (no conflicts)
- **Timestamps**: Server time for tie-breaking

## Data Flow

1. Desktop adds card → Reviews review log
2. Mobile requests due cards → Receives serialized cards
3. Mobile submits grades → Logs stored locally + queued for sync
4. Desktop pulls reviews → Updates SRS state
5. Sync completes → Status indicator updates