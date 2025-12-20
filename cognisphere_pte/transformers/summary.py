from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cognisphere_pte.cache import TransformationCache
from cognisphere_pte.llm.providers.base import LLMGenerationConfig
from cognisphere_pte.llm.selector import HybridLLM
from cognisphere_pte.prompts import build_summary_prompt
from cognisphere_pte.utils.json import extract_json


@dataclass
class MultiSummary:
    brief: str
    medium: str
    detailed: str
    key_concepts: list[dict[str, Any]]
    related_topics: list[str]
    related_links: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "brief": self.brief,
            "medium": self.medium,
            "detailed": self.detailed,
            "key_concepts": self.key_concepts,
            "related_topics": self.related_topics,
            "related_links": self.related_links,
        }


class SummaryGenerator:
    def __init__(self, *, llm: HybridLLM | None = None, cache: TransformationCache | None = None):
        self.llm = llm or HybridLLM()
        self.cache = cache or TransformationCache()

    def generate(self, text: str) -> MultiSummary:
        params: dict[str, Any] = {}
        hit = self.cache.get(content=text, transform_type="summary", params=params)
        if hit:
            payload = hit.payload
            return MultiSummary(
                brief=payload.get("brief", ""),
                medium=payload.get("medium", ""),
                detailed=payload.get("detailed", ""),
                key_concepts=payload.get("key_concepts", []) or [],
                related_topics=payload.get("related_topics", []) or [],
                related_links=payload.get("related_links", []) or [],
            )

        prompt = build_summary_prompt(text)
        raw = self.llm.generate(
            prompt,
            config=LLMGenerationConfig(temperature=0.2, max_tokens=1200, top_p=0.95),
        )
        payload = extract_json(raw)
        out = self._validate(payload)

        self.cache.set(content=text, transform_type="summary", params=params, payload=out)
        return MultiSummary(
            brief=out["brief"],
            medium=out["medium"],
            detailed=out["detailed"],
            key_concepts=out.get("key_concepts", []),
            related_topics=out.get("related_topics", []),
            related_links=out.get("related_links", []),
        )

    def _validate(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Summary payload must be an object")
        for k in ("brief", "medium", "detailed"):
            if not isinstance(payload.get(k), str) or not payload[k].strip():
                raise ValueError(f"Summary payload missing '{k}'")
        if not isinstance(payload.get("key_concepts", []), list):
            payload["key_concepts"] = []
        if not isinstance(payload.get("related_topics", []), list):
            payload["related_topics"] = []
        if not isinstance(payload.get("related_links", []), list):
            payload["related_links"] = []
        return payload
