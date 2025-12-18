from __future__ import annotations

from dataclasses import dataclass

from .base import BaseLLM


@dataclass
class OfflineLLM(BaseLLM):
    """Fallback LLM used when neither local nor cloud providers are available.

    The transformation generators use task-specific heuristics when the engine
    is running with :class:`OfflineLLM`.
    """

    reason: str = "No local or cloud LLM configured"

    def generate_text(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        return (
            "[OFFLINE MODE]\n"
            "No LLM available to answer the prompt. Configure a cloud API key or install local model dependencies.\n\n"
            f"Reason: {self.reason}\n\n"
            "Prompt was:\n"
            + prompt[:2000]
        )
