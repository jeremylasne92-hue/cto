from .base import BaseAdapter
from ..models import SourceType
from typing import Dict, Any
import os
import tempfile
import whisper
import pytube
import torch


class YouTubeAdapter(BaseAdapter):
    """Adapter for YouTube videos using pytube and Whisper"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.whisper_model = config.get("whisper_model", "base")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._whisper_model_instance = None
    
    def get_source_type(self):
        return SourceType.YOUTUBE
    
    def validate_source(self, source_url: str) -> bool:
        """Validate YouTube URL"""
        try:
            pytube.YouTube(source_url)
            return True
        except:
            return False
    
    @property
    def whisper_model_instance(self):
        """Lazy load Whisper model"""
        if self._whisper_model_instance is None:
            self._whisper_model_instance = whisper.load_model(
                self.whisper_model, 
                device=self.device
            )
        return self._whisper_model_instance
    
    async def extract_content(self, source_url: str) -> tuple[str, Dict[str, Any]]:
        """Extract audio and transcribe with Whisper"""
        try:
            # Download audio using pytube
            youtube = pytube.YouTube(source_url)
            audio_stream = youtube.streams.filter(only_audio=True).first()
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                audio_file_path = temp_file.name
            
            # Download audio
            audio_stream.download(filename=audio_file_path)
            
            # Transcribe with Whisper
            result = self.whisper_model_instance.transcribe(
                audio_file_path,
                task="transcribe",
                language="en"
            )
            
            transcription_text = result["text"].strip()
            
            # Extract metadata
            metadata = {
                "title": youtube.title,
                "author": youtube.author,
                "url": source_url,
                "video_id": youtube.video_id,
                "duration": youtube.length,
                "view_count": youtube.views,
                "created_at": youtube.publish_date,
                "content_type": "audio/mp4",
            }
            
            # Clean up temporary file
            os.unlink(audio_file_path)
            
            return transcription_text, metadata
            
        except Exception as e:
            # Clean up on error
            if 'audio_file_path' in locals() and os.path.exists(audio_file_path):
                os.unlink(audio_file_path)
            raise Exception(f"YouTube extraction failed: {str(e)}")