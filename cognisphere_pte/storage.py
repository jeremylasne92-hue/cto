from __future__ import annotations

import os
from pathlib import Path


def get_data_dir() -> Path:
    override = os.environ.get("COGNISPHERE_PTE_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()

    home = Path.home()
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser().resolve() / "cognisphere_pte"

    return home / ".local" / "share" / "cognisphere_pte"


def get_cache_dir() -> Path:
    override = os.environ.get("COGNISPHERE_PTE_CACHE_DIR")
    if override:
        return Path(override).expanduser().resolve()

    home = Path.home()
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg).expanduser().resolve() / "cognisphere_pte"

    return home / ".cache" / "cognisphere_pte"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
