"""
FastAPI-based REST API for FSRS-5 SRS Engine
Provides web interface for the spaced repetition system
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from srs_engine import SRSEngine

# Pydantic models for API
class CreateDeckRequest(BaseModel):
    name: str = Field(..., description="Deck name")
    description: Optional[str] = Field("", description="Deck description")

class CreateCardRequest(BaseModel):
    deck_id: str = Field(..., description="Deck ID")
    front: str = Field(..., description="Card front side")
    back: str = Field(..., description="Card back side")
    card_type: str = Field("flashcard", description="Card type: quiz/flashcard/mindmap")

class ReviewCardRequest(BaseModel):
    card_id: str = Field(..., description="Card ID")
    grade: int = Field(..., description="Review grade: 1=Again, 2=Hard, 3=Good, 4=Easy")
    review_duration: Optional[float] = Field(0.0, description="Review duration in seconds")

class SkipCardRequest(BaseModel):
    card_id: str = Field(..., description="Card ID")
    reason: Optional[str] = Field("skipped", description="Reason for skipping")

# Initialize FastAPI app
app = FastAPI(
    title="FSRS-5 SRS Engine API",
    description="Spaced Repetition System using FSRS-5 algorithm",
    version="1.0.0"
)

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SRS Engine
srs_engine = SRSEngine()

# ====================
# API Routes
# ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FSRS-5 SRS Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "fsrs_version": "FSRS-5"
    }

# ====================
# Deck Management
# ====================

@app.post("/api/decks")
async def create_deck(request: CreateDeckRequest):
    """Create a new deck"""
    try:
        deck = srs_engine.create_deck(request.name, request.description)
        return {
            "success": True,
            "deck": deck
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/decks")
async def get_decks():
    """Get all decks with statistics"""
    try:
        decks = srs_engine.get_decks()
        return {
            "success": True,
            "decks": decks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/decks/{deck_id}/stats")
async def get_deck_stats(deck_id: str):
    """Get deck statistics"""
    try:
        stats = srs_engine.get_deck_statistics(deck_id)
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Deck not found: {str(e)}")

# ====================
# Card Management
# ====================

@app.post("/api/cards")
async def create_card(request: CreateCardRequest):
    """Create a new card"""
    try:
        card = srs_engine.create_card(
            request.deck_id, 
            request.front, 
            request.back, 
            request.card_type
        )
        return {
            "success": True,
            "card": card
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/cards")
async def get_cards(deck_id: Optional[str] = None):
    """Get cards from a deck"""
    try:
        cards = srs_engine.get_cards(deck_id)
        return {
            "success": True,
            "cards": cards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================
# Review Sessions
# ====================

@app.post("/api/sessions/start")
async def start_session(deck_id: Optional[str] = None):
    """Start a new review session"""
    try:
        session = srs_engine.start_review_session(deck_id)
        return {
            "success": True,
            "session": session
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/end")
async def end_session():
    """End the current review session"""
    try:
        session_info = srs_engine.end_review_session()
        return {
            "success": True,
            "session": session_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/due-cards")
async def get_due_cards(deck_id: Optional[str] = None):
    """Get cards due for review"""
    try:
        due_cards = srs_engine.get_due_cards(deck_id)
        return {
            "success": True,
            "due_cards": due_cards,
            "count": len(due_cards)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================
# Card Review
# ====================

@app.post("/api/review")
async def review_card(request: ReviewCardRequest):
    """Process a card review"""
    try:
        if not (1 <= request.grade <= 4):
            raise ValueError("Grade must be between 1 and 4")
        
        result = srs_engine.review_card(
            request.card_id, 
            request.grade, 
            request.review_duration or 0.0
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/review/skip")
async def skip_card_review(request: SkipCardRequest):
    """Skip a card review"""
    try:
        result = srs_engine.skip_card_review(request.card_id, request.reason)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ====================
# Analytics and Statistics
# ====================

@app.get("/api/analytics/reviews")
async def get_review_analytics(days: int = 30):
    """Get review analytics"""
    try:
        analytics = srs_engine.get_review_analytics(days)
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/leech-cards")
async def get_leech_cards():
    """Get leech cards that need attention"""
    try:
        leech_cards = srs_engine.get_leech_cards()
        return {
            "success": True,
            "leech_cards": leech_cards,
            "count": len(leech_cards)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================
# Import/Export
# ====================

@app.post("/api/decks/{deck_id}/export")
async def export_deck(deck_id: str):
    """Export deck data"""
    try:
        export_data = srs_engine.export_deck_data(deck_id)
        return {
            "success": True,
            "export": export_data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Deck not found: {str(e)}")

@app.post("/api/decks/import")
async def import_deck(deck_data: Dict[str, Any]):
    """Import deck data"""
    try:
        result = srs_engine.import_deck_data(deck_data)
        return {
            "success": True,
            "import": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ====================
# Web Interface Routes
# ====================

# Serve static files for web interface
@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Serve the web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FSRS-5 SRS Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .card { background: white; border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 8px; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .button:hover { background: #0056b3; }
            .button.grade-1 { background: #dc3545; }
            .button.grade-2 { background: #fd7e14; }
            .button.grade-3 { background: #28a745; }
            .button.grade-4 { background: #20c997; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
            .review-card { min-height: 300px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
            .card-front { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
            .card-back { font-size: 20px; color: #333; display: none; }
            .card-back.show { display: block; }
            .review-controls { margin-top: 20px; }
            .grading-buttons { display: flex; gap: 10px; justify-content: center; }
            .timer { text-align: center; font-size: 18px; color: #666; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 FSRS-5 SRS Engine</h1>
                <p>Spaced Repetition System using FSRS-5 Algorithm</p>
            </div>
            
            <!-- Deck Management -->
            <div id="deck-section">
                <h2>📚 Deck Management</h2>
                <div>
                    <input type="text" id="deck-name" placeholder="Deck name" style="padding: 10px; margin-right: 10px;">
                    <input type="text" id="deck-description" placeholder="Description" style="padding: 10px; margin-right: 10px;">
                    <button class="button" onclick="createDeck()">Create Deck</button>
                    <button class="button" onclick="loadDecks()">Refresh Decks</button>
                </div>
                <div id="decks-list" style="margin-top: 20px;"></div>
            </div>
            
            <!-- Card Creation -->
            <div id="card-section">
                <h2>📝 Create Cards</h2>
                <div>
                    <select id="card-deck" style="padding: 10px; margin-right: 10px;">
                        <option value="">Select Deck</option>
                    </select>
                    <input type="text" id="card-front" placeholder="Front side" style="padding: 10px; width: 200px; margin-right: 10px;">
                    <input type="text" id="card-back" placeholder="Back side" style="padding: 10px; width: 200px; margin-right: 10px;">
                    <select id="card-type" style="padding: 10px; margin-right: 10px;">
                        <option value="flashcard">Flashcard</option>
                        <option value="quiz">Quiz</option>
                        <option value="mindmap">Mind Map</option>
                    </select>
                    <button class="button" onclick="createCard()">Create Card</button>
                </div>
            </div>
            
            <!-- Review Section -->
            <div id="review-section">
                <h2>🎯 Start Review Session</h2>
                <div>
                    <select id="review-deck" style="padding: 10px; margin-right: 10px;">
                        <option value="">All Decks</option>
                    </select>
                    <button class="button" onclick="startSession()">Start Session</button>
                </div>
                <div id="review-stats" style="margin: 20px 0;"></div>
                <div id="current-card" style="margin: 20px 0;"></div>
                <div id="review-controls" style="display: none;">
                    <div class="timer">Time: <span id="timer">0.0</span>s</div>
                    <div class="grading-buttons">
                        <button class="button grade-1" onclick="gradeCard(1)">Again</button>
                        <button class="button grade-2" onclick="gradeCard(2)">Hard</button>
                        <button class="button grade-3" onclick="gradeCard(3)">Good</button>
                        <button class="button grade-4" onclick="gradeCard(4)">Easy</button>
                        <button class="button" onclick="skipCard()">Skip</button>
                    </div>
                </div>
            </div>
            
            <!-- Analytics -->
            <div id="analytics-section">
                <h2>📊 Analytics</h2>
                <button class="button" onclick="loadAnalytics()">Load Analytics</button>
                <button class="button" onclick="loadLeechCards()">Load Leech Cards</button>
                <div id="analytics-data"></div>
            </div>
        </div>
        
        <script>
            let currentSession = null;
            let currentCardIndex = 0;
            let sessionCards = [];
            let reviewStartTime = 0;
            let timerInterval = null;
            
            async function apiCall(endpoint, method = 'GET', data = null) {
                try {
                    const options = {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    };
                    if (data) options.body = JSON.stringify(data);
                    
                    const response = await fetch(endpoint, options);
                    const result = await response.json();
                    
                    if (!result.success) {
                        throw new Error(result.error || 'API call failed');
                    }
                    
                    return result;
                } catch (error) {
                    console.error('API Error:', error);
                    alert('Error: ' + error.message);
                    return null;
                }
            }
            
            async function loadDecks() {
                const result = await apiCall('/api/decks');
                if (result) {
                    const decksList = document.getElementById('decks-list');
                    const deckSelects = [document.getElementById('card-deck'), document.getElementById('review-deck')];
                    
                    // Update deck list display
                    let html = '<div class="stats">';
                    result.decks.forEach(deck => {
                        html += `
                            <div class="stat-card">
                                <h3>${deck.name}</h3>
                                <p>Cards: ${deck.total_cards}</p>
                                <p>Due: ${deck.due_cards}</p>
                                <p>Reviewed Today: ${deck.reviewed_today}</p>
                            </div>
                        `;
                    });
                    html += '</div>';
                    decksList.innerHTML = html;
                    
                    // Update select options
                    deckSelects.forEach(select => {
                        const currentValue = select.value;
                        select.innerHTML = '<option value="">Select Deck</option>';
                        result.decks.forEach(deck => {
                            if (!deck.is_default) {
                                const option = document.createElement('option');
                                option.value = deck.id;
                                option.textContent = deck.name;
                                select.appendChild(option);
                            }
                        });
                        select.value = currentValue;
                    });
                }
            }
            
            async function createDeck() {
                const name = document.getElementById('deck-name').value;
                const description = document.getElementById('deck-description').value;
                
                if (!name) {
                    alert('Please enter a deck name');
                    return;
                }
                
                const result = await apiCall('/api/decks', 'POST', { name, description });
                if (result) {
                    document.getElementById('deck-name').value = '';
                    document.getElementById('deck-description').value = '';
                    loadDecks();
                }
            }
            
            async function createCard() {
                const deckId = document.getElementById('card-deck').value;
                const front = document.getElementById('card-front').value;
                const back = document.getElementById('card-back').value;
                const cardType = document.getElementById('card-type').value;
                
                if (!deckId || !front || !back) {
                    alert('Please fill all card fields');
                    return;
                }
                
                const result = await apiCall('/api/cards', 'POST', {
                    deck_id: deckId, front, back, card_type: cardType
                });
                
                if (result) {
                    document.getElementById('card-front').value = '';
                    document.getElementById('card-back').value = '';
                    alert('Card created successfully!');
                }
            }
            
            async function startSession() {
                const deckId = document.getElementById('review-deck').value || null;
                const result = await apiCall('/api/sessions/start', 'POST', { deck_id: deckId });
                
                if (result) {
                    currentSession = result.session.session_id;
                    sessionCards = result.session.cards;
                    currentCardIndex = 0;
                    
                    document.getElementById('review-stats').innerHTML = `
                        <div class="stats">
                            <div class="stat-card">
                                <h3>Session Started</h3>
                                <p>Cards: ${sessionCards.length}</p>
                                <p>Estimated: ${Math.round(result.session.estimated_duration/60)}min</p>
                            </div>
                        </div>
                    `;
                    
                    showNextCard();
                }
            }
            
            function showNextCard() {
                if (currentCardIndex >= sessionCards.length) {
                    endSession();
                    return;
                }
                
                const card = sessionCards[currentCardIndex];
                const cardContainer = document.getElementById('current-card');
                const controls = document.getElementById('review-controls');
                
                cardContainer.innerHTML = `
                    <div class="card review-card">
                        <div class="card-front" id="card-text">${card.front}</div>
                        <div class="card-back" id="card-answer">${card.back}</div>
                    </div>
                `;
                
                controls.style.display = 'block';
                reviewStartTime = Date.now();
                startTimer();
                
                // Auto-show answer after 5 seconds
                setTimeout(() => showAnswer(), 5000);
            }
            
            function showAnswer() {
                document.getElementById('card-answer').classList.add('show');
            }
            
            function startTimer() {
                const timerEl = document.getElementById('timer');
                timerInterval = setInterval(() => {
                    const elapsed = (Date.now() - reviewStartTime) / 1000;
                    timerEl.textContent = elapsed.toFixed(1);
                }, 100);
            }
            
            function stopTimer() {
                if (timerInterval) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                }
                return (Date.now() - reviewStartTime) / 1000;
            }
            
            async function gradeCard(grade) {
                const card = sessionCards[currentCardIndex];
                const reviewDuration = stopTimer();
                
                const result = await apiCall('/api/review', 'POST', {
                    card_id: card.id,
                    grade: grade,
                    review_duration: reviewDuration
                });
                
                if (result) {
                    console.log('Review result:', result.result);
                    currentCardIndex++;
                    showNextCard();
                }
            }
            
            async function skipCard() {
                const card = sessionCards[currentCardIndex];
                const reviewDuration = stopTimer();
                
                const result = await apiCall('/api/review/skip', 'POST', {
                    card_id: card.id,
                    reason: 'manually skipped'
                });
                
                if (result) {
                    currentCardIndex++;
                    showNextCard();
                }
            }
            
            async function endSession() {
                const result = await apiCall('/api/sessions/end', 'POST');
                if (result) {
                    document.getElementById('current-card').innerHTML = '<div class="card"><h3>Session Complete! 🎉</h3></div>';
                    document.getElementById('review-controls').style.display = 'none';
                    currentSession = null;
                }
            }
            
            async function loadAnalytics() {
                const result = await apiCall('/api/analytics/reviews?days=7');
                if (result) {
                    const analyticsDiv = document.getElementById('analytics-data');
                    let html = '<div class="stats">';
                    
                    result.analytics.daily_reviews.forEach(day => {
                        html += `
                            <div class="stat-card">
                                <h4>${day.review_date}</h4>
                                <p>Reviews: ${day.reviews}</p>
                                <p>Avg Grade: ${(day.avg_grade || 0).toFixed(1)}</p>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    analyticsDiv.innerHTML = html;
                }
            }
            
            async function loadLeechCards() {
                const result = await apiCall('/api/analytics/leech-cards');
                if (result) {
                    const analyticsDiv = document.getElementById('analytics-data');
                    let html = '<h3>Leech Cards</h3>';
                    
                    if (result.leech_cards.length === 0) {
                        html += '<p>No leech cards found! 🎉</p>';
                    } else {
                        result.leech_cards.forEach(card => {
                            html += `
                                <div class="card">
                                    <h4>${card.front}</h4>
                                    <p>${card.back}</p>
                                    <p>Difficulty: ${card.difficulty.toFixed(1)} | Lapses: ${card.lapses}</p>
                                </div>
                            `;
                        });
                    }
                    
                    analyticsDiv.innerHTML = html;
                }
            }
            
            // Initialize page
            loadDecks();
        </script>
    </body>
    </html>
    """

# Main function for running the server
def main():
    """Run the FSRS-5 SRS Engine API server"""
    print("🧠 Starting FSRS-5 SRS Engine...")
    print("📡 API will be available at: http://localhost:8000")
    print("🌐 Web Interface: http://localhost:8000/web")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()