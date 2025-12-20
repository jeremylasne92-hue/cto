import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from app.services.extractors.base import BaseExtractor


class WebExtractor(BaseExtractor):
    
    def extract(self, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        url = metadata.get('url', source)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ''
        
        author = ''
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            author = author_meta.get('content', '')
        
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        text = main_content.get_text(separator='\n', strip=True) if main_content else ''
        
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'text': link.get_text().strip(),
                'href': link['href']
            })
        
        return {
            'text': text,
            'title': title_text,
            'author': author,
            'url': url,
            'links': links[:50],
        }
    
    def extract_metadata(self, source: str) -> Dict[str, Any]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(source, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        metadata = {
            'url': source,
            'title': '',
            'description': '',
            'author': '',
            'publish_date': '',
        }
        
        title = soup.find('title')
        if title:
            metadata['title'] = title.get_text().strip()
        
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['title'] = og_title.get('content', metadata['title'])
        
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            metadata['description'] = description.get('content', '')
        
        author = soup.find('meta', attrs={'name': 'author'})
        if author:
            metadata['author'] = author.get('content', '')
        
        return metadata
