from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from html import unescape
from pathlib import Path

from .engine import TransformationEngine


def _read_text_from_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "PDF support requires optional dependency 'pypdf'. Install it or provide pre-extracted text."
        ) from e

    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n\n".join(parts)


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    html = re.sub(r"(?s)<.*?>", " ", html)
    html = unescape(html)
    return " ".join(html.split())


def read_input(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        return _strip_html(raw)

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(source)

    if path.suffix.lower() == ".pdf":
        return _read_text_from_pdf(path)

    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pedagogy_engine")
    parser.add_argument("type", choices=["quiz", "mindmap", "summary", "socratic"], help="Artifact type")
    parser.add_argument("source", nargs="?", help="Path to text/PDF file or URL (not required for socratic)")
    parser.add_argument("--topic", help="Topic override for mindmap")
    parser.add_argument("--num-questions", type=int, default=5, help="Number of quiz questions")
    args = parser.parse_args(argv)

    engine = TransformationEngine()

    if args.type == "socratic":
        print(json.dumps(engine.get_socratic_prompts(), indent=2))
        return 0

    if not args.source:
        parser.error("source is required for quiz/mindmap/summary")

    content = read_input(args.source)

    if args.type == "quiz":
        out = engine.generate_quiz(content, num_questions=args.num_questions)
    elif args.type == "mindmap":
        out = engine.generate_mind_map(content, topic=args.topic)
    else:
        out = engine.generate_summaries(content)

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
