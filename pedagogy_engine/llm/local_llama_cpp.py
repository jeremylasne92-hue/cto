from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .base import BaseLLM, ModelUnavailableError, OutOfMemoryError
from .selector import HardwareTier, LocalModelSpec


def _try_import_llama_cpp() -> Any:
    try:
        from llama_cpp import Llama  # type: ignore

        return Llama
    except Exception as e:  # pragma: no cover
        raise ModelUnavailableError(
            "llama-cpp-python is not installed. Install optional dependency 'llama-cpp-python' to use local models."
        ) from e


def _try_hf_download(repo_id: str, filename: str) -> str:
    try:
        from huggingface_hub import hf_hub_download  # type: ignore
    except Exception as e:  # pragma: no cover
        raise ModelUnavailableError(
            "huggingface-hub is not installed; cannot auto-download GGUF models. Provide PEDAGOGY_ENGINE_MODEL_PATH instead."
        ) from e

    try:
        return hf_hub_download(repo_id=repo_id, filename=filename)
    except Exception as e:  # pragma: no cover
        raise ModelUnavailableError(f"Failed to download model '{repo_id}/{filename}': {e}") from e


@dataclass
class LlamaCppLocalLLM(BaseLLM):
    """Local GGUF inference via llama.cpp.

    Model loading is lazy and happens on first call.
    """

    model_path: str
    n_ctx: int = 4096
    n_threads: int | None = None
    n_gpu_layers: int = 0

    _llama: Any | None = None

    @classmethod
    def from_spec(
        cls,
        spec: LocalModelSpec,
        *,
        tier: HardwareTier,
        allow_download: bool = True,
    ) -> "LlamaCppLocalLLM":
        env_path = os.environ.get("PEDAGOGY_ENGINE_MODEL_PATH")
        if env_path:
            return cls(
                model_path=env_path,
                n_ctx=_default_ctx(tier),
                n_gpu_layers=_default_gpu_layers(tier),
            )

        if not allow_download:
            raise ModelUnavailableError(
                "Local model not found and auto-download disabled. Set PEDAGOGY_ENGINE_MODEL_PATH or enable downloads."
            )

        path = _try_hf_download(spec.repo_id, spec.filename)
        return cls(
            model_path=path,
            n_ctx=_default_ctx(tier),
            n_gpu_layers=_default_gpu_layers(tier),
        )

    def _ensure_loaded(self) -> Any:
        if self._llama is not None:
            return self._llama

        Llama = _try_import_llama_cpp()
        try:
            self._llama = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
            )
        except (MemoryError, OSError) as e:  # pragma: no cover
            raise OutOfMemoryError(f"Failed to load local model (OOM or OS error): {e}") from e
        except Exception as e:  # pragma: no cover
            raise ModelUnavailableError(f"Failed to load local model: {e}") from e

        return self._llama

    def generate_text(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        llama = self._ensure_loaded()
        try:
            out = llama(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["</s>"],
            )
        except (MemoryError, OSError) as e:  # pragma: no cover
            raise OutOfMemoryError(f"Local generation failed (OOM or OS error): {e}") from e

        if isinstance(out, dict) and "choices" in out and out["choices"]:
            return out["choices"][0].get("text", "")
        return str(out)


def _default_ctx(tier: HardwareTier) -> int:
    override = os.environ.get("PEDAGOGY_ENGINE_CTX")
    if override and override.isdigit():
        return int(override)

    return 4096 if tier == "premium" else 2048


def _default_gpu_layers(tier: HardwareTier) -> int:
    override = os.environ.get("PEDAGOGY_ENGINE_GPU_LAYERS")
    if override and override.isdigit():
        return int(override)

    # Conservative default to reduce OOM risk; tune via env var.
    if tier == "premium":
        return 20

    return 0
