#!/usr/bin/env python3
"""
Standalone E2E Learning Cycle Test

This test can be run without pytest and demonstrates the complete learning workflow:
ingest → transform → review → update SRS
"""

import tempfile
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import the test class
from tests.integration.test_e2e_learning_cycle import TestE2ELearningCycle


class StandaloneE2ETest:
    """Standalone test runner for E2E learning cycle"""
    
    def __init__(self):
        self.test_instance = TestE2ELearningCycle()
        self.results = {}
    
    def run_all_tests(self):
        """Run all E2E learning cycle tests"""
        print("=" * 60)
        print("E2E Learning Cycle Integration Test")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Setup
            print("\n1. Setting up test environment...")
            test_database = self.test_instance.get_test_database()
            services = self.test_instance.get_learning_cycle_services(test_database)
            sample_content = self.test_instance.get_sample_biology_content()
            print("✓ Test environment setup complete")
            
            # Test 1: Ingest Content
            print("\n2. Testing content ingestion...")
            created_cards, deck_id = self.test_instance.test_ingest_content_and_create_chunks(
                services, sample_content
            )
            self.results['chunks_created'] = len(created_cards)
            print(f"✓ Created {len(created_cards)} content chunks")
            
            # Test 2: Generate Quizzes
            print("\n3. Testing quiz generation...")
            generated_quizzes = self.test_instance.test_generate_quizzes_from_chunks(
                services, created_cards
            )
            self.results['quizzes_generated'] = len(generated_quizzes)
            print(f"✓ Generated {len(generated_quizzes)} quizzes")
            
            # Test 3: Simulate User Reviews
            print("\n4. Testing 5-day review simulation...")
            review_log, review_deck_id = self.test_instance.test_simulate_user_reviews_5_day_cycle(
                services, created_cards
            )
            self.results['reviews_completed'] = len(review_log)
            print(f"✓ Completed {len(review_log)} reviews over 5 days")
            
            # Test 4: Verify SRS State Updates
            print("\n5. Testing SRS state updates...")
            final_cards = self.test_instance.test_verify_srs_state_updates(
                services, review_log, review_deck_id
            )
            self.results['srs_states_verified'] = len(final_cards)
            print(f"✓ Verified SRS states for {len(final_cards)} cards")
            
            # Test 5: Verify Retention Metrics
            print("\n6. Testing retention metrics...")
            retention_data = self.test_instance.test_verify_retention_metrics(
                services, final_cards
            )
            if retention_data:
                avg_retention = sum(r['estimated_retention'] for r in retention_data) / len(retention_data)
                self.results['avg_retention'] = avg_retention
                print(f"✓ Average retention: {avg_retention:.2%}")
            else:
                self.results['avg_retention'] = 0
                print("✓ Retention metrics calculated (no data)")
            
            # Test 6: Verify Knowledge Graph Updates
            print("\n7. Testing knowledge graph updates...")
            concepts, graph_data = self.test_instance.test_verify_knowledge_graph_updates(
                services, sample_content, review_deck_id
            )
            self.results['concepts_created'] = len(concepts)
            self.results['graph_nodes'] = len(graph_data.get('nodes', []))
            print(f"✓ Created {len(concepts)} concepts with {len(graph_data.get('nodes', []))} graph nodes")
            
            # Test 7: Verify Data Integrity
            print("\n8. Testing data integrity...")
            integrity_ok = self.test_instance.test_verify_data_integrity(
                services, review_log, review_deck_id
            )
            self.results['data_integrity'] = integrity_ok
            print(f"✓ Data integrity check: {'PASSED' if integrity_ok else 'FAILED'}")
            
            # Performance check
            end_time = time.time()
            execution_time = end_time - start_time
            self.results['execution_time'] = execution_time
            
            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print(f"Execution Time: {execution_time:.2f} seconds")
            print(f"Content Chunks Created: {self.results['chunks_created']}")
            print(f"Quizzes Generated: {self.results['quizzes_generated']}")
            print(f"Reviews Completed: {self.results['reviews_completed']}")
            print(f"SRS States Verified: {self.results['srs_states_verified']}")
            print(f"Average Retention: {self.results.get('avg_retention', 0):.2%}")
            print(f"Concepts Created: {self.results['concepts_created']}")
            print(f"Graph Nodes: {self.results['graph_nodes']}")
            print(f"Data Integrity: {'PASS' if self.results['data_integrity'] else 'FAIL'}")
            
            # Performance requirement check
            if execution_time < 300:  # 5 minutes
                print(f"✓ Performance requirement met (< 5 minutes)")
            else:
                print(f"✗ Performance requirement failed ({execution_time:.2f} seconds > 300)")
            
            # Retention requirement check
            avg_ret = self.results.get('avg_retention', 0)
            if avg_ret >= 0.40:  # 40%
                print(f"✓ Retention requirement met (>= 40%)")
            else:
                print(f"✗ Retention requirement failed ({avg_ret:.2%} < 40%)")
            
            # Overall result
            all_passed = (
                self.results['chunks_created'] >= 10 and
                self.results['quizzes_generated'] >= 20 and
                self.results['reviews_completed'] >= 100 and
                self.results['srs_states_verified'] > 0 and
                self.results.get('avg_retention', 0) >= 0.40 and
                self.results['concepts_created'] >= 5 and
                self.results['data_integrity']
            )
            
            print(f"\nOVERALL RESULT: {'PASS' if all_passed else 'FAIL'}")
            
            return all_passed
            
        except Exception as e:
            print(f"\n✗ Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Cleanup
            try:
                if 'test_database' in locals():
                    os.unlink(test_database['db_path'])
                    os.unlink(test_database['lancedb_path'])
            except:
                pass
    
    def save_results(self, filename="e2e_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nResults saved to {filename}")


def main():
    """Main entry point"""
    test_runner = StandaloneE2ETest()
    success = test_runner.run_all_tests()
    test_runner.save_results()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())