# SRS Engine - FSRS-5 Algorithm Implementation

A comprehensive Spaced Repetition System (SRS) implementation using the FSRS-5 algorithm for optimal learning scheduling.

## Features

- FSRS-5 algorithm with model parameters (Difficulty, Stability, Retrievability)
- Database schema for cards, SRS state, and review logs
- Scheduling system with session optimization
- Review interface with grading buttons (1-4)
- Deck management and statistics
- Retention mechanics with category-based decay rates
- Leech detection for problematic cards
- SQLite persistence with sync-ready logging

## Project Structure

```
srs_engine/
├── models/           # Database models
├── algorithms/       # FSRS-5 algorithm implementation
├── scheduling/       # Session and scheduling logic
├── api/             # Review and deck management endpoints
├── database.py      # Database initialization
├── config.py        # Configuration
└── main.py          # Application entry point
```

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```

## API Endpoints

- `POST /api/decks` - Create a deck
- `GET /api/decks` - List decks
- `POST /api/cards` - Create a card
- `GET /api/cards/due` - Get due cards for today's session
- `POST /api/review` - Submit a review
- `GET /api/stats` - Get deck statistics

## Algorithm Details

The FSRS-5 algorithm uses the following model parameters:
- **Difficulty (D)**: 0-10 scale, how hard a card is
- **Stability (S)**: Days, how well the content is retained
- **Retrievability (R)**: 0-1 scale, probability of correct recall

Grade scale:
- 1 = Again (incorrect)
- 2 = Hard (correct, difficult)
- 3 = Good (correct, medium difficulty)
- 4 = Easy (correct, easy)
