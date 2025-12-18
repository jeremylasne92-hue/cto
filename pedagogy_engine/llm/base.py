from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol


class LLMError(RuntimeError):
    pass


class ModelUnavailableError(LLMError):
    pass


class OutOfMemoryError(LLMError):
    pass


class LLM(Protocol):
    """A minimal interface used by the transformation engine."""

    def generate_text(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str: ...

    def generate_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Any:
        ...


@dataclass
class BaseLLM:
    """Convenience base class implementing :meth:`generate_json` on top of text generation."""

    def generate_text(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str:  # pragma: no cover
        raise NotImplementedError

    def generate_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Any:
        text = self.generate_text(prompt, temperature=temperature, max_tokens=max_tokens)
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError as e:
                raise LLMError(f"Failed to parse JSON output from model: {e}") from e

        raise LLMError("Failed to parse JSON output from model")
