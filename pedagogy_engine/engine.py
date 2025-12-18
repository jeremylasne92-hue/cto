from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

from .cache.embedding import HashingEmbedder
from .cache.store import CacheStore
from .llm.hybrid import get_default_llm
from .transform.mindmap import MindMapGenerator
from .transform.quiz import QuizGenerator
from .transform.socratic import SOCRATIC_PROMPTS
from .transform.summary import SummaryGenerator

ArtifactType = Literal["quiz", "mindmap", "summary"]


def _normalize_text(text: str) -> str:
    return " ".join(text.split())


def _content_hash(text: str) -> str:
    return hashlib.sha256(_normalize_text(text).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TransformationEngine:
    """High-level facade for generating pedagogy artifacts with caching and reuse."""

    cache: CacheStore | None = None
    similarity_threshold: float = 0.92

    def __post_init__(self) -> None:
        if self.cache is None:
            object.__setattr__(self, "cache", CacheStore())

    def generate_quiz(
        self,
        content: str | list[str],
        *,
        num_questions: int = 5,
        difficulty_target: int | None = None,
        allow_reuse: bool = True,
    ) -> dict[str, Any]:
        text = "\n\n".join(content) if isinstance(content, list) else content
        return self._generate(
            "quiz",
            text,
            allow_reuse=allow_reuse,
            generator=lambda llm: QuizGenerator(llm=llm).generate(
                text,
                num_questions=num_questions,
                difficulty_target=difficulty_target,
            ),
        )

    def generate_mind_map(
        self,
        content: str,
        *,
        topic: str | None = None,
        allow_reuse: bool = True,
    ) -> dict[str, Any]:
        return self._generate(
            "mindmap",
            content,
            allow_reuse=allow_reuse,
            generator=lambda llm: MindMapGenerator(llm=llm).generate(content, topic=topic),
        )

    def generate_summaries(
        self,
        content: str,
        *,
        allow_reuse: bool = True,
    ) -> dict[str, Any]:
        return self._generate(
            "summary",
            content,
            allow_reuse=allow_reuse,
            generator=lambda llm: SummaryGenerator(llm=llm).generate(content),
        )

    def get_socratic_prompts(self) -> dict[str, Any]:
        return json.loads(json.dumps(SOCRATIC_PROMPTS))

    def _generate(
        self,
        artifact_type: ArtifactType,
        content: str,
        *,
        allow_reuse: bool,
        generator: Any,
    ) -> dict[str, Any]:
        content_hash = _content_hash(content)
        cache = self.cache
        if cache is None:
            llm = get_default_llm()
            return generator(llm)

        if allow_reuse:
            hit = cache.get_exact(artifact_type, content_hash)
            if hit is not None:
                return hit

            embedder = HashingEmbedder()
            query_embedding = embedder.embed(content)
            similar = cache.find_similar(
                artifact_type,
                query_embedding,
                similarity_threshold=self.similarity_threshold,
            )
            if similar is not None:
                return similar

        llm = get_default_llm()
        payload = generator(llm)

        embedder = HashingEmbedder()
        embedding = embedder.embed(content)
        cache.put(artifact_type, content_hash, embedding, payload)
        return payload
