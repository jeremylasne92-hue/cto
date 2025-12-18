from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass


_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_'-]*")


def _tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]


@dataclass(frozen=True)
class HashingEmbedder:
    """Fast, dependency-free pseudo-embedding.

    This is not a semantic embedding model, but it is sufficient for detecting
    near-duplicates and highly similar imports without external dependencies.
    """

    dims: int = 256

    def embed(self, text: str) -> list[float]:
        tokens = _tokenize(text)
        if not tokens:
            return [0.0] * self.dims

        counts = Counter(tokens)
        vec = [0.0] * self.dims
        for tok, c in counts.items():
            digest = hashlib.blake2b(tok.encode("utf-8"), digest_size=4).digest()
            idx = int.from_bytes(digest, "little") % self.dims
            vec[idx] += float(c)

        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0.0:
            return vec
        return [v / norm for v in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    return sum(x * y for x, y in zip(a, b))
