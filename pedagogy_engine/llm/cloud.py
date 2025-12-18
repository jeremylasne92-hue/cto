from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass

from .base import BaseLLM, ModelUnavailableError


@dataclass
class OpenAICompatibleChatLLM(BaseLLM):
    """Cloud LLM using an OpenAI-compatible Chat Completions endpoint.

    Works for OpenAI and Groq (OpenAI-compatible base URL).
    """

    api_key: str
    model: str
    base_url: str = "https://api.openai.com/v1"

    @classmethod
    def from_env(cls) -> "OpenAICompatibleChatLLM":
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            return cls(api_key=api_key, model=model, base_url=base_url)

        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key:
            model = os.environ.get("GROQ_MODEL", "llama-3.1-70b-versatile")
            base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
            return cls(api_key=groq_key, model=model, base_url=base_url)

        raise ModelUnavailableError("No OPENAI_API_KEY or GROQ_API_KEY configured")

    def generate_text(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful tutor that outputs only the requested format."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except Exception as e:  # pragma: no cover
            raise ModelUnavailableError(f"Cloud request failed: {e}") from e

        parsed = json.loads(raw)
        try:
            return parsed["choices"][0]["message"]["content"]
        except Exception as e:  # pragma: no cover
            raise ModelUnavailableError(f"Unexpected cloud response format: {e}") from e


@dataclass
class AnthropicMessagesLLM(BaseLLM):
    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    base_url: str = "https://api.anthropic.com/v1"

    @classmethod
    def from_env(cls) -> "AnthropicMessagesLLM":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ModelUnavailableError("No ANTHROPIC_API_KEY configured")
        model = os.environ.get("ANTHROPIC_MODEL", cls.model)
        base_url = os.environ.get("ANTHROPIC_BASE_URL", cls.base_url)
        return cls(api_key=api_key, model=model, base_url=base_url)

    def generate_text(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        url = f"{self.base_url.rstrip('/')}/messages"
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except Exception as e:  # pragma: no cover
            raise ModelUnavailableError(f"Anthropic request failed: {e}") from e

        parsed = json.loads(raw)
        try:
            # anthropic returns content as list of blocks
            blocks = parsed.get("content", [])
            if blocks and isinstance(blocks, list):
                return "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
            return str(parsed)
        except Exception as e:  # pragma: no cover
            raise ModelUnavailableError(f"Unexpected Anthropic response format: {e}") from e
