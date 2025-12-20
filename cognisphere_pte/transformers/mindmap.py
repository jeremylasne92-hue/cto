from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cognisphere_pte.cache import TransformationCache
from cognisphere_pte.llm.providers.base import LLMGenerationConfig
from cognisphere_pte.llm.selector import HybridLLM
from cognisphere_pte.prompts import build_mindmap_prompt
from cognisphere_pte.utils.json import extract_json


@dataclass
class MindMap:
    root: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"root": self.root}


class MindMapGenerator:
    def __init__(self, *, llm: HybridLLM | None = None, cache: TransformationCache | None = None):
        self.llm = llm or HybridLLM()
        self.cache = cache or TransformationCache()

    def generate(self, text: str) -> MindMap:
        params: dict[str, Any] = {}
        hit = self.cache.get(content=text, transform_type="mindmap", params=params)
        if hit:
            payload = hit.payload
            root = payload.get("root") if isinstance(payload, dict) else None
            if isinstance(root, dict):
                return MindMap(root=root)

        prompt = build_mindmap_prompt(text)
        raw = self.llm.generate(
            prompt,
            config=LLMGenerationConfig(temperature=0.25, max_tokens=900, top_p=0.95),
        )
        payload = extract_json(raw)
        root = self._validate(payload)

        out = {"root": root}
        self.cache.set(content=text, transform_type="mindmap", params=params, payload=out)
        return MindMap(root=root)

    def _validate(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict) or not isinstance(payload.get("root"), dict):
            raise ValueError("Mind map payload must be an object with a 'root' object")
        root = payload["root"]
        if not root.get("label") or not isinstance(root.get("children"), list):
            raise ValueError("Mind map root must include label and children")
        return root
