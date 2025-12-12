from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

from cognisphere_pte.engine import TransformationEngine


def _read_text_file(path: Path) -> str:
    return path.read_text("utf-8")


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("PDF support requires: pip install .[pdf]") from e

    reader = PdfReader(str(path))
    texts: list[str] = []
    for page in reader.pages:
        t = page.extract_text() or ""
        if t.strip():
            texts.append(t)
    return "\n\n".join(texts)


def _fetch_url_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    # Minimal tag strip (good enough for prompt context).
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _load_input(args: argparse.Namespace) -> str:
    if args.text_file:
        return _read_text_file(Path(args.text_file))
    if args.pdf_file:
        return _read_pdf(Path(args.pdf_file))
    if args.url:
        return _fetch_url_text(args.url)
    if args.text:
        return args.text

    raise SystemExit("Provide one of: --text-file, --pdf-file, --url, or --text")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cognisphere-pte")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_quiz = sub.add_parser("quiz", help="Generate a quiz from text/PDF/URL")
    p_quiz.add_argument("--text-file")
    p_quiz.add_argument("--pdf-file")
    p_quiz.add_argument("--url")
    p_quiz.add_argument("--text")
    p_quiz.add_argument("--num-questions", type=int, default=5)

    p_mind = sub.add_parser("mindmap", help="Generate a mind map from text/PDF/URL")
    p_mind.add_argument("--text-file")
    p_mind.add_argument("--pdf-file")
    p_mind.add_argument("--url")
    p_mind.add_argument("--text")

    p_sum = sub.add_parser("summary", help="Generate multi-level summaries")
    p_sum.add_argument("--text-file")
    p_sum.add_argument("--pdf-file")
    p_sum.add_argument("--url")
    p_sum.add_argument("--text")

    args = parser.parse_args(argv)
    engine = TransformationEngine()

    if args.cmd == "quiz":
        text = _load_input(args)
        quiz = engine.generate_quiz([text], num_questions=args.num_questions)
        print(json.dumps(quiz.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "mindmap":
        text = _load_input(args)
        mm = engine.generate_mindmap(text)
        print(json.dumps(mm.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "summary":
        text = _load_input(args)
        summ = engine.generate_summary(text)
        print(json.dumps(summ.to_dict(), ensure_ascii=False, indent=2))
        return 0

    raise SystemExit(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
