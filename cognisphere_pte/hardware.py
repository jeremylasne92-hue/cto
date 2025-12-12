from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum


class HardwareTier(str, Enum):
    PREMIUM = "premium"
    STANDARD = "standard"
    MINIMUM = "minimum"


@dataclass(frozen=True)
class HardwareProfile:
    tier: HardwareTier
    total_ram_gb: float
    has_discrete_gpu: bool
    is_apple_silicon: bool


def _get_total_ram_gb() -> float:
    try:
        if hasattr(os, "sysconf"):
            page_size = os.sysconf("SC_PAGE_SIZE")
            pages = os.sysconf("SC_PHYS_PAGES")
            return (page_size * pages) / (1024**3)
    except Exception:
        pass

    # Fallback: unknown
    return 0.0


def _has_nvidia_gpu() -> bool:
    if os.environ.get("COGNISPHERE_PTE_HAS_GPU") in {"1", "true", "TRUE"}:
        return True

    if shutil.which("nvidia-smi") is None:
        return False

    try:
        subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=1.5,
        )
        return True
    except Exception:
        return False


def _is_apple_silicon() -> bool:
    if platform.system().lower() != "darwin":
        return False
    try:
        return platform.machine().lower() in {"arm64", "aarch64"}
    except Exception:
        return False


def detect_hardware() -> HardwareProfile:
    forced = os.environ.get("COGNISPHERE_PTE_HARDWARE_TIER")
    ram_gb = _get_total_ram_gb()
    has_gpu = _has_nvidia_gpu()
    apple = _is_apple_silicon()

    if forced:
        tier = HardwareTier(forced.lower())
        return HardwareProfile(tier=tier, total_ram_gb=ram_gb, has_discrete_gpu=has_gpu, is_apple_silicon=apple)

    # Very conservative heuristics.
    if has_gpu or apple or ram_gb >= 24:
        tier = HardwareTier.PREMIUM
    elif ram_gb >= 14:
        tier = HardwareTier.STANDARD
    else:
        tier = HardwareTier.MINIMUM

    return HardwareProfile(tier=tier, total_ram_gb=ram_gb, has_discrete_gpu=has_gpu, is_apple_silicon=apple)
