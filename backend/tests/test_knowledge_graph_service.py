import unittest
import tempfile
import os
from backend.database.sqlite_manager import SQLiteManager
from backend.core.graph.knowledge_graph_service import KnowledgeGraphService


class TestKnowledgeGraphService(unittest.TestCase):
    """Test suite for knowledge graph service."""
    
    def setUp(self):
        """Set up test database and service."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_manager = SQLiteManager(self.temp_db.name)
        self.kg_service = KnowledgeGraphService(self.db_manager)
        
        # Create test user
        self.user_id = self.db_manager.create_user('test_user', 'test@example.com')
    
    def tearDown(self):
        """Clean up test database."""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_create_concept(self):
        """Test concept creation."""
        concept = self.kg_service.create_concept(
            name="Python",
            description="Programming language",
            metadata={"category": "language"}
        )
        
        self.assertIsNotNone(concept)
        self.assertEqual(concept['name'], "Python")
        self.assertEqual(concept['description'], "Programming language")
    
    def test_duplicate_concept_name_rejected(self):
        """Test that duplicate concept names are rejected."""
        self.kg_service.create_concept("Python", "First concept")
        
        with self.assertRaises(ValueError) as context:
            self.kg_service.create_concept("Python", "Duplicate concept")
        
        self.assertIn("already exists", str(context.exception))
    
    def test_create_relation(self):
        """Test relation creation."""
        concept1 = self.kg_service.create_concept("Variables", "Basic concept")
        concept2 = self.kg_service.create_concept("Functions", "Advanced concept")
        
        relation = self.kg_service.create_relation(
            source_id=concept1['id'],
            target_id=concept2['id'],
            relation_type="prerequisite",
            strength=0.8
        )
        
        self.assertIsNotNone(relation)
        self.assertEqual(relation['source_id'], concept1['id'])
        self.assertEqual(relation['target_id'], concept2['id'])
        self.assertEqual(relation['relation_type'], "prerequisite")
    
    def test_prevent_orphan_relations(self):
        """Test that relations to non-existent concepts are rejected."""
        concept = self.kg_service.create_concept("Test", "Test concept")
        
        with self.assertRaises(ValueError) as context:
            self.kg_service.create_relation(
                source_id=concept['id'],
                target_id="non-existent-id",
                relation_type="related"
            )
        
        self.assertIn("not found", str(context.exception))
    
    def test_prevent_self_loops(self):
        """Test that self-loop relations are rejected."""
        concept = self.kg_service.create_concept("Test", "Test concept")
        
        with self.assertRaises(ValueError) as context:
            self.kg_service.create_relation(
                source_id=concept['id'],
                target_id=concept['id'],
                relation_type="related"
            )
        
        self.assertIn("itself", str(context.exception))
    
    def test_delete_concept_cascades(self):
        """Test that deleting a concept removes its relations."""
        concept1 = self.kg_service.create_concept("Concept1", "First")
        concept2 = self.kg_service.create_concept("Concept2", "Second")
        
        self.kg_service.create_relation(
            source_id=concept1['id'],
            target_id=concept2['id'],
            relation_type="related"
        )
        
        # Delete concept1
        self.kg_service.delete_concept(concept1['id'])
        
        # Check that relations are gone
        relations = self.db_manager.get_relations(concept_id=concept1['id'])
        self.assertEqual(len(relations), 0)
    
    def test_get_graph_data(self):
        """Test graph data retrieval."""
        concept1 = self.kg_service.create_concept("Node1", "First node")
        concept2 = self.kg_service.create_concept("Node2", "Second node")
        
        self.kg_service.create_relation(
            source_id=concept1['id'],
            target_id=concept2['id'],
            relation_type="prerequisite"
        )
        
        graph_data = self.kg_service.get_graph_data()
        
        self.assertEqual(len(graph_data['nodes']), 2)
        self.assertEqual(len(graph_data['edges']), 1)
        self.assertIn('metadata', graph_data)
    
    def test_mastery_colors(self):
        """Test mastery color assignment."""
        concept = self.kg_service.create_concept("Test", "Test concept")
        
        # Add review logs
        for i in range(10):
            self.db_manager.add_review_log(
                user_id=self.user_id,
                concept_id=concept['id'],
                correct=(i % 10 < 9),
                review_type='quiz'
            )
        
        # Aggregate mastery
        mastery = self.kg_service.aggregate_mastery_from_reviews(
            self.user_id, concept['id']
        )
        
        self.assertIn(concept['id'], mastery)
        self.assertGreater(mastery[concept['id']]['mastery_percent'], 80)
        
        # Get graph data with mastery
        graph_data = self.kg_service.get_graph_data(user_id=self.user_id)
        
        node = next(n for n in graph_data['nodes'] if n['id'] == concept['id'])
        self.assertEqual(node['color'], '#10b981')  # green for >80%
    
    def test_integrity_check_orphans(self):
        """Test integrity check with foreign key constraints enabled."""
        concept = self.kg_service.create_concept("Test", "Test")
        
        # With foreign key constraints enabled, orphan relations cannot be created
        # This test verifies that attempting to create an orphan relation fails
        success = self.db_manager.create_relation(
            relation_id="orphan-relation",
            source_id=concept['id'],
            target_id="non-existent",
            relation_type="related"
        )
        
        # Should fail due to foreign key constraint
        self.assertFalse(success)
        
        # Verify integrity check still works and shows no issues
        report = self.kg_service.run_integrity_check()
        self.assertFalse(report['has_issues'])
    
    def test_integrity_check_cycles(self):
        """Test integrity check detects cycles."""
        c1 = self.kg_service.create_concept("C1", "First")
        c2 = self.kg_service.create_concept("C2", "Second")
        c3 = self.kg_service.create_concept("C3", "Third")
        
        # Create a cycle: C1 -> C2 -> C3 -> C1
        self.kg_service.create_relation(c1['id'], c2['id'], "prerequisite")
        self.kg_service.create_relation(c2['id'], c3['id'], "prerequisite")
        self.kg_service.create_relation(c3['id'], c1['id'], "prerequisite")
        
        report = self.kg_service.run_integrity_check()
        
        self.assertTrue(report['has_issues'])
        self.assertGreater(len(report['issues']['cycles']), 0)
    
    def test_search_filter(self):
        """Test graph data search filtering."""
        self.kg_service.create_concept("Python", "Language")
        self.kg_service.create_concept("JavaScript", "Language")
        self.kg_service.create_concept("Database", "Storage")
        
        graph_data = self.kg_service.get_graph_data(search_term="python")
        
        self.assertEqual(len(graph_data['nodes']), 1)
        self.assertEqual(graph_data['nodes'][0]['name'], "Python")
    
    def test_depth_filter(self):
        """Test graph data depth filtering."""
        c1 = self.kg_service.create_concept("Root", "Root node")
        c2 = self.kg_service.create_concept("Child", "Child node")
        c3 = self.kg_service.create_concept("Grandchild", "Grandchild node")
        
        self.kg_service.create_relation(c1['id'], c2['id'], "prerequisite")
        self.kg_service.create_relation(c2['id'], c3['id'], "prerequisite")
        
        graph_data = self.kg_service.get_graph_data(depth=1)
        
        # With depth 1, we should get root and direct children
        self.assertLessEqual(len(graph_data['nodes']), 2)
    
    def test_layout_persistence(self):
        """Test saving and loading layout positions."""
        concept = self.kg_service.create_concept("Test", "Test")
        
        positions = {
            concept['id']: {'x': 100.5, 'y': 200.7, 'z': 0}
        }
        
        success = self.kg_service.save_layout_positions(positions)
        self.assertTrue(success)
        
        # Retrieve and verify
        loaded_positions = self.db_manager.get_layout_positions()
        self.assertIn(concept['id'], loaded_positions)
        self.assertAlmostEqual(loaded_positions[concept['id']]['x'], 100.5)
        self.assertAlmostEqual(loaded_positions[concept['id']]['y'], 200.7)


if __name__ == '__main__':
    unittest.main()
