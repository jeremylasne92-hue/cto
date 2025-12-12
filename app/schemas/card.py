from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class State(int, Enum):
    New = 0
    Learning = 1
    Review = 2
    Relearning = 3

class Grade(int, Enum):
    Again = 1
    Hard = 2
    Good = 3
    Easy = 4

class CardCreate(BaseModel):
    front: str
    back: str

class CardResponse(BaseModel):
    id: int
    front: str
    back: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SRSStateResponse(BaseModel):
    card_id: int
    state: State
    stability: float
    difficulty: float
    elapsed_days: float
    scheduled_days: float
    due: Optional[datetime]
    last_review: Optional[datetime]
    reps: int
    lapses: int

    class Config:
        from_attributes = True

class ReviewLogCreate(BaseModel):
    card_id: int
    grade: Grade
    duration_ms: int = 0

class ReviewLogResponse(BaseModel):
    id: int
    card_id: int
    grade: int
    review_date: datetime
    
    class Config:
        from_attributes = True

class SchedulingInfo(BaseModel):
    grade: Grade
    interval: float
    stability: float
    difficulty: float

class NextReviewSchedule(BaseModel):
    card_id: int
    schedules: List[SchedulingInfo]
