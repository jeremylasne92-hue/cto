from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cognisphere_pte.embeddings import EmbeddingModel, cosine_similarity
from cognisphere_pte.storage import ensure_dir, get_cache_dir


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _canonicalize_content(content: str) -> str:
    return re.sub(r"\s+", " ", content).strip()


@dataclass
class CacheHit:
    kind: str  # exact | similar
    content_hash: str
    similarity: float
    payload: dict[str, Any]


class TransformationCache:
    def __init__(self, *, similarity_threshold: float = 0.93):
        self.similarity_threshold = similarity_threshold
        self.base_dir = ensure_dir(get_cache_dir() / "pte")
        self.artifacts_dir = ensure_dir(self.base_dir / "artifacts")
        self.db_path = self.base_dir / "index.sqlite"
        self._init_db()
        self._embedder = EmbeddingModel()

    def _init_db(self) -> None:
        ensure_dir(self.base_dir)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS embeddings (
                    content_hash TEXT PRIMARY KEY,
                    embedding_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transformations (
                    key TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    transform_type TEXT NOT NULL,
                    params_hash TEXT NOT NULL,
                    artifact_path TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    def _key(self, content_hash: str, transform_type: str, params_hash: str) -> str:
        return f"{transform_type}:{content_hash}:{params_hash}"

    def _artifact_path(self, key: str) -> Path:
        return self.artifacts_dir / f"{key.replace(':', '_')}.json"

    def _upsert_embedding(self, content_hash: str, embedding: list[float]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO embeddings (content_hash, embedding_json, created_at) VALUES (?, ?, ?)",
                (content_hash, _stable_json(embedding), time.time()),
            )

    def _find_most_similar(self, embedding: list[float]) -> tuple[str | None, float]:
        best_hash: str | None = None
        best_sim = 0.0
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT content_hash, embedding_json FROM embeddings").fetchall()

        for content_hash, emb_json in rows:
            try:
                other = json.loads(emb_json)
                sim = cosine_similarity(embedding, other)
            except Exception:
                continue
            if sim > best_sim:
                best_sim = sim
                best_hash = content_hash

        return best_hash, best_sim

    def get(self, *, content: str, transform_type: str, params: dict[str, Any]) -> CacheHit | None:
        canonical = _canonicalize_content(content)
        content_hash = _sha256(canonical)
        params_hash = _sha256(_stable_json(params))
        key = self._key(content_hash, transform_type, params_hash)

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT artifact_path FROM transformations WHERE key = ?",
                (key,),
            ).fetchone()

        if row:
            artifact_path = Path(row[0])
            if artifact_path.exists():
                return CacheHit(kind="exact", content_hash=content_hash, similarity=1.0, payload=json.loads(artifact_path.read_text("utf-8")))

        embedding = self._embedder.embed(canonical)
        similar_hash, sim = self._find_most_similar(embedding)
        if not similar_hash or sim < self.similarity_threshold:
            self._upsert_embedding(content_hash, embedding)
            return None

        similar_key = self._key(similar_hash, transform_type, params_hash)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT artifact_path FROM transformations WHERE key = ?",
                (similar_key,),
            ).fetchone()

        if row:
            artifact_path = Path(row[0])
            if artifact_path.exists():
                # Also index embedding for current content hash for faster next time.
                self._upsert_embedding(content_hash, embedding)
                return CacheHit(kind="similar", content_hash=similar_hash, similarity=sim, payload=json.loads(artifact_path.read_text("utf-8")))

        self._upsert_embedding(content_hash, embedding)
        return None

    def set(self, *, content: str, transform_type: str, params: dict[str, Any], payload: dict[str, Any]) -> None:
        canonical = _canonicalize_content(content)
        content_hash = _sha256(canonical)
        params_hash = _sha256(_stable_json(params))
        key = self._key(content_hash, transform_type, params_hash)
        artifact_path = self._artifact_path(key)

        artifact_path.write_text(_stable_json(payload), "utf-8")
        self._upsert_embedding(content_hash, self._embedder.embed(canonical))
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO transformations (key, content_hash, transform_type, params_hash, artifact_path, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (key, content_hash, transform_type, params_hash, str(artifact_path), time.time()),
            )
