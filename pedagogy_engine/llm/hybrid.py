from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

from .base import BaseLLM, LLM, ModelUnavailableError, OutOfMemoryError
from .cloud import AnthropicMessagesLLM, OpenAICompatibleChatLLM
from .local_llama_cpp import LlamaCppLocalLLM
from .offline import OfflineLLM
from .selector import default_local_model_for_tier, detect_hardware_tier


@dataclass
class FailoverLLM(BaseLLM):
    """Fallback wrapper that switches to a secondary provider on failure.

    Used to gracefully recover from local OOM / load failures by switching to a
    cloud provider (or offline mode).
    """

    primary: LLM
    fallback_factory: Callable[[], LLM]
    _fallback: LLM | None = None

    def _get_fallback(self) -> LLM:
        if self._fallback is None:
            try:
                self._fallback = self.fallback_factory()
            except ModelUnavailableError as e:
                self._fallback = OfflineLLM(reason=str(e))
        return self._fallback

    def generate_text(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        try:
            return self.primary.generate_text(prompt, temperature=temperature, max_tokens=max_tokens)
        except (OutOfMemoryError, ModelUnavailableError):
            fallback = self._get_fallback()
            return fallback.generate_text(prompt, temperature=temperature, max_tokens=max_tokens)


@dataclass
class HybridLLM:
    """Chooses the best available LLM based on hardware tier and availability."""

    tier: str | None = None

    def _provider_preference(self) -> list[str]:
        pref = os.environ.get("PEDAGOGY_ENGINE_CLOUD_PROVIDER")
        if pref:
            return [p.strip().lower() for p in pref.split(",") if p.strip()]
        return ["openai", "groq", "anthropic"]

    def _cloud_llm(self) -> LLM:
        for provider in self._provider_preference():
            if provider in {"openai", "groq"}:
                return OpenAICompatibleChatLLM.from_env()
            if provider == "anthropic":
                return AnthropicMessagesLLM.from_env()

        raise ModelUnavailableError("No supported cloud provider configured")

    def get(self) -> LLM:
        tier = self.tier or detect_hardware_tier()
        mode = os.environ.get("PEDAGOGY_ENGINE_MODE", "hybrid").lower().strip()

        allow_download_raw = os.environ.get("PEDAGOGY_ENGINE_ALLOW_DOWNLOAD")
        if allow_download_raw is None:
            allow_download = (
                os.environ.get("CI") is None
                and os.environ.get("HF_HUB_OFFLINE", "0") not in {"1", "true", "yes"}
                and os.environ.get("TRANSFORMERS_OFFLINE", "0") not in {"1", "true", "yes"}
            )
        else:
            allow_download = allow_download_raw.lower().strip() in {"1", "true", "yes"}

        if mode == "cloud":
            try:
                return self._cloud_llm()
            except ModelUnavailableError as e:
                return OfflineLLM(reason=str(e))

        if mode in {"local", "hybrid"}:
            spec = default_local_model_for_tier(tier) if tier in {"premium", "standard", "minimum"} else None
            if spec is not None:
                try:
                    local = LlamaCppLocalLLM.from_spec(spec, tier=tier, allow_download=allow_download)
                    return FailoverLLM(primary=local, fallback_factory=self._cloud_llm)
                except OutOfMemoryError:
                    try:
                        return self._cloud_llm()
                    except ModelUnavailableError as e:
                        return OfflineLLM(reason=str(e))
                except ModelUnavailableError:
                    # Local unavailable (dependencies or download). Fall back to cloud for minimum tier,
                    # or for any tier when local isn't usable.
                    try:
                        return self._cloud_llm()
                    except ModelUnavailableError as e:
                        return OfflineLLM(reason=str(e))

        # Minimum tier: default to cloud; if not configured, go offline.
        try:
            return self._cloud_llm()
        except ModelUnavailableError as e:
            return OfflineLLM(reason=str(e))


_default: LLM | None = None


def get_default_llm() -> LLM:
    global _default
    if _default is None:
        _default = HybridLLM().get()
    return _default
