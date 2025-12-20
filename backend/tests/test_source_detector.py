import unittest
from app.core.source_detector import SourceDetector


class TestSourceDetector(unittest.TestCase):
    
    def test_youtube_detection(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        source_type, metadata = SourceDetector.detect(url)
        self.assertEqual(source_type, 'youtube')
        self.assertEqual(metadata['video_id'], 'dQw4w9WgXcQ')
    
    def test_web_url_detection(self):
        url = "https://www.example.com/article"
        source_type, metadata = SourceDetector.detect(url)
        self.assertEqual(source_type, 'web')
        self.assertEqual(metadata['url'], url)
    
    def test_pdf_file_detection(self):
        source_type, metadata = SourceDetector.detect("", file_path="document.pdf")
        self.assertEqual(source_type, 'pdf')
        self.assertEqual(metadata['extension'], 'pdf')
    
    def test_markdown_file_detection(self):
        source_type, metadata = SourceDetector.detect("", file_path="readme.md")
        self.assertEqual(source_type, 'markdown')
        self.assertEqual(metadata['extension'], 'md')
    
    def test_text_detection(self):
        text = "This is plain text content"
        source_type, metadata = SourceDetector.detect(text)
        self.assertEqual(source_type, 'text')
        self.assertEqual(metadata['content'], text)


if __name__ == '__main__':
    unittest.main()
