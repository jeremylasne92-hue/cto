from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.config import settings


class EmbeddingGenerator:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingGenerator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._model = SentenceTransformer(settings.embedding_model)
    
    def generate(self, text: str) -> List[float]:
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
