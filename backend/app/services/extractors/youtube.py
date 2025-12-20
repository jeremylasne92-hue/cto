import yt_dlp
from typing import Dict, Any
from app.services.extractors.base import BaseExtractor
import tempfile
import os


class YouTubeExtractor(BaseExtractor):
    
    def extract(self, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        video_id = metadata.get('video_id')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=False)
            
            content = {
                'text': '',
                'title': info.get('title', ''),
                'author': info.get('uploader', ''),
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', ''),
                'description': info.get('description', ''),
            }
            
            if 'subtitles' in info and info['subtitles']:
                for lang, subs in info['subtitles'].items():
                    for sub in subs:
                        if sub.get('ext') in ['vtt', 'srt']:
                            content['text'] += f"\n{sub.get('data', '')}"
                            break
                    break
            
            if 'automatic_captions' in info and info['automatic_captions'] and not content['text']:
                for lang, captions in info['automatic_captions'].items():
                    for caption in captions:
                        if caption.get('ext') in ['vtt', 'srt']:
                            content['text'] += f"\n{caption.get('data', '')}"
                            break
                    break
            
            if not content['text'] and content['description']:
                content['text'] = content['description']
            
            return content
    
    def extract_metadata(self, source: str) -> Dict[str, Any]:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=False)
            
            return {
                'title': info.get('title', ''),
                'author': info.get('uploader', ''),
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', ''),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'channel': info.get('channel', ''),
                'channel_id': info.get('channel_id', ''),
            }
