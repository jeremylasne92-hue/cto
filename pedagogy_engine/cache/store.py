from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Literal

from .embedding import cosine_similarity

ArtifactType = Literal["quiz", "mindmap", "summary"]


def _default_cache_path() -> str:
    root = os.path.join(os.path.expanduser("~"), ".cache", "pedagogy_engine")
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, "cache.sqlite")


@dataclass
class CacheStore:
    path: str = ""

    def __post_init__(self) -> None:
        if not self.path:
            self.path = _default_cache_path()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artifact_type TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_exact
                ON artifacts(artifact_type, content_hash)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_artifacts_type
                ON artifacts(artifact_type)
                """
            )

    def get_exact(self, artifact_type: ArtifactType, content_hash: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT payload_json
                FROM artifacts
                WHERE artifact_type = ? AND content_hash = ?
                """,
                (artifact_type, content_hash),
            ).fetchone()
            if not row:
                return None
            return json.loads(row[0])

    def put(
        self,
        artifact_type: ArtifactType,
        content_hash: str,
        embedding: list[float],
        payload: dict[str, Any],
    ) -> None:
        embedding_json = json.dumps(embedding)
        payload_json = json.dumps(payload)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO artifacts (artifact_type, content_hash, embedding_json, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (artifact_type, content_hash, embedding_json, payload_json, time.time()),
            )

    def find_similar(
        self,
        artifact_type: ArtifactType,
        query_embedding: list[float],
        *,
        similarity_threshold: float,
        max_candidates: int = 50,
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT embedding_json, payload_json
                FROM artifacts
                WHERE artifact_type = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (artifact_type, max_candidates),
            ).fetchall()

        best_score = similarity_threshold
        best_payload: dict[str, Any] | None = None
        for embedding_json, payload_json in rows:
            try:
                emb = json.loads(embedding_json)
            except Exception:
                continue
            score = cosine_similarity(query_embedding, emb)
            if score >= best_score:
                best_score = score
                best_payload = json.loads(payload_json)

        return best_payload
