"""
Unit tests for Knowledge Graph Service
Tests core operations including concept creation, relation queries, and integrity failures
"""
import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock

from backend.core.graph.knowledge_graph_service import KnowledgeGraphService
from backend.database.sqlite_manager import SQLiteManager


class TestKnowledgeGraphService(unittest.TestCase):
    """Test cases for Knowledge Graph Service"""
    
    def setUp(self):
        """Set up test database"""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Initialize service with test database
        self.service = KnowledgeGraphService(self.db_path)
        
        # Clean up any existing data
        self._clean_database()
    
    def tearDown(self):
        """Clean up test database"""
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass
    
    def _clean_database(self):
        """Clean database for fresh test state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM relations')
            cursor.execute('DELETE FROM concepts')
            cursor.execute('DELETE FROM concept_mastery')
            cursor.execute('DELETE FROM concept_embeddings')
            conn.commit()
    
    def test_create_concept_success(self):
        """Test successful concept creation"""
        concept = self.service.create_concept(
            name="Test Concept",
            description="A test concept",
            content="Test content"
        )
        
        self.assertIsNotNone(concept)
        self.assertEqual(concept['name'], "Test Concept")
        self.assertEqual(concept['description'], "A test concept")
        self.assertEqual(concept['content'], "Test content")
        self.assertIn('id', concept)
        self.assertIn('created_at', concept)
    
    def test_create_concept_duplicate_name(self):
        """Test that duplicate concept names are rejected"""
        # Create first concept
        self.service.create_concept(name="Duplicate Test", description="First")
        
        # Try to create second with same name
        with self.assertRaises(ValueError) as context:
            self.service.create_concept(name="Duplicate Test", description="Second")
        
        self.assertIn("already exists", str(context.exception))
    
    def test_create_concept_with_parent(self):
        """Test concept creation with parent concept"""
        # Create parent concept
        parent = self.service.create_concept(name="Parent Concept", description="Parent")
        
        # Create child concept
        child = self.service.create_concept(
            name="Child Concept",
            description="Child",
            parent_id=parent['id']
        )
        
        self.assertEqual(child['parent_id'], parent['id'])
    
    def test_create_concept_nonexistent_parent(self):
        """Test that creating concept with nonexistent parent raises error"""
        with self.assertRaises(ValueError) as context:
            self.service.create_concept(
                name="Orphan Concept",
                description="Should fail",
                parent_id=999
            )
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_update_concept_success(self):
        """Test successful concept update"""
        # Create concept
        concept = self.service.create_concept(name="Original", description="Original desc")
        
        # Update it
        updated = self.service.update_concept(
            concept['id'],
            name="Updated",
            description="Updated desc"
        )
        
        self.assertEqual(updated['name'], "Updated")
        self.assertEqual(updated['description'], "Updated desc")
    
    def test_update_concept_nonexistent(self):
        """Test updating nonexistent concept raises error"""
        with self.assertRaises(ValueError) as context:
            self.service.update_concept(999, name="Doesn't exist")
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_update_concept_duplicate_name(self):
        """Test that updating to duplicate name is rejected"""
        # Create two concepts
        concept1 = self.service.create_concept(name="First", description="First")
        concept2 = self.service.create_concept(name="Second", description="Second")
        
        # Try to rename second to first's name
        with self.assertRaises(ValueError) as context:
            self.service.update_concept(concept2['id'], name="First")
        
        self.assertIn("already exists", str(context.exception))
    
    def test_delete_concept_success(self):
        """Test successful concept deletion"""
        # Create concept
        concept = self.service.create_concept(name="To Delete", description="Delete me")
        concept_id = concept['id']
        
        # Delete it
        result = self.service.delete_concept(concept_id)
        self.assertTrue(result)
        
        # Verify it's gone
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM concepts WHERE id = ?', (concept_id,))
            self.assertIsNone(cursor.fetchone())
    
    def test_delete_concept_with_relations(self):
        """Test that concept deletion prevents orphans by default"""
        # Create two concepts and a relation
        concept1 = self.service.create_concept(name="Source", description="Source")
        concept2 = self.service.create_concept(name="Target", description="Target")
        self.service.create_relation(concept1['id'], concept2['id'])
        
        # Try to delete source (should fail without force)
        with self.assertRaises(ValueError) as context:
            self.service.delete_concept(concept1['id'])
        
        self.assertIn("orphaned relations", str(context.exception))
    
    def test_delete_concept_force(self):
        """Test forced concept deletion removes relations"""
        # Create two concepts and a relation
        concept1 = self.service.create_concept(name="Source", description="Source")
        concept2 = self.service.create_concept(name="Target", description="Target")
        self.service.create_relation(concept1['id'], concept2['id'])
        
        # Force delete source
        result = self.service.delete_concept(concept1['id'], force=True)
        self.assertTrue(result)
        
        # Verify source is gone
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM concepts WHERE id = ?', (concept1['id'],))
            self.assertIsNone(cursor.fetchone())
    
    def test_create_relation_success(self):
        """Test successful relation creation"""
        # Create concepts
        source = self.service.create_concept(name="Source", description="Source")
        target = self.service.create_concept(name="Target", description="Target")
        
        # Create relation
        relation = self.service.create_relation(
            source['id'],
            target['id'],
            relation_type="prerequisite",
            strength=2.5
        )
        
        self.assertIsNotNone(relation)
        self.assertEqual(relation['source_concept_id'], source['id'])
        self.assertEqual(relation['target_concept_id'], target['id'])
        self.assertEqual(relation['relation_type'], "prerequisite")
        self.assertEqual(relation['strength'], 2.5)
    
    def test_create_relation_self_reference(self):
        """Test that self-referencing relations are rejected"""
        concept = self.service.create_concept(name="Self Ref", description="Self")
        
        with self.assertRaises(ValueError) as context:
            self.service.create_relation(concept['id'], concept['id'])
        
        self.assertIn("self-referencing", str(context.exception))
    
    def test_create_relation_nonexistent_concepts(self):
        """Test that relations with nonexistent concepts are rejected"""
        with self.assertRaises(ValueError) as context:
            self.service.create_relation(999, 888)
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_create_duplicate_relation(self):
        """Test that duplicate relations are rejected"""
        # Create concepts
        source = self.service.create_concept(name="Source", description="Source")
        target = self.service.create_concept(name="Target", description="Target")
        
        # Create first relation
        self.service.create_relation(source['id'], target['id'])
        
        # Try to create duplicate
        with self.assertRaises(ValueError) as context:
            self.service.create_relation(source['id'], target['id'])
        
        self.assertIn("already exists", str(context.exception))
    
    def test_get_concept_graph_data(self):
        """Test graph data retrieval"""
        # Create test data
        concept1 = self.service.create_concept(name="Math", description="Mathematics")
        concept2 = self.service.create_concept(name="Algebra", description="Algebra basics")
        concept3 = self.service.create_concept(name="Calculus", description="Advanced math")
        
        self.service.create_relation(concept1['id'], concept2['id'], strength=3.0)
        self.service.create_relation(concept2['id'], concept3['id'], strength=2.0)
        
        # Add mastery data
        self.service.db_manager.update_mastery("test_user", concept1['id'], 85.0)
        self.service.db_manager.update_mastery("test_user", concept2['id'], 60.0)
        
        # Get graph data
        graph_data = self.service.get_concept_graph_data(user_id="test_user")
        
        # Verify structure
        self.assertIn('nodes', graph_data)
        self.assertIn('links', graph_data)
        self.assertIn('stats', graph_data)
        
        # Verify nodes
        self.assertEqual(len(graph_data['nodes']), 3)
        
        # Check mastery colors
        nodes_by_id = {node['id']: node for node in graph_data['nodes']}
        self.assertEqual(nodes_by_id[concept1['id']]['color'], 'green')  # 85%
        self.assertEqual(nodes_by_id[concept2['id']]['color'], 'yellow')  # 60%
        self.assertEqual(nodes_by_id[concept3['id']]['color'], 'gray')   # 0%
        
        # Verify links
        self.assertEqual(len(graph_data['links']), 2)
        
        # Verify stats
        self.assertEqual(graph_data['stats']['total_concepts'], 3)
        self.assertEqual(graph_data['stats']['total_relations'], 2)
    
    def test_search_concepts(self):
        """Test concept search functionality"""
        # Create test concepts
        self.service.create_concept(name="Python Programming", description="Learn Python")
        self.service.create_concept(name="JavaScript Basics", description="JS fundamentals")
        self.service.create_concept(name="Data Science", description="Data analysis")
        
        # Search for "Python"
        results = self.service.search_concepts("Python", limit=10)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Python Programming")
        self.assertEqual(results[0]['match_type'], 'text')
    
    def test_mastery_color_buckets(self):
        """Test mastery color categorization"""
        # Test color buckets
        self.assertEqual(self.service.get_mastery_color(90), 'green')
        self.assertEqual(self.service.get_mastery_color(75), 'yellow')
        self.assertEqual(self.service.get_mastery_color(35), 'orange')
        self.assertEqual(self.service.get_mastery_color(10), 'gray')
        
        # Test boundary conditions
        self.assertEqual(self.service.get_mastery_color(80), 'green')   # >= 80
        self.assertEqual(self.service.get_mastery_color(50), 'yellow')  # >= 50
        self.assertEqual(self.service.get_mastery_color(20), 'orange')  # >= 20
        self.assertEqual(self.service.get_mastery_color(0), 'gray')     # < 20
    
    def test_aggregate_mastery_from_reviews(self):
        """Test mastery aggregation from review scores"""
        # Create concept
        concept = self.service.create_concept(name="Test Subject", description="Test")
        
        # Test aggregation
        review_scores = [0.6, 0.7, 0.8, 0.9]  # 60%, 70%, 80%, 90%
        result = self.service.aggregate_mastery_from_reviews(
            "test_user", 
            concept['id'], 
            review_scores
        )
        
        self.assertIn('mastery_percentage', result)
        self.assertIn('review_count', result)
        self.assertEqual(result['review_count'], 4)
        
        # Verify mastery was updated in database
        mastery = self.service.db_manager.get_mastery("test_user", concept['id'])
        self.assertIsNotNone(mastery)
        self.assertEqual(mastery['review_count'], 4)
    
    def test_check_integrity_no_issues(self):
        """Test integrity check with clean graph"""
        # Create clean graph
        concept1 = self.service.create_concept(name="A", description="A")
        concept2 = self.service.create_concept(name="B", description="B")
        self.service.create_relation(concept1['id'], concept2['id'])
        
        # Check integrity
        result = self.service.check_integrity()
        
        self.assertEqual(result['status'], 'healthy')
        self.assertEqual(result['total_issues'], 0)
    
    def test_check_integrity_with_orphans(self):
        """Test integrity check detects orphaned relations"""
        # Create concepts and relation
        concept1 = self.service.create_concept(name="Source", description="Source")
        concept2 = self.service.create_concept(name="Target", description="Target")
        self.service.create_relation(concept1['id'], concept2['id'])
        
        # Manually break referential integrity
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM concepts WHERE id = ?', (concept2['id'],))
            conn.commit()
        
        # Check integrity
        result = self.service.check_integrity()
        
        self.assertEqual(result['status'], 'issues_found')
        self.assertGreater(result['total_issues'], 0)
        self.assertGreater(len(result['issues']['orphans']), 0)
    
    def test_check_integrity_with_cycles(self):
        """Test integrity check detects circular dependencies"""
        # Create concepts
        concept1 = self.service.create_concept(name="A", description="A")
        concept2 = self.service.create_concept(name="B", description="B")
        concept3 = self.service.create_concept(name="C", description="C")
        
        # Create circular dependency: A -> B -> C -> A
        self.service.create_relation(concept1['id'], concept2['id'])
        self.service.create_relation(concept2['id'], concept3['id'])
        self.service.create_relation(concept3['id'], concept1['id'])
        
        # Check integrity
        result = self.service.check_integrity()
        
        self.assertEqual(result['status'], 'issues_found')
        self.assertGreater(result['total_issues'], 0)
        self.assertGreater(len(result['issues']['cycles']), 0)
    
    def test_check_integrity_with_duplicates(self):
        """Test integrity check detects duplicate concept names"""
        # Insert duplicate manually to bypass validation
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO concepts (name, description) VALUES (?, ?)', 
                         ("Duplicate", "First"))
            cursor.execute('INSERT INTO concepts (name, description) VALUES (?, ?)', 
                         ("Duplicate", "Second"))
            conn.commit()
        
        # Check integrity
        result = self.service.check_integrity()
        
        self.assertEqual(result['status'], 'issues_found')
        self.assertGreater(result['total_issues'], 0)
        self.assertGreater(len(result['issues']['duplicate_ids']), 0)
    
    def test_check_integrity_with_strength_anomalies(self):
        """Test integrity check detects anomalous relation strengths"""
        # Create concepts
        concept1 = self.service.create_concept(name="A", description="A")
        concept2 = self.service.create_concept(name="B", description="B")
        
        # Insert relation with invalid strength
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO relations (source_concept_id, target_concept_id, strength)
                VALUES (?, ?, ?)
            ''', (concept1['id'], concept2['id'], -1.5))  # Invalid negative strength
            conn.commit()
        
        # Check integrity
        result = self.service.check_integrity()
        
        self.assertEqual(result['status'], 'issues_found')
        self.assertGreater(result['total_issues'], 0)
        self.assertGreater(len(result['issues']['strength_anomalies']), 0)
    
    def test_find_semantic_neighbors(self):
        """Test semantic neighbor discovery"""
        # Create test concepts
        concept1 = self.service.create_concept(
            name="Machine Learning", 
            description="AI and ML concepts"
        )
        concept2 = self.service.create_concept(
            name="Neural Networks", 
            description="Deep learning architectures"
        )
        concept3 = self.service.create_concept(
            name="Cooking", 
            description="Food preparation techniques"
        )
        
        # Find neighbors (simplified implementation uses name similarity)
        neighbors = self.service.find_semantic_neighbors(concept1['id'], limit=10)
        
        self.assertIsInstance(neighbors, list)
        # Should find neural networks as similar to machine learning
        neighbor_names = [n['name'] for n in neighbors]
        self.assertIn("Neural Networks", neighbor_names)
    
    def test_database_migration(self):
        """Test that database migrations run correctly"""
        # Verify tables exist
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check core tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='concepts'")
            self.assertIsNotNone(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relations'")
            self.assertIsNotNone(cursor.fetchone())
            
            # Check migration-added tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='concept_mastery'")
            self.assertIsNotNone(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='concept_layout_cache'")
            self.assertIsNotNone(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='concept_embeddings'")
            self.assertIsNotNone(cursor.fetchone())
    
    @patch('backend.core.graph.knowledge_graph_service.KnowledgeGraphService._generate_simple_embedding')
    def test_embedding_generation(self, mock_generate_embedding):
        """Test that embeddings are generated for new concepts"""
        mock_generate_embedding.return_value = [0.1] * 50  # Mock embedding
        
        concept = self.service.create_concept(name="Test", description="Test desc")
        
        # Verify embedding was stored
        embedding = self.service.vector_manager.get_embedding(concept['id'])
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 50)
        
        # Verify embedding generation was called
        mock_generate_embedding.assert_called_once_with("Test", "Test desc")


if __name__ == '__main__':
    unittest.main()