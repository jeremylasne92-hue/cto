import unittest
import sqlite3
import os
import shutil
import tempfile
import sys
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.database.sqlite_manager import SQLiteManager
from backend.core.graph.knowledge_graph_service import KnowledgeGraphService

class TestKnowledgeGraphService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        self.sqlite = SQLiteManager(self.db_path)
        self.sqlite.initialize_schema()
        
        self.lancedb = MagicMock()
        self.lancedb.embeddings_table = MagicMock()
        
        self.service = KnowledgeGraphService(self.sqlite, self.lancedb)

    def tearDown(self):
        self.sqlite.close()
        shutil.rmtree(self.test_dir)

    def test_create_concept(self):
        c = self.service.create_concept("Test Concept", "Description")
        self.assertIsNotNone(c)
        self.assertEqual(c['name'], "Test Concept")
        self.assertEqual(c['description'], "Description")
        
        # Check database
        saved = self.service.get_concept(c['id'])
        self.assertEqual(saved['name'], "Test Concept")
        
        # Check mastery initialization
        mastery = self.sqlite.fetch_one("SELECT * FROM concept_mastery WHERE concept_id = ?", (c['id'],))
        self.assertIsNotNone(mastery)
        self.assertEqual(mastery['mastery_level'], 0.0)

    def test_duplicate_concept(self):
        self.service.create_concept("Unique")
        with self.assertRaises(ValueError):
            self.service.create_concept("Unique")

    def test_create_relation(self):
        c1 = self.service.create_concept("C1")
        c2 = self.service.create_concept("C2")
        
        r = self.service.create_relation(c1['id'], c2['id'], "related", 0.8)
        self.assertIsNotNone(r)
        self.assertEqual(r['source'], c1['id'])
        self.assertEqual(r['target'], c2['id'])
        self.assertEqual(r['strength'], 0.8)

    def test_orphan_relation(self):
        c1 = self.service.create_concept("C1")
        with self.assertRaises(ValueError):
            self.service.create_relation(c1['id'], "non-existent", "related")

    def test_self_loop(self):
        c1 = self.service.create_concept("C1")
        with self.assertRaises(ValueError):
            self.service.create_relation(c1['id'], c1['id'], "related")

    def test_integrity_check(self):
        # Create orphans
        self.service.create_concept("Orphan")
        
        check = self.service.run_integrity_check()
        self.assertFalse(check['valid'])
        self.assertTrue(any("orphan" in i for i in check['issues']))
        
        # Create cycle
        c1 = self.service.create_concept("C1")
        c2 = self.service.create_concept("C2")
        self.service.create_relation(c1['id'], c2['id'], "rel")
        self.service.create_relation(c2['id'], c1['id'], "rel")
        
        check = self.service.run_integrity_check()
        self.assertFalse(check['valid'])
        self.assertTrue(any("cycle" in i for i in check['issues']))

    def test_graph_data(self):
        c1 = self.service.create_concept("C1")
        c2 = self.service.create_concept("C2")
        self.service.create_relation(c1['id'], c2['id'], "rel")
        
        data = self.service.get_graph_data()
        self.assertEqual(len(data['nodes']), 2)
        self.assertEqual(len(data['links']), 1)
        
        # Test search
        data = self.service.get_graph_data(search_term="C1")
        self.assertTrue(any(n['name'] == "C1" for n in data['nodes']))

if __name__ == '__main__':
    unittest.main()
