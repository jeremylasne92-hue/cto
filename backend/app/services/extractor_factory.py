from app.services.extractors import (
    YouTubeExtractor,
    PDFExtractor,
    WebExtractor,
    EPUBExtractor,
    DOCXExtractor,
    MarkdownExtractor,
    TextExtractor,
)


class ExtractorFactory:
    
    EXTRACTORS = {
        'youtube': YouTubeExtractor,
        'pdf': PDFExtractor,
        'web': WebExtractor,
        'epub': EPUBExtractor,
        'docx': DOCXExtractor,
        'markdown': MarkdownExtractor,
        'text': TextExtractor,
    }
    
    @classmethod
    def get_extractor(cls, source_type: str):
        extractor_class = cls.EXTRACTORS.get(source_type)
        if not extractor_class:
            raise ValueError(f"Unsupported source type: {source_type}")
        return extractor_class()
