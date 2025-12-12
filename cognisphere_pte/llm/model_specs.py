from __future__ import annotations

from dataclasses import dataclass

from cognisphere_pte.hardware import HardwareTier


@dataclass(frozen=True)
class LocalModelSpec:
    provider: str
    model_id: str
    hf_repo: str
    hf_filename: str
    approx_size_gb: float
    recommended_ram_gb: float


MISTRAL_7B_INSTRUCT_Q4KM = LocalModelSpec(
    provider="llama.cpp",
    model_id="mistral-7b-instruct-v0.2-q4_k_m",
    hf_repo="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
    hf_filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    approx_size_gb=4.1,
    recommended_ram_gb=16.0,
)

PHI_2_Q4KM = LocalModelSpec(
    provider="llama.cpp",
    model_id="phi-2-q4_k_m",
    hf_repo="TheBloke/phi-2-GGUF",
    hf_filename="phi-2.Q4_K_M.gguf",
    approx_size_gb=1.6,
    recommended_ram_gb=8.0,
)

TINYLLAMA_Q4KM = LocalModelSpec(
    provider="llama.cpp",
    model_id="tinyllama-1.1b-chat-q4_k_m",
    hf_repo="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
    hf_filename="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    approx_size_gb=1.0,
    recommended_ram_gb=6.0,
)


def default_local_model_for_tier(tier: HardwareTier) -> LocalModelSpec:
    if tier == HardwareTier.PREMIUM:
        return MISTRAL_7B_INSTRUCT_Q4KM
    if tier == HardwareTier.STANDARD:
        return PHI_2_Q4KM
    return TINYLLAMA_Q4KM
