from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from ..llm.base import LLM
from ..llm.offline import OfflineLLM


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]


def _truncate_words(text: str, n_words: int) -> str:
    words = text.split()
    if len(words) <= n_words:
        return text.strip()
    return " ".join(words[:n_words]).strip() + "…"


def _keywords(text: str, *, top_n: int = 10) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_'-]{3,}", text.lower())
    stop = {
        "that",
        "this",
        "with",
        "from",
        "into",
        "your",
        "their",
        "there",
        "which",
        "also",
        "have",
        "has",
        "were",
        "been",
        "will",
        "would",
        "should",
        "could",
        "than",
        "then",
        "when",
        "where",
        "what",
        "about",
        "because",
        "between",
    }
    freq: dict[str, int] = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1

    ranked = sorted(freq.items(), key=lambda kv: (kv[1], len(kv[0])), reverse=True)
    return [w.title() for w, _ in ranked[:top_n]]


@dataclass
class SummaryGenerator:
    llm: LLM

    def generate(self, content: str) -> dict[str, Any]:
        if not isinstance(self.llm, OfflineLLM):
            try:
                return self._generate_with_llm(content)
            except Exception:
                pass
        return self._generate_heuristic(content)

    def _generate_with_llm(self, content: str) -> dict[str, Any]:
        prompt = (
            "Generate multi-level summaries. Output ONLY valid JSON.\n\n"
            "Return:\n"
            "- brief: ~50 words\n"
            "- medium: ~200 words\n"
            "- detailed: ~500 words\n"
            "- key_concepts: 5-12 bullet items\n"
            "- related_links: list of {title,url}\n\n"
            "JSON schema: { 'version':'1', 'brief':'...', 'medium':'...', 'detailed':'...', 'key_concepts':[...], 'related_links':[{'title':'','url':''}] }\n\n"
            "Content:\n"
            + content[:12000]
        )

        out = self.llm.generate_json(prompt, temperature=0.2, max_tokens=1400)
        if not isinstance(out, dict):
            raise ValueError("LLM did not return an object")
        out.setdefault("version", "1")
        return out

    def _generate_heuristic(self, content: str) -> dict[str, Any]:
        sents = _sentences(content)
        joined = " ".join(sents)

        brief = _truncate_words(joined, 50)
        medium = _truncate_words(joined, 200)
        detailed = _truncate_words(joined, 500)

        key_concepts = _keywords(content, top_n=10)
        related_links = [
            {"title": c, "url": f"https://en.wikipedia.org/wiki/{quote(c.replace(' ', '_'))}"}
            for c in key_concepts[:6]
        ]

        return {
            "version": "1",
            "generator": "heuristic",
            "brief": brief,
            "medium": medium,
            "detailed": detailed,
            "key_concepts": key_concepts,
            "related_links": related_links,
        }
