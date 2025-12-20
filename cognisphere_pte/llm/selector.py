from __future__ import annotations

import os
from dataclasses import dataclass

from cognisphere_pte.hardware import HardwareProfile, HardwareTier, detect_hardware

from .downloader import download_model_if_needed
from .model_specs import PHI_2_Q4KM, TINYLLAMA_Q4KM, default_local_model_for_tier
from .providers.base import LLMClient, LLMGenerationConfig, LLMOutOfMemoryError
from .providers.cloud import CloudLLMClient
from .providers.llama_cpp import LlamaCppClient
from .providers.offline import OfflineHeuristicLLMClient


@dataclass
class HybridLLM:
    hardware: HardwareProfile | None = None

    _client: LLMClient | None = None

    def _build_local(self, tier: HardwareTier) -> LLMClient:
        spec = default_local_model_for_tier(tier)
        model_path = download_model_if_needed(spec)
        return LlamaCppClient(model_path=model_path, hardware=self.hardware or detect_hardware())

    def _build_cloud_or_offline(self) -> LLMClient:
        has_cloud_key = any(
            [
                bool(os.environ.get("OPENAI_API_KEY")),
                bool(os.environ.get("ANTHROPIC_API_KEY")),
                bool(os.environ.get("GROQ_API_KEY")),
            ]
        )
        return CloudLLMClient() if has_cloud_key else OfflineHeuristicLLMClient()

    def get_client(self) -> LLMClient:
        if self._client is not None:
            return self._client

        hw = self.hardware or detect_hardware()
        self.hardware = hw

        if hw.tier == HardwareTier.MINIMUM:
            self._client = self._build_cloud_or_offline()
            return self._client

        # Preferred local model for this tier
        try:
            self._client = self._build_local(hw.tier)
            return self._client
        except LLMOutOfMemoryError:
            pass
        except Exception:
            # Local inference stack missing; fall back to cloud (or offline if no keys).
            self._client = self._build_cloud_or_offline()
            return self._client

        # If we got OOM: try progressively smaller local model before cloud.
        try:
            model_path = download_model_if_needed(PHI_2_Q4KM)
            self._client = LlamaCppClient(model_path=model_path, hardware=hw)
            return self._client
        except Exception:
            pass

        try:
            model_path = download_model_if_needed(TINYLLAMA_Q4KM)
            self._client = LlamaCppClient(model_path=model_path, hardware=hw)
            return self._client
        except Exception:
            self._client = self._build_cloud_or_offline()
            return self._client

    def generate(self, prompt: str, *, config: LLMGenerationConfig | None = None) -> str:
        return self.get_client().generate(prompt, config=config)
