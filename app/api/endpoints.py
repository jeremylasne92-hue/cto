from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.models.models import Card
from app.schemas.card import CardCreate, CardResponse, ReviewLogCreate, ReviewLogResponse, NextReviewSchedule, SRSStateResponse
from app.services.review import ReviewService

router = APIRouter()

@router.post("/cards", response_model=CardResponse)
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    db_card = Card(front=card.front, back=card.back)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@router.get("/reviews/queue", response_model=List[CardResponse])
def get_review_queue(limit: int = 10, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.get_queue(limit)

@router.get("/reviews/{card_id}/schedule", response_model=NextReviewSchedule)
def get_schedule(card_id: int, db: Session = Depends(get_db)):
    service = ReviewService(db)
    # Ensure card exists
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return service.schedule(card_id)

@router.post("/reviews/{card_id}", response_model=SRSStateResponse)
def record_review(card_id: int, review: ReviewLogCreate, db: Session = Depends(get_db)):
    if card_id != review.card_id:
         raise HTTPException(status_code=400, detail="Card ID mismatch")
    
    service = ReviewService(db)
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    updated_state = service.record_review(card_id, review.grade, review.duration_ms)
    return updated_state
