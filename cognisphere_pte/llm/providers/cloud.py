from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from enum import Enum

from .base import LLMError, LLMGenerationConfig


class CloudProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"


@dataclass(frozen=True)
class CloudModelConfig:
    provider: CloudProvider
    model: str


DEFAULT_CLOUD_MODELS: dict[CloudProvider, CloudModelConfig] = {
    CloudProvider.OPENAI: CloudModelConfig(CloudProvider.OPENAI, os.environ.get("COGNISPHERE_PTE_OPENAI_MODEL", "gpt-4o-mini")),
    CloudProvider.ANTHROPIC: CloudModelConfig(CloudProvider.ANTHROPIC, os.environ.get("COGNISPHERE_PTE_ANTHROPIC_MODEL", "claude-3-5-haiku-latest")),
    CloudProvider.GROQ: CloudModelConfig(CloudProvider.GROQ, os.environ.get("COGNISPHERE_PTE_GROQ_MODEL", "llama-3.1-8b-instant")),
}


def _pick_provider() -> CloudProvider:
    forced = os.environ.get("COGNISPHERE_PTE_CLOUD_PROVIDER")
    if forced:
        return CloudProvider(forced.lower())

    if os.environ.get("OPENAI_API_KEY"):
        return CloudProvider.OPENAI
    if os.environ.get("ANTHROPIC_API_KEY"):
        return CloudProvider.ANTHROPIC
    if os.environ.get("GROQ_API_KEY"):
        return CloudProvider.GROQ

    return CloudProvider.OPENAI


@dataclass
class CloudLLMClient:
    provider: CloudProvider | None = None
    model: str | None = None

    def _cfg(self) -> CloudModelConfig:
        provider = self.provider or _pick_provider()
        base = DEFAULT_CLOUD_MODELS[provider]
        return CloudModelConfig(provider=provider, model=self.model or base.model)

    def generate(self, prompt: str, *, config: LLMGenerationConfig | None = None) -> str:
        cfg = config or LLMGenerationConfig()
        model_cfg = self._cfg()

        if model_cfg.provider == CloudProvider.OPENAI:
            return self._openai(prompt, cfg, model_cfg.model)
        if model_cfg.provider == CloudProvider.ANTHROPIC:
            return self._anthropic(prompt, cfg, model_cfg.model)
        if model_cfg.provider == CloudProvider.GROQ:
            return self._groq(prompt, cfg, model_cfg.model)

        raise LLMError(f"Unsupported provider: {model_cfg.provider}")

    def _openai(self, prompt: str, cfg: LLMGenerationConfig, model: str) -> str:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise LLMError("OPENAI_API_KEY is not set")

        url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions"
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful tutor that outputs ONLY valid JSON when asked."},
                {"role": "user", "content": prompt},
            ],
            "temperature": cfg.temperature,
            "top_p": cfg.top_p,
            "max_tokens": cfg.max_tokens,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data["choices"][0]["message"]["content"].strip()

    def _groq(self, prompt: str, cfg: LLMGenerationConfig, model: str) -> str:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise LLMError("GROQ_API_KEY is not set")

        url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1") + "/chat/completions"
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful tutor that outputs ONLY valid JSON when asked."},
                {"role": "user", "content": prompt},
            ],
            "temperature": cfg.temperature,
            "top_p": cfg.top_p,
            "max_tokens": cfg.max_tokens,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data["choices"][0]["message"]["content"].strip()

    def _anthropic(self, prompt: str, cfg: LLMGenerationConfig, model: str) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise LLMError("ANTHROPIC_API_KEY is not set")

        url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com") + "/v1/messages"
        body = {
            "model": model,
            "max_tokens": cfg.max_tokens,
            "temperature": cfg.temperature,
            "top_p": cfg.top_p,
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "x-api-key": key,
                "anthropic-version": os.environ.get("ANTHROPIC_VERSION", "2023-06-01"),
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Anthropics response format: content: [{type: 'text', text: '...'}]
        parts = data.get("content") or []
        texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
        return "".join(texts).strip()
