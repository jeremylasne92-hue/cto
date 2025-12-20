import unittest
import tempfile
import os
from app.core.hasher import ContentHasher


class TestContentHasher(unittest.TestCase):
    
    def test_text_hashing(self):
        text = "Hello, world!"
        hash1 = ContentHasher.hash_text(text)
        hash2 = ContentHasher.hash_text(text)
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)
    
    def test_url_hashing(self):
        url = "https://www.example.com"
        hash1 = ContentHasher.hash_url(url)
        hash2 = ContentHasher.hash_url(url)
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)
    
    def test_file_hashing(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            hash1 = ContentHasher.hash_file(temp_file)
            hash2 = ContentHasher.hash_file(temp_file)
            
            self.assertEqual(hash1, hash2)
            self.assertEqual(len(hash1), 64)
        finally:
            os.unlink(temp_file)
    
    def test_different_content_different_hash(self):
        hash1 = ContentHasher.hash_text("Content 1")
        hash2 = ContentHasher.hash_text("Content 2")
        
        self.assertNotEqual(hash1, hash2)


if __name__ == '__main__':
    unittest.main()
