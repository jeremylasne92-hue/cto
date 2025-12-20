from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


@dataclass
class EmbeddingModel:
    dims: int = 384

    def embed(self, text: str) -> list[float]:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            model = SentenceTransformer(model_name)
            vec = model.encode([text], normalize_embeddings=True)[0]
            return [float(x) for x in vec.tolist()]
        except Exception:
            return self._hash_embed(text)

    def _hash_embed(self, text: str) -> list[float]:
        # Lightweight deterministic embedding (fallback) for similarity reuse.
        v = [0.0] * self.dims
        tokens = _normalize(text).split(" ")
        if not tokens:
            return v

        for t in tokens:
            h = hashlib.sha256(t.encode("utf-8")).digest()
            idx = int.from_bytes(h[:4], "little") % self.dims
            sign = -1.0 if (h[4] & 1) else 1.0
            v[idx] += sign

        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))
