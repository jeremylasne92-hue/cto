from __future__ import annotations

import json
import re
from typing import Any


_JSON_BLOCK_RE = re.compile(r"(\{.*\}|\[.*\])", re.DOTALL)


def extract_json(text: str) -> Any:
    text = text.strip()

    # Fast path
    try:
        return json.loads(text)
    except Exception:
        pass

    m = _JSON_BLOCK_RE.search(text)
    if not m:
        raise ValueError("No JSON object/array found in model output")

    candidate = m.group(1)
    try:
        return json.loads(candidate)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON from model output: {e}")
