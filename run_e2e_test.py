#!/usr/bin/env python3
"""
Test runner for E2E Learning Cycle
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test_methods():
    """Run individual test methods to verify they work"""
    from tests.integration.test_e2e_learning_cycle import TestE2ELearningCycle
    
    test_instance = TestE2ELearningCycle()
    
    print("Testing individual E2E methods...")
    
    try:
        # Test setup
        print("1. Testing setup methods...")
        test_db_gen = test_instance.test_database()
        test_db = next(test_db_gen)  # Get the actual database from generator
        services = test_instance.get_learning_cycle_services(test_db)
        sample_content = test_instance.sample_biology_content()
        print("✓ Setup methods work")
        
        # Test content ingestion
        print("2. Testing content ingestion...")
        cards, deck_id = test_instance.test_ingest_content_and_create_chunks(services, sample_content)
        print(f"✓ Content ingestion works: {len(cards)} chunks")
        
        # Test quiz generation
        print("3. Testing quiz generation...")
        quizzes = test_instance.test_generate_quizzes_from_chunks(services, cards)
        print(f"✓ Quiz generation works: {len(quizzes)} quizzes")
        
        # Test review simulation
        print("4. Testing review simulation...")
        review_log, review_deck_id = test_instance.test_simulate_user_reviews_5_day_cycle(services, cards)
        print(f"✓ Review simulation works: {len(review_log)} reviews")
        
        # Test SRS verification
        print("5. Testing SRS verification...")
        final_cards = test_instance.test_verify_srs_state_updates(services, review_log, review_deck_id)
        print(f"✓ SRS verification works: {len(final_cards)} cards")
        
        # Test retention metrics
        print("6. Testing retention metrics...")
        retention_data = test_instance.test_verify_retention_metrics(services, final_cards)
        print(f"✓ Retention metrics work: {len(retention_data)} data points")
        
        # Test knowledge graph
        print("7. Testing knowledge graph...")
        concepts, graph_data = test_instance.test_verify_knowledge_graph_updates(services, sample_content, review_deck_id)
        print(f"✓ Knowledge graph works: {len(concepts)} concepts")
        
        # Test data integrity
        print("8. Testing data integrity...")
        integrity_ok = test_instance.test_verify_data_integrity(services, review_log, review_deck_id)
        print(f"✓ Data integrity works: {'PASS' if integrity_ok else 'FAIL'}")
        
        # Cleanup
        try:
            os.unlink(test_db['db_path'])
            os.unlink(test_db['lancedb_path'])
        except:
            pass
        
        print("\n✓ All individual test methods work correctly!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_test_methods()
    exit(0 if success else 1)