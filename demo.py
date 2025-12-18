"""
Demo script for FSRS-5 SRS Engine
Shows how to use the system programmatically
"""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from srs_engine import SRSEngine

def create_sample_deck(engine):
    """Create a sample Spanish vocabulary deck"""
    print("🇪🇸 Creating Spanish Vocabulary Deck...")
    
    # Create deck
    deck = engine.create_deck(
        "Spanish Vocabulary",
        "Basic Spanish words and phrases for travelers"
    )
    deck_id = deck['deck_id']
    
    # Sample Spanish cards
    spanish_cards = [
        {"front": "Hola", "back": "Hello", "type": "flashcard"},
        {"front": "Gracias", "back": "Thank you", "type": "flashcard"},
        {"front": "Por favor", "back": "Please", "type": "flashcard"},
        {"front": "Lo siento", "back": "Sorry", "type": "flashcard"},
        {"front": "Buenos días", "back": "Good morning", "type": "flashcard"},
        {"front": "Buenas noches", "back": "Good night", "type": "flashcard"},
        {"front": "¿Dónde está...?", "back": "Where is...?", "type": "flashcard"},
        {"front": "¿Cuánto cuesta?", "back": "How much does it cost?", "type": "flashcard"},
        {"front": "La cuenta, por favor", "back": "The bill, please", "type": "flashcard"},
        {"front": "¿Habla inglés?", "back": "Do you speak English?", "type": "flashcard"},
        {"front": "No entiendo", "back": "I don't understand", "type": "flashcard"},
        {"front": "¿Puede ayudarme?", "back": "Can you help me?", "type": "flashcard"},
    ]
    
    # Create cards
    created_cards = []
    for card_data in spanish_cards:
        card = engine.create_card(
            deck_id, 
            card_data["front"], 
            card_data["back"], 
            card_data["type"]
        )
        created_cards.append(card)
        print(f"  ✅ Created: {card_data['front']} → {card_data['back']}")
    
    print(f"\n📚 Deck created with {len(created_cards)} cards")
    return deck_id, created_cards

def simulate_reviews(engine, cards, deck_id):
    """Simulate some initial reviews to show how the system works"""
    print("\n🎯 Starting Review Session...")
    
    # Start session
    session = engine.start_review_session(deck_id)
    print(f"📊 Session started with {session['due_cards_count']} cards due")
    print(f"⏱️  Estimated duration: {session['estimated_duration']//60} minutes")
    
    # Show session optimizer breakdown
    optimizer = session['session_optimizer']
    print(f"🏃 Warm-up (medium): {optimizer['warmup_medium']} cards")
    print(f"💪 Main (hard): {optimizer['main_hard']} cards")  
    print(f"😌 Cool-down (easy): {optimizer['cooldown_easy']} cards")
    
    # Simulate reviewing some cards with realistic grades
    review_scenarios = [
        {"card_idx": 0, "grade": 3, "duration": 6.5, "note": "Good recall"},
        {"card_idx": 1, "grade": 4, "duration": 4.2, "note": "Too easy"},
        {"card_idx": 2, "grade": 2, "duration": 12.8, "note": "Had to think hard"},
        {"card_idx": 3, "grade": 3, "duration": 7.1, "note": "Good recall"},
        {"card_idx": 4, "grade": 1, "duration": 15.2, "note": "Complete failure"},
    ]
    
    print("\n📝 Processing Reviews:")
    for scenario in review_scenarios:
        if scenario["card_idx"] < len(cards):
            card = cards[scenario["card_idx"]]
            result = engine.review_card(
                card["card_id"], 
                scenario["grade"], 
                scenario["duration"]
            )
            
            # Convert days to human readable
            interval_days = result['next_review']['interval_days']
            if interval_days < 1:
                interval_str = f"{int(interval_days * 24)} hours"
            else:
                interval_str = f"{interval_days:.1f} days"
            
            grade_names = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
            print(f"  📚 {card['front']} → Grade: {scenario['grade']} ({grade_names[scenario['grade']]})")
            print(f"     💭 {scenario['note']} | ⏱️ {scenario['duration']}s")
            print(f"     📈 Difficulty: {result['old_state']['difficulty']:.1f} → {result['new_state']['difficulty']:.1f}")
            print(f"     ⏰ Next review: {interval_str}")
            if result['is_leech']:
                print(f"     🐌 LEECH CARD DETECTED!")
            print()
    
    # End session
    session_info = engine.end_review_session()
    print(f"✅ Session ended after {session_info['duration_seconds']:.1f} seconds")
    
    return session

def show_analytics(engine, deck_id):
    """Show analytics and statistics"""
    print("\n📊 Analytics & Statistics")
    print("=" * 40)
    
    # Deck statistics
    stats = engine.get_deck_statistics(deck_id)
    print(f"📚 Total Cards: {stats['total_cards']}")
    print(f"⏰ Due Cards: {stats['due_cards']}")
    print(f"✅ Reviewed Today: {stats['reviewed_today']}")
    print(f"🐌 Leech Cards: {stats['leech_cards']}")
    print(f"📈 Avg Difficulty: {stats['avg_difficulty']:.1f}")
    print(f"⏱️ Avg Stability: {stats['avg_stability']:.1f} days")
    print(f"🧠 Avg Retrievability: {stats['avg_retrievability']:.1%}")
    
    # Review analytics
    analytics = engine.get_review_analytics(7)  # Last 7 days
    print(f"\n📅 Reviews (Last 7 Days): {analytics['total_reviews']}")
    
    if analytics['daily_reviews']:
        for day in analytics['daily_reviews'][-3:]:  # Show last 3 days
            avg_grade = day['avg_grade'] or 0
            print(f"  📆 {day['review_date']}: {day['reviews']} reviews, avg grade {avg_grade:.1f}")
    
    # Leech cards
    leech_cards = engine.get_leech_cards()
    if leech_cards:
        print(f"\n🐌 Leech Cards ({len(leech_cards)} total):")
        for card in leech_cards[:3]:  # Show first 3
            print(f"  🔴 {card['front']} (Difficulty: {card['difficulty']:.1f}, Lapses: {card['lapses']})")
    else:
        print("\n🎉 No leech cards detected!")

def demonstrate_fsrs_algorithm():
    """Demonstrate the FSRS algorithm directly"""
    print("\n🧠 FSRS-5 Algorithm Demonstration")
    print("=" * 40)
    
    from fsrs_algorithm import FSRS5Algorithm, FSRSState
    
    fsrs = FSRS5Algorithm()
    
    # Start with a new card
    state = fsrs.initialize_new_card()
    print(f"🆕 New Card State:")
    print(f"   Difficulty: {state.difficulty}")
    print(f"   Stability: {state.stability} days")
    print(f"   Retrievability: {state.retrievability:.1%}")
    
    # Simulate several reviews
    print(f"\n📚 Review Simulation:")
    current_state = state
    
    reviews = [
        {"grade": 3, "note": "Good recall"},
        {"grade": 4, "note": "Too easy"},
        {"grade": 2, "note": "Hard but correct"},
        {"grade": 3, "note": "Good recall"},
        {"grade": 1, "note": "Complete failure"},
    ]
    
    for i, review in enumerate(reviews, 1):
        result = fsrs.review_card(current_state, review['grade'], 8.0, i-1)
        
        interval_days = result.next_interval
        if interval_days < 1:
            interval_str = f"{int(interval_days * 24)} hours"
        else:
            interval_str = f"{interval_days:.1f} days"
        
        grade_names = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
        print(f"  Review {i}: {review['grade']} ({grade_names[review['grade']]}) - {review['note']}")
        print(f"    Difficulty: {current_state.difficulty:.1f} → {result.new_difficulty:.1f}")
        print(f"    Stability: {current_state.stability:.1f} → {result.new_stability:.1f} days")
        print(f"    Next interval: {interval_str}")
        
        # Update state for next iteration
        current_state = FSRSState(
            difficulty=result.new_difficulty,
            stability=result.new_stability, 
            retrievability=result.new_retrievability
        )
    
    # Final state
    print(f"\n📊 Final Card State:")
    print(f"   Difficulty: {current_state.difficulty:.1f} / 10.0")
    print(f"   Stability: {current_state.stability:.1f} days")
    print(f"   Retrievability: {current_state.retrievability:.1%}")

def main():
    """Run the complete demo"""
    print("🧠 FSRS-5 SRS Engine Demo")
    print("=" * 50)
    print("This demo shows how the FSRS-5 algorithm works")
    print("for spaced repetition learning.\n")
    
    # Initialize engine with temporary database
    engine = SRSEngine("demo_srs_engine.db")
    
    try:
        # 1. Create sample data
        deck_id, cards = create_sample_deck(engine)
        
        # 2. Simulate reviews
        simulate_reviews(engine, cards, deck_id)
        
        # 3. Show analytics
        show_analytics(engine, deck_id)
        
        # 4. Demonstrate algorithm directly
        demonstrate_fsrs_algorithm()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"💡 You can now:")
        print(f"   • Run the web interface: python backend/api.py")
        print(f"   • Access the API at: http://localhost:8000")
        print(f"   • Open the web UI at: http://localhost:8000/web")
        print(f"   • Run tests: python -m pytest tests/ -v")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up demo database
        if os.path.exists("demo_srs_engine.db"):
            os.remove("demo_srs_engine.db")
            print(f"\n🧹 Cleaned up demo database")

if __name__ == "__main__":
    main()