from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from app.db.base import Base

class State(enum.Enum):
    New = 0
    Learning = 1
    Review = 2
    Relearning = 3

class Rating(enum.Enum):
    Again = 1
    Hard = 2
    Good = 3
    Easy = 4

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    front = Column(String, nullable=False)
    back = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    srs_state = relationship("CardSRSState", back_populates="card", uselist=False, cascade="all, delete-orphan")
    review_logs = relationship("ReviewLog", back_populates="card", cascade="all, delete-orphan")

class CardSRSState(Base):
    __tablename__ = "card_srs_state"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), unique=True, nullable=False)
    
    state = Column(Integer, default=State.New.value) # Storing as integer for FSRS compatibility
    stability = Column(Float, default=0.0)
    difficulty = Column(Float, default=0.0)
    elapsed_days = Column(Float, default=0.0)
    scheduled_days = Column(Float, default=0.0)
    reps = Column(Integer, default=0)
    lapses = Column(Integer, default=0)
    
    due = Column(DateTime(timezone=True), nullable=True)
    last_review = Column(DateTime(timezone=True), nullable=True)

    card = relationship("Card", back_populates="srs_state")

class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    
    grade = Column(Integer, nullable=False) # 1-4
    
    state = Column(Integer, nullable=False) # State before review
    stability = Column(Float, nullable=False) # Stability before review
    difficulty = Column(Float, nullable=False) # Difficulty before review
    
    elapsed_days = Column(Float, nullable=False)
    scheduled_days = Column(Float, nullable=False)
    
    review_date = Column(DateTime(timezone=True), server_default=func.now())
    duration_ms = Column(Integer, default=0)

    card = relationship("Card", back_populates="review_logs")
