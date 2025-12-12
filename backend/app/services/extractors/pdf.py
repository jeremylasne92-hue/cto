import fitz
import pdfplumber
from typing import Dict, Any
from app.services.extractors.base import BaseExtractor


class PDFExtractor(BaseExtractor):
    
    def extract(self, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        file_path = metadata.get('file_path', source)
        
        content = {
            'text': '',
            'title': '',
            'author': '',
            'pages': 0,
            'has_images': False,
            'has_tables': False,
        }
        
        try:
            doc = fitz.open(file_path)
            content['pages'] = len(doc)
            
            pdf_metadata = doc.metadata
            content['title'] = pdf_metadata.get('title', '')
            content['author'] = pdf_metadata.get('author', '')
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                content['text'] += page.get_text()
                
                if page.get_images():
                    content['has_images'] = True
            
            doc.close()
        except Exception as e:
            raise Exception(f"Error extracting PDF with PyMuPDF: {str(e)}")
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        content['has_tables'] = True
                        for table in tables:
                            table_text = '\n'.join(['\t'.join([str(cell) for cell in row]) for row in table])
                            content['text'] += f"\n\n[TABLE]\n{table_text}\n[/TABLE]\n\n"
        except Exception as e:
            pass
        
        return content
    
    def extract_metadata(self, source: str) -> Dict[str, Any]:
        try:
            doc = fitz.open(source)
            metadata = doc.metadata
            pages = len(doc)
            doc.close()
            
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'pages': pages,
            }
        except Exception as e:
            return {'error': str(e)}
