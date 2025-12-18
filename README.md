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