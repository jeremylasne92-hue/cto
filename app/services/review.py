from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import math
from app.models.models import Card, CardSRSState, ReviewLog, State
from app.schemas.card import Grade, SchedulingInfo, NextReviewSchedule
from app.services.fsrs_algorithm import FSRSCalculator, FSRSParameters

class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.fsrs = FSRSCalculator()

    def _get_or_create_state(self, card_id: int) -> CardSRSState:
        state = self.db.query(CardSRSState).filter(CardSRSState.card_id == card_id).first()
        if not state:
            state = CardSRSState(
                card_id=card_id,
                state=State.New.value,
                stability=0.0,
                difficulty=0.0,
                elapsed_days=0.0,
                scheduled_days=0.0,
                reps=0,
                lapses=0
            )
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
        return state

    def schedule(self, card_id: int) -> NextReviewSchedule:
        state = self._get_or_create_state(card_id)
        
        now = datetime.now(timezone.utc)
        if state.last_review:
            last_review = state.last_review
            if last_review.tzinfo is None:
                last_review = last_review.replace(tzinfo=timezone.utc)
            elapsed_days = (now - last_review).total_seconds() / 86400
        else:
            elapsed_days = 0

        schedules = []
        for grade in [Grade.Again, Grade.Hard, Grade.Good, Grade.Easy]:
            if state.state == State.New.value:
                new_d = self.fsrs.init_difficulty(grade.value)
                new_s = self.fsrs.init_stability(grade.value)
            else:
                retrievability = self.fsrs.forgetting_curve(elapsed_days, state.stability)
                new_d = self.fsrs.next_difficulty(state.difficulty, grade.value)
                new_s = self.fsrs.next_stability(state.stability, state.difficulty, retrievability, grade.value)
            
            new_interval = self.fsrs.next_interval(new_s)
            
            schedules.append(SchedulingInfo(
                grade=grade,
                interval=new_interval,
                stability=new_s,
                difficulty=new_d
            ))
            
        return NextReviewSchedule(card_id=card_id, schedules=schedules)

    def record_review(self, card_id: int, grade: int, elapsed_ms: int = 0) -> CardSRSState:
        state = self._get_or_create_state(card_id)
        now = datetime.now(timezone.utc)
        
        # Snapshot for log
        log = ReviewLog(
            card_id=card_id,
            grade=grade,
            state=state.state,
            stability=state.stability,
            difficulty=state.difficulty,
            elapsed_days=state.elapsed_days, # This is elapsed days OF THE PREVIOUS interval, but wait.
            # actually logs usually store the interval/elapsed that led to THIS review.
            scheduled_days=state.scheduled_days,
            review_date=now,
            duration_ms=elapsed_ms
        )

        if state.last_review:
            last_review = state.last_review
            if last_review.tzinfo is None:
                last_review = last_review.replace(tzinfo=timezone.utc)
            current_elapsed_days = (now - last_review).total_seconds() / 86400
        else:
            current_elapsed_days = 0
            
        # Update Log elapsed days to be accurate for THIS review
        log.elapsed_days = current_elapsed_days

        if state.state == State.New.value:
            new_d = self.fsrs.init_difficulty(grade)
            new_s = self.fsrs.init_stability(grade)
            
            state.state = State.Learning.value if grade == 1 else State.Review.value # Simplification
            # Actually FSRS maps New -> Review directly usually, unless we have learning steps.
            # "Grades 1-4". 1=Again. 
            # If grade is Again on New, it stays "New" or goes to "Learning"?
            # Let's say it enters Review/Learning cycle.
            # FSRS v5 is often "scheduler only", assumes no learning steps or handles them outside.
            # I will assume standard FSRS behavior: 
            # 1 (Again) -> first interval is small.
            state.state = State.Review.value # For FSRS pure usage
            
        else:
            retrievability = self.fsrs.forgetting_curve(current_elapsed_days, state.stability)
            new_d = self.fsrs.next_difficulty(state.difficulty, grade)
            new_s = self.fsrs.next_stability(state.stability, state.difficulty, retrievability, grade)
            
            if grade == 1:
                state.lapses += 1
                state.state = State.Relearning.value 
            else:
                state.state = State.Review.value

        state.stability = new_s
        state.difficulty = new_d
        state.elapsed_days = current_elapsed_days # Last interval actual duration
        
        new_interval = self.fsrs.next_interval(new_s)
        state.scheduled_days = new_interval
        
        # Calculate due date
        # If interval < 1 day, it might be minutes. 
        # But next_interval returns days.
        state.due = now + timedelta(days=new_interval)
        state.last_review = now
        state.reps += 1
        
        self.db.add(log)
        self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        
        return state

    def get_queue(self, limit: int = 10):
        now = datetime.now(timezone.utc)
        # Fetch cards due before now, ordered by due date
        # Also include New cards?
        # Typically mixed. Let's prioritize due reviews.
        
        due_cards = self.db.query(Card).join(CardSRSState).filter(
            CardSRSState.due <= now
        ).order_by(CardSRSState.due).limit(limit).all()
        
        if len(due_cards) < limit:
            # Fetch new cards
            # New cards might not have SRSState or have state=New
            new_limit = limit - len(due_cards)
            new_cards = self.db.query(Card).outerjoin(CardSRSState).filter(
                (CardSRSState.id == None) | (CardSRSState.state == State.New.value)
            ).limit(new_limit).all()
            return due_cards + new_cards
            
        return due_cards
