from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cognisphere_pte.hardware import HardwareProfile, HardwareTier

from .base import LLMGenerationConfig, LLMOutOfMemoryError


_OOM_PATTERNS = [
    re.compile(r"out of memory", re.IGNORECASE),
    re.compile(r"failed to allocate", re.IGNORECASE),
    re.compile(r"std::bad_alloc", re.IGNORECASE),
]


def _looks_like_oom(msg: str) -> bool:
    return any(p.search(msg) for p in _OOM_PATTERNS)


@dataclass
class LlamaCppClient:
    model_path: Path
    hardware: HardwareProfile
    n_ctx: int = 4096

    _llama: Any | None = None

    def _load(self) -> None:
        if self._llama is not None:
            return

        try:
            from llama_cpp import Llama  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "llama-cpp-python is not installed. Install with: pip install .[local-llm]"
            ) from e

        n_threads = int(os.environ.get("COGNISPHERE_PTE_N_THREADS") or max(1, (os.cpu_count() or 4) - 1))

        if os.environ.get("COGNISPHERE_PTE_N_GPU_LAYERS"):
            n_gpu_layers = int(os.environ["COGNISPHERE_PTE_N_GPU_LAYERS"])
        elif self.hardware.tier == HardwareTier.PREMIUM and (self.hardware.has_discrete_gpu or self.hardware.is_apple_silicon):
            n_gpu_layers = 99
        else:
            n_gpu_layers = 0

        try:
            self._llama = Llama(
                model_path=str(self.model_path),
                n_ctx=self.n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                logits_all=False,
                embedding=False,
                verbose=False,
            )
        except Exception as e:
            msg = str(e)
            if _looks_like_oom(msg):
                raise LLMOutOfMemoryError(msg) from e
            raise

    def generate(self, prompt: str, *, config: LLMGenerationConfig | None = None) -> str:
        self._load()
        assert self._llama is not None

        cfg = config or LLMGenerationConfig()

        # Mistral-style instruction wrapper keeps behavior consistent for non-chat llama.cpp usage.
        wrapped = f"<s>[INST] {prompt.strip()} [/INST]"

        try:
            out = self._llama(
                wrapped,
                max_tokens=cfg.max_tokens,
                temperature=cfg.temperature,
                top_p=cfg.top_p,
                stop=["</s>", "[INST]", "[/INST]"],
            )
        except Exception as e:
            msg = str(e)
            if _looks_like_oom(msg):
                raise LLMOutOfMemoryError(msg) from e
            raise

        text = out["choices"][0]["text"]
        return text.strip()
