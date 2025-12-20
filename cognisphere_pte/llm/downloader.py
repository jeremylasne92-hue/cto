from __future__ import annotations

import os
import urllib.request
from pathlib import Path

from cognisphere_pte.storage import ensure_dir, get_data_dir

from .model_specs import LocalModelSpec


def get_models_dir() -> Path:
    return ensure_dir(get_data_dir() / "models")


def _hf_resolve_url(repo: str, filename: str, revision: str = "main") -> str:
    return f"https://huggingface.co/{repo}/resolve/{revision}/{filename}"


def download_model_if_needed(spec: LocalModelSpec) -> Path:
    override = os.environ.get("COGNISPHERE_PTE_MODEL_PATH")
    if override:
        p = Path(override).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"COGNISPHERE_PTE_MODEL_PATH points to missing file: {p}")
        return p

    models_dir = get_models_dir()
    target = models_dir / spec.hf_filename
    if target.exists() and target.stat().st_size > 0:
        return target

    tmp = target.with_suffix(target.suffix + ".partial")
    url = _hf_resolve_url(spec.hf_repo, spec.hf_filename, revision=os.environ.get("COGNISPHERE_PTE_HF_REVISION", "main"))

    headers = {}
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    ensure_dir(models_dir)

    with urllib.request.urlopen(req) as resp, open(tmp, "wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    tmp.replace(target)
    return target
