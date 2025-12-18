from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Any

from ..llm.base import LLM
from ..llm.offline import OfflineLLM
from .quality import validate_mindmap


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if len(s.split()) >= 6]


def _pick_root(topic: str | None, content: str) -> str:
    if topic and topic.strip():
        return topic.strip()
    sents = _sentences(content)
    if not sents:
        return "Mind Map"
    first = sents[0]
    return " ".join(first.split()[:10]).strip(" .,:;()[]{}\"'")


def _extract_headings(content: str) -> list[str]:
    headings: list[str] = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            headings.append(line.lstrip("#").strip())
            continue
        if len(line) <= 70 and line.isupper() and len(line.split()) <= 8:
            headings.append(line.title())
    # Deduplicate
    out: list[str] = []
    seen = set()
    for h in headings:
        k = h.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(h)
    return out


def _keywords(content: str, *, max_n: int = 7) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_'-]{3,}", content.lower())
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
    return [w.title() for w, _ in ranked[:max_n]]


def _make_node(name: str, children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    node: dict[str, Any] = {"id": str(uuid.uuid4()), "name": name}
    if children is not None:
        node["children"] = children
    return node


@dataclass
class MindMapGenerator:
    llm: LLM

    def generate(self, content: str, *, topic: str | None = None) -> dict[str, Any]:
        if not isinstance(self.llm, OfflineLLM):
            try:
                mm = self._generate_with_llm(content, topic=topic)
                if not validate_mindmap(mm):
                    return mm
            except Exception:
                pass

        return self._generate_heuristic(content, topic=topic)

    def _generate_with_llm(self, content: str, *, topic: str | None) -> dict[str, Any]:
        prompt = (
            "Create a hierarchical mind map from the content. Output ONLY valid JSON.\n\n"
            "Requirements:\n"
            "- A single root node with 3-7 children (major branches).\n"
            "- Each major branch has 2-5 sub-branches; leaves contain specific details/examples.\n"
            "- Output should be ready for D3.js: use {name, children}.\n\n"
            "JSON schema:\n"
            "{ 'version':'1', 'root': { 'name': '...', 'children': [ ... ] } }\n\n"
            f"Topic override (if present): {topic or ''}\n\n"
            "Content:\n"
            + content[:12000]
        )

        out = self.llm.generate_json(prompt, temperature=0.2, max_tokens=1200)
        if not isinstance(out, dict):
            raise ValueError("LLM did not return an object")

        out.setdefault("version", "1")
        return out

    def _generate_heuristic(self, content: str, *, topic: str | None) -> dict[str, Any]:
        root_name = _pick_root(topic, content)

        headings = _extract_headings(content)
        branches = headings[:7]
        if len(branches) < 3:
            branches = _keywords(content, max_n=7)

        branches = branches[:7]
        if len(branches) < 3:
            branches = ["Overview", "Key Ideas", "Examples"]

        sents = _sentences(content)

        children: list[dict[str, Any]] = []
        for b in branches[:7]:
            lower_b = b.lower()
            related = [s for s in sents if lower_b.split()[0] in s.lower()]
            related = related[:5]

            sub: list[dict[str, Any]] = []
            for s in related[:4]:
                leaf = " ".join(s.split()[:14]).strip(" .,:;()[]{}\"'")
                sub.append(_make_node(leaf))

            if len(sub) < 2:
                # fallback: generic sub-branches
                sub.extend([_make_node("Definition"), _make_node("Why it matters")][: 2 - len(sub)])

            children.append(_make_node(b, children=sub[:5]))

        mindmap = {"version": "1", "generator": "heuristic", "root": _make_node(root_name, children=children[:7])}

        # Ensure compliance (3-7 major branches)
        while len(mindmap["root"]["children"]) < 3:
            mindmap["root"]["children"].append(_make_node(f"Branch {len(mindmap['root']['children']) + 1}", children=[]))

        return mindmap
