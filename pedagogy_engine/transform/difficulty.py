from __future__ import annotations

import math
import re

_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_'-]*")


def estimate_difficulty_1_to_10(text: str) -> int:
    """Heuristic difficulty estimate based on vocabulary density and length.

    The goal is a stable, dependency-free rating usable as a baseline or as a
    validation signal for model-generated values.
    """

    words = [m.group(0) for m in _WORD_RE.finditer(text)]
    if not words:
        return 1

    n = len(words)
    unique_ratio = len({w.lower() for w in words}) / max(1, n)
    avg_len = sum(len(w) for w in words) / n

    long_words = sum(1 for w in words if len(w) >= 10) / n
    numeric = sum(1 for w in words if any(ch.isdigit() for ch in w)) / n

    score = 0.0
    score += 4.0 * unique_ratio
    score += 0.35 * avg_len
    score += 3.0 * long_words
    score += 1.5 * numeric

    score += 0.5 * math.log(max(1.0, n / 50.0), 2)

    rating = int(round(score))
    return max(1, min(10, rating))
