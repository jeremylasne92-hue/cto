import unittest
from app.core.chunker import SemanticChunker


class TestSemanticChunker(unittest.TestCase):
    
    def setUp(self):
        self.chunker = SemanticChunker(chunk_size=10, overlap=2)
    
    def test_basic_chunking(self):
        text = "This is a test sentence with more than ten words in it to test chunking"
        chunks = self.chunker.chunk_text(text)
        
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0]['chunk_type'], 'text')
        self.assertEqual(chunks[0]['position'], 0)
        self.assertEqual(chunks[0]['chunk_order'], 0)
    
    def test_chunk_overlap(self):
        text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12 word13"
        chunks = self.chunker.chunk_text(text)
        
        self.assertGreater(len(chunks), 1)
    
    def test_markdown_chunking(self):
        markdown = """# Heading 1
Content under heading 1

## Heading 2
Content under heading 2
"""
        chunks = self.chunker.chunk_with_structure(markdown, 'markdown')
        
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(chunk['chunk_type'], 'markdown_section')
    
    def test_chunk_id_generation(self):
        text = "Test content"
        chunks = self.chunker.chunk_text(text)
        
        self.assertIsNotNone(chunks[0]['chunk_id'])
        self.assertIsInstance(chunks[0]['chunk_id'], str)


if __name__ == '__main__':
    unittest.main()
