from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Content Ingestion Pipeline"
    debug: bool = True
    
    database_url: str = "sqlite:///./content_ingestion.db"
    lance_db_path: str = "./lancedb_data"
    upload_dir: str = "./uploads"
    
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    max_file_size: int = 52428800
    
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"


settings = Settings()

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.lance_db_path).mkdir(parents=True, exist_ok=True)
