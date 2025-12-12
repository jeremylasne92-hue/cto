# SRS Engine - Usage Guide

## Starting the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The application will start on `http://localhost:5000`

## API Usage Examples

### 1. Deck Management

#### Create a Deck
```bash
curl -X POST http://localhost:5000/api/decks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spanish Vocabulary",
    "description": "Learn Spanish words"
  }'
```

#### List All Decks
```bash
curl http://localhost:5000/api/decks
```

#### Get Deck Statistics
```bash
curl http://localhost:5000/api/decks/1/stats
```

#### Delete a Deck
```bash
curl -X DELETE http://localhost:5000/api/decks/1
```

### 2. Card Management

#### Create a Card
```bash
curl -X POST http://localhost:5000/api/cards \
  -H "Content-Type: application/json" \
  -d '{
    "front": "What is the Spanish word for dog?",
    "back": "perro",
    "deck_id": 1,
    "card_type": "flashcard",
    "category": "language"
  }'
```

#### Bulk Create Cards
```bash
curl -X POST http://localhost:5000/api/cards/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "deck_id": 1,
    "cards": [
      {"front": "Dog", "back": "perro"},
      {"front": "Cat", "back": "gato"},
      {"front": "House", "back": "casa"}
    ]
  }'
```

#### Get Card Details
```bash
curl http://localhost:5000/api/cards/1
```

#### Update a Card
```bash
curl -X PUT http://localhost:5000/api/cards/1 \
  -H "Content-Type: application/json" \
  -d '{
    "front": "Updated question",
    "back": "Updated answer"
  }'
```

#### Search Cards
```bash
curl "http://localhost:5000/api/cards/search?q=spanish"
```

#### Suspend a Card
```bash
curl -X POST http://localhost:5000/api/cards/1/suspend
```

#### Reset Card SRS State
```bash
curl -X POST http://localhost:5000/api/cards/1/reset
```

### 3. Review System

#### Get Due Cards for Review
```bash
curl "http://localhost:5000/api/reviews/due?deck_id=1&limit=20"
```

Response includes:
- Cards ready for review
- Session duration estimate
- Total due count

#### Submit a Review
```bash
curl -X POST http://localhost:5000/api/reviews/submit \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": 1,
    "grade": 3,
    "duration_seconds": 15,
    "session_id": "session-uuid"
  }'
```

**Grade Scale:**
- 1 = Again (incorrect)
- 2 = Hard (correct but difficult)
- 3 = Good (correct)
- 4 = Easy (correct and easy)

#### Skip a Card
```bash
curl -X POST http://localhost:5000/api/reviews/skip \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": 1,
    "session_id": "session-uuid"
  }'
```

#### Get Review History
```bash
curl "http://localhost:5000/api/reviews/1/history?limit=10"
```

### 4. Session Management

#### Create a Review Session
```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "deck_id": 1
  }'
```

Response includes session ID.

#### End a Session
```bash
curl -X POST http://localhost:5000/api/sessions/session-uuid \
  -H "Content-Type: application/json" \
  -d '{
    "total_duration": 1200
  }'
```

#### Get Session Statistics
```bash
curl http://localhost:5000/api/sessions/session-uuid/stats
```

## Typical Review Workflow

1. **Create a deck:**
   ```
   POST /api/decks
   ```

2. **Add cards to deck:**
   ```
   POST /api/cards (or POST /api/cards/bulk)
   ```

3. **Create a review session:**
   ```
   POST /api/sessions
   ```

4. **Get today's due cards:**
   ```
   GET /api/reviews/due?deck_id=1&limit=20
   ```

5. **For each card, submit review:**
   ```
   POST /api/reviews/submit
   ```

6. **End the session:**
   ```
   POST /api/sessions/{session_id}
   ```

7. **Check statistics:**
   ```
   GET /api/decks/{deck_id}/stats
   GET /api/sessions/{session_id}/stats
   ```

## FSRS-5 Algorithm Details

### Model Parameters

Each card has three parameters that are updated after each review:

- **Difficulty (D)**: 0-10 scale
  - Low: Easy card, might forget easily
  - High: Difficult card, but stable when learned

- **Stability (S)**: Measured in days
  - Determines the next review interval
  - Higher stability = longer interval before next review

- **Retrievability (R)**: 0-1 scale
  - Probability of correct recall
  - Decays exponentially over time
  - Reset to near-1 when reviewed

### Review Impact

- **Grade 1 (Again)**: 
  - Increases difficulty
  - Decreases stability significantly
  - Counts as a lapse

- **Grade 2 (Hard)**:
  - Increases difficulty slightly
  - Increases stability moderately
  - No lapse counted

- **Grade 3 (Good)**:
  - Keeps difficulty stable
  - Increases stability
  - Optimal performance

- **Grade 4 (Easy)**:
  - Decreases difficulty
  - Increases stability significantly
  - Best case scenario

### Next Review Interval Calculation

The interval is calculated using:
```
interval = stability * ln(target_retention) / ln(0.9)
```

Where target_retention is typically 0.9 (90% chance of recall).

### Leech Detection

Cards with more than 2 lapses are flagged as leeches and:
- Appear at the end of review sessions
- Highlighted for manual review
- May need simplification or deletion

## Session Scheduling

The system optimizes review order for learning:

1. **Warmup (Medium difficulty 4-6)**
   - Gets you in the zone
   - Medium difficulty cards

2. **Main (Hard difficulty 7-10)**
   - Challenge your knowledge
   - Harder cards in the middle

3. **Cooldown (Easy difficulty 0-5)**
   - End on a positive note
   - Easy cards to maintain confidence

4. **Leeches (cards with many lapses)**
   - At the end for manual review
   - Flagged for potential issues

## Database Schema

### Tables

- **decks**: Deck metadata
- **cards**: Card content and metadata
- **card_srs_state**: Current SRS state for each card
- **review_logs**: Append-only review history
- **session_states**: Review session tracking

### Key Relationships

```
Deck (1) ─── (Many) Card
Card (1) ─── (1) CardSRSState
Card (1) ─── (Many) ReviewLog
```

## Configuration

Edit `config.py` to adjust:

- `TARGET_RETENTION`: Default 0.9 (90%)
- `SESSION_TARGET_DURATION_MINUTES`: Target session length
- `SESSION_TARGET_CARD_COUNT`: Target cards per session
- `LEECH_THRESHOLD_LAPSES`: Lapses before flagging
- `CATEGORY_DECAY_RATES`: Retention decay by category

## Performance Considerations

- Reviews are logged synchronously (automatic save)
- SRS state updates are immediate
- Scheduling is optimized for typical session lengths (20-30 minutes, 15+ cards)
- Database uses SQLite (suitable for single-user, sync-ready design)

## Sync-Ready Design

The review log is append-only, making it suitable for sync:
- No update conflicts (only inserts)
- Preserves complete history
- Each review is timestamped
- Session grouping for batch operations
