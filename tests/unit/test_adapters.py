import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from src.models import SourceType, Document, SourceMetadata, JobStatus
from src.adapters.base import BaseAdapter
from src.adapters.youtube import YouTubeAdapter
from src.adapters.pdf import PDFAdapter
from src.adapters.web_page import WebPageAdapter
from src.adapters.markdown import MarkdownAdapter
from src.adapters.plain_text import PlainTextAdapter
from src.adapters import AdapterFactory


class TestBaseAdapter:
    """Test the BaseAdapter class"""
    
    def test_generate_hash(self):
        """Test SHA256 hash generation"""
        adapter = BaseAdapter()
        content = "test content"
        source = "test://source"
        
        hash1 = adapter._generate_hash(content, source)
        hash2 = adapter._generate_hash(content, source)
        hash3 = adapter._generate_hash("different content", source)
        
        assert len(hash1) == 64  # SHA256 is 64 hex characters
        assert hash1 == hash2  # Same content should produce same hash
        assert hash1 != hash3  # Different content should produce different hash
    
    def test_extract_metadata(self):
        """Test metadata extraction and standardization"""
        adapter = BaseAdapter()
        raw_metadata = {"title": "Test Title", "author": "Test Author"}
        
        metadata = adapter._extract_metadata(raw_metadata)
        
        assert metadata.title == "Test Title"
        assert metadata.author == "Test Author"


class TestYouTubeAdapter:
    """Test YouTube adapter"""
    
    def test_get_source_type(self):
        """Test YouTube source type detection"""
        adapter = YouTubeAdapter()
        assert adapter.get_source_type() == SourceType.YOUTUBE
    
    def test_validate_source(self):
        """Test YouTube URL validation"""
        adapter = YouTubeAdapter()
        
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ"
        ]
        
        invalid_urls = [
            "https://vimeo.com/123456",
            "https://example.com/video",
            "not a url"
        ]
        
        for url in valid_urls:
            # Mock the pytube validation to avoid network calls
            with patch('pytube.YouTube'):
                assert adapter.validate_source(url) == True
        
        for url in invalid_urls:
            assert adapter.validate_source(url) == False
    
    @pytest.mark.asyncio
    async def test_extract_content(self):
        """Test YouTube content extraction (mocked)"""
        adapter = YouTubeAdapter()
        
        # Mock pytube and whisper
        with patch.object(adapter, 'whisper_model_instance') as mock_whisper, \
             patch('pytube.YouTube') as mock_youtube, \
             patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('os.unlink') as mock_unlink:
            
            # Setup mocks
            mock_video = Mock()
            mock_video.title = "Test Video"
            mock_video.author = "Test Author"
            mock_video.video_id = "dQw4w9WgXcQ"
            mock_video.length = 180
            mock_video.views = 1000000
            mock_video.publish_date = "2023-01-01"
            
            mock_audio_stream = Mock()
            mock_video.streams.filter.return_value = [mock_audio_stream]
            
            mock_youtube.return_value = mock_video
            mock_whisper.transcribe.return_value = {"text": "This is a test transcription."}
            
            mock_temp.return_value.name = "/tmp/test.mp4"
            
            # Test extraction
            content, metadata = await adapter.extract_content("https://www.youtube.com/watch?v=test")
            
            assert content == "This is a test transcription."
            assert metadata["title"] == "Test Video"
            assert metadata["author"] == "Test Author"
            assert metadata["video_id"] == "dQw4w9WgXcQ"


class TestPDFAdapter:
    """Test PDF adapter"""
    
    def test_get_source_type(self):
        """Test PDF source type detection"""
        adapter = PDFAdapter()
        assert adapter.get_source_type() == SourceType.PDF
    
    def test_validate_source(self):
        """Test PDF source validation"""
        adapter = PDFAdapter()
        
        assert adapter.validate_source("document.pdf") == True
        assert adapter.validate_source("/path/to/document.pdf") == True
        assert adapter.validate_source("https://example.com/document.pdf") == True
        assert adapter.validate_source("document.txt") == False
        assert adapter.validate_source("not a file") == False
    
    @pytest.mark.asyncio
    async def test_extract_content(self):
        """Test PDF content extraction (mocked)"""
        adapter = PDFAdapter()
        
        # Create a temporary PDF file for testing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n299\n%%EOF")
            temp_path = temp_file.name
        
        try:
            with patch('fitz.open') as mock_open:
                # Mock PyMuPDF
                mock_doc = Mock()
                mock_page = Mock()
                mock_page.get_text.return_value = "Test PDF content"
                mock_doc.__len__ = Mock(return_value=1)
                mock_doc.load_page.return_value = mock_page
                mock_doc.metadata = {"title": "Test PDF", "author": "Test Author"}
                mock_open.return_value = mock_doc
                
                # Test extraction
                content, metadata = await adapter.extract_content(temp_path)
                
                assert "Test PDF content" in content
                assert metadata["title"] == "Test PDF"
                assert metadata["page_count"] == 1
                
        finally:
            os.unlink(temp_path)


class TestWebPageAdapter:
    """Test web page adapter"""
    
    def test_get_source_type(self):
        """Test web page source type detection"""
        adapter = WebPageAdapter()
        assert adapter.get_source_type() == SourceType.WEB_PAGE
    
    def test_validate_source(self):
        """Test web page URL validation"""
        adapter = WebPageAdapter()
        
        assert adapter.validate_source("https://example.com") == True
        assert adapter.validate_source("http://example.com") == True
        assert adapter.validate_source("ftp://example.com") == False
        assert adapter.validate_source("not a url") == False
    
    @pytest.mark.asyncio
    async def test_extract_content(self):
        """Test web page content extraction (mocked)"""
        adapter = WebPageAdapter()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="A test page">
            <meta name="author" content="Test Author">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a test paragraph.</p>
            <script>console.log('This should be removed');</script>
        </body>
        </html>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = html_content.encode('utf-8')
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Test extraction
            content, metadata = await adapter.extract_content("https://example.com")
            
            assert "Main Heading" in content
            assert "test paragraph" in content
            assert "console.log" not in content  # Script should be removed
            assert metadata["title"] == "Test Page"
            assert metadata["domain"] == "example.com"
            assert metadata["author"] == "Test Author"


class TestMarkdownAdapter:
    """Test Markdown adapter"""
    
    def test_get_source_type(self):
        """Test Markdown source type detection"""
        adapter = MarkdownAdapter()
        assert adapter.get_source_type() == SourceType.MARKDOWN
    
    def test_validate_source(self):
        """Test Markdown source validation"""
        adapter = MarkdownAdapter()
        
        assert adapter.validate_source("document.md") == True
        assert adapter.validate_source("document.markdown") == True
        assert adapter.validate_source("https://example.com/README.md") == True
        assert adapter.validate_source("document.txt") == False
    
    @pytest.mark.asyncio
    async def test_extract_content(self):
        """Test Markdown content extraction (mocked)"""
        adapter = MarkdownAdapter()
        
        markdown_content = "# Test Title\n\nThis is **bold** text and this is *italic*.\n\n```python\nprint('hello')\n```"
        
        with patch('builtins.open', create=True) as mock_open, \
             patch('markdown.Markdown') as mock_markdown:
            
            # Setup mocks
            mock_file = Mock()
            mock_file.read.return_value = markdown_content
            mock_open.return_value.__enter__.return_value = mock_file
            
            mock_md_instance = Mock()
            mock_md_instance.convert.return_value = "<h1>Test Title</h1><p>This is <strong>bold</strong> text...</p>"
            mock_markdown.return_value = mock_md_instance
            
            # Test extraction
            content, metadata = await adapter.extract_content("document.md")
            
            assert "Test Title" in content
            assert "bold" in content
            assert metadata["title"] == "Test Title"
            assert metadata["content_type"] == "text/markdown"


class TestPlainTextAdapter:
    """Test plain text adapter"""
    
    def test_get_source_type(self):
        """Test plain text source type detection"""
        adapter = PlainTextAdapter()
        assert adapter.get_source_type() == SourceType.PLAIN_TEXT
    
    def test_validate_source(self):
        """Test plain text source validation"""
        adapter = PlainTextAdapter()
        
        assert adapter.validate_source("document.txt") == True
        assert adapter.validate_source("data.csv") == True
        assert adapter.validate_source("config.json") == True
        assert adapter.validate_source("document.pdf") == False
        assert adapter.validate_source("not a file") == False
    
    @pytest.mark.asyncio
    async def test_extract_content(self):
        """Test plain text content extraction (mocked)"""
        adapter = PlainTextAdapter()
        
        text_content = "This is a test document.\n\nIt has multiple lines."
        
        with patch('builtins.open', create=True) as mock_open:
            # Setup mock
            mock_file = Mock()
            mock_file.read.return_value = text_content
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Test extraction
            content, metadata = await adapter.extract_content("document.txt")
            
            assert content == text_content
            assert metadata["title"] == "document"
            assert metadata["content_type"] == "text/plain"


class TestAdapterFactory:
    """Test adapter factory"""
    
    def test_get_supported_types(self):
        """Test getting supported source types"""
        factory = AdapterFactory()
        supported_types = factory.get_supported_types()
        
        assert SourceType.YOUTUBE in supported_types
        assert SourceType.PDF in supported_types
        assert SourceType.WEB_PAGE in supported_types
        assert SourceType.MARKDOWN in supported_types
        assert SourceType.PLAIN_TEXT in supported_types
        assert len(supported_types) == 5
    
    def test_get_adapter(self):
        """Test getting adapter instances"""
        factory = AdapterFactory()
        
        youtube_adapter = factory.get_adapter(SourceType.YOUTUBE)
        assert isinstance(youtube_adapter, YouTubeAdapter)
        
        pdf_adapter = factory.get_adapter(SourceType.PDF)
        assert isinstance(pdf_adapter, PDFAdapter)
    
    def test_detect_source_type(self):
        """Test automatic source type detection"""
        factory = AdapterFactory()
        
        # This test would require network access, so we'll just test the logic
        with patch.object(factory._adapters[SourceType.PDF], 'validate_source') as mock_validate:
            mock_validate.return_value = True
            detected_type = factory.detect_source_type("document.pdf")
            assert detected_type == SourceType.PDF
    
    def test_register_adapter(self):
        """Test registering new adapters"""
        factory = AdapterFactory()
        
        class CustomAdapter(BaseAdapter):
            def get_source_type(self):
                return "custom"
            
            def validate_source(self, source_url: str) -> bool:
                return True
            
            async def extract_content(self, source_url: str):
                return "content", {}
        
        factory.register_adapter("custom", CustomAdapter)
        assert "custom" in factory._adapters