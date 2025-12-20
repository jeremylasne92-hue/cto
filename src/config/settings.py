# Universal Ingestion Service Configuration

from pydantic import BaseSettings
from typing import Optional, Dict, Any


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Database Configuration
    sqlite_db_path: str = "ingestion.db"
    
    # Vector Database Configuration
    lancedb_path: str = "lancedb"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Chunking Configuration
    max_chunk_size: int = 1000
    chunk_overlap: int = 100
    min_chunk_size: int = 100
    similarity_threshold: float = 0.7
    
    # Processing Limits
    max_content_length: int = 1000000
    timeout_seconds: int = 300
    
    # Adapter Configuration
    youtube_whisper_model: str = "base"  # tiny, base, small, medium, large
    youtube_device: str = "auto"  # auto, cpu, cuda
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()