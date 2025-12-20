from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LLMError(RuntimeError):
    pass


class LLMOutOfMemoryError(LLMError):
    pass


@dataclass(frozen=True)
class LLMGenerationConfig:
    temperature: float = 0.4
    max_tokens: int = 800
    top_p: float = 0.95


class LLMClient(Protocol):
    def generate(self, prompt: str, *, config: LLMGenerationConfig | None = None) -> str: ...
