import markdown
from typing import Dict, Any
from app.services.extractors.base import BaseExtractor
import re


class MarkdownExtractor(BaseExtractor):
    
    def extract(self, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        file_path = metadata.get('file_path', source)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        title = ''
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        
        html = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
        
        content = {
            'text': md_content,
            'html': html,
            'title': title,
            'author': '',
        }
        
        return content
    
    def extract_metadata(self, source: str) -> Dict[str, Any]:
        with open(source, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        metadata = {
            'title': '',
            'author': '',
        }
        
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1)
        
        frontmatter_match = re.match(r'^---\n(.*?)\n---', md_content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        
        return metadata
