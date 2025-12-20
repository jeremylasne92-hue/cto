from datetime import datetime, timezone, timedelta
from app.models.models import CardSRSState

def test_full_review_cycle(client, db_session):
    # 1. Create Card
    response = client.post("/api/v1/cards", json={"front": "F", "back": "B"})
    assert response.status_code == 200
    card_id = response.json()["id"]
    
    # 2. Check Queue - should contain the new card
    response = client.get("/api/v1/reviews/queue")
    assert response.status_code == 200
    queue = response.json()
    assert len(queue) == 1
    assert queue[0]["id"] == card_id

    # 3. Get Schedule Preview
    response = client.get(f"/api/v1/reviews/{card_id}/schedule")
    assert response.status_code == 200
    schedule = response.json()
    assert len(schedule["schedules"]) == 4
    # Good (3) should have interval ~3 days (approx 3.17)
    good_sched = next(s for s in schedule["schedules"] if s["grade"] == 3)
    assert 3.0 <= good_sched["interval"] <= 3.5

    # 4. Record Review (Good)
    # New -> Learning/Review
    response = client.post(f"/api/v1/reviews/{card_id}", json={"card_id": card_id, "grade": 3})
    assert response.status_code == 200
    state = response.json()
    assert state["state"] == 2 # Review (as per my simplified implementation where New -> Review)
    assert state["reps"] == 1
    
    # Check due date
    due_str = state["due"]
    if due_str.endswith("Z"):
        due_date = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
    else:
        # Check if it has timezone info
        d = datetime.fromisoformat(due_str)
        if d.tzinfo is None:
             due_date = d.replace(tzinfo=timezone.utc)
        else:
             due_date = d
             
    now = datetime.now(timezone.utc)
    # Expected interval is ~3.17 days
    assert (due_date - now).days >= 3

    # 5. Check Queue - should be empty now (since due date is in future)
    response = client.get("/api/v1/reviews/queue")
    assert response.status_code == 200
    queue = response.json()
    assert len(queue) == 0

def test_multiple_reviews_evolution(client, db_session):
    # Create card
    response = client.post("/api/v1/cards", json={"front": "F2", "back": "B2"})
    card_id = response.json()["id"]
    
    # Review 1: Good
    client.post(f"/api/v1/reviews/{card_id}", json={"card_id": card_id, "grade": 3})
    
    # Simulate time passing by modifying DB directly?
    # Or just use the `record_review` service but mock time?
    # I can't easily mock time inside the service unless I inject it or use freezegun.
    # But I can modify the card state in DB to simulate that time has passed.
    
    # Fetch state manually
    state_obj = db_session.query(CardSRSState).filter(CardSRSState.card_id == card_id).first()
    # Let's pretend 4 days passed (interval was ~3.17)
    # So we are slightly overdue.
    old_stability = state_obj.stability
    state_obj.last_review = state_obj.last_review - timedelta(days=4)
    state_obj.due = state_obj.last_review + timedelta(days=state_obj.scheduled_days)
    db_session.commit()
    
    # Verify it is in queue
    response = client.get("/api/v1/reviews/queue")
    assert len(response.json()) == 1
    
    # Review 2: Good
    response = client.post(f"/api/v1/reviews/{card_id}", json={"card_id": card_id, "grade": 3})
    new_state = response.json()
    
    # Stability should increase
    assert new_state["stability"] > old_stability
    # Interval should increase significantly
    assert new_state["scheduled_days"] > 3.5
