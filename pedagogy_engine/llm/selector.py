from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from typing import Literal


HardwareTier = Literal["premium", "standard", "minimum"]


def _ram_gb() -> float:
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return (pages * page_size) / (1024**3)
    except Exception:
        return 0.0


def _has_nvidia_gpu() -> bool:
    if os.path.exists("/dev/nvidia0"):
        return True

    cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if cuda_visible and cuda_visible.strip() not in {"", "-1"}:
        return True

    nvidia_visible = os.environ.get("NVIDIA_VISIBLE_DEVICES")
    if nvidia_visible and nvidia_visible.strip() not in {"", "void", "none"}:
        return True

    return False


def _is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}


def detect_hardware_tier() -> HardwareTier:
    override = os.environ.get("PEDAGOGY_ENGINE_TIER")
    if override:
        override = override.lower().strip()
        if override in {"premium", "standard", "minimum"}:
            return override  # type: ignore[return-value]

    if _has_nvidia_gpu() or _is_apple_silicon():
        return "premium"

    ram = _ram_gb()
    if ram >= 16:
        return "standard"

    return "minimum"


@dataclass(frozen=True)
class LocalModelSpec:
    repo_id: str
    filename: str
    friendly_name: str


def default_local_model_for_tier(tier: HardwareTier) -> LocalModelSpec | None:
    if tier == "premium":
        return LocalModelSpec(
            repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
            filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            friendly_name="Mistral-7B-Instruct-v0.2 (Q4_K_M)",
        )

    if tier == "standard":
        return LocalModelSpec(
            repo_id="TheBloke/phi-2-GGUF",
            filename="phi-2.Q4_K_M.gguf",
            friendly_name="Phi-2 (Q4_K_M)",
        )

    return None
