from __future__ import annotations

import json
import random
import re
import uuid
from dataclasses import dataclass
from typing import Any

from ..llm.base import LLM
from ..llm.offline import OfflineLLM
from .difficulty import estimate_difficulty_1_to_10
from .quality import validate_quiz


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_'-]*")

_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "if",
    "then",
    "else",
    "when",
    "while",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "as",
    "by",
    "at",
    "from",
    "into",
    "about",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "it",
    "this",
    "that",
    "these",
    "those",
    "we",
    "you",
    "they",
    "i",
    "he",
    "she",
    "them",
    "his",
    "her",
    "their",
    "our",
    "your",
    "not",
    "can",
    "may",
    "might",
    "will",
    "would",
    "should",
    "could",
}


def _sentences(text: str) -> list[str]:
    parts = [p.strip() for p in _SENTENCE_SPLIT_RE.split(text) if p.strip()]
    return [p for p in parts if len(p.split()) >= 6]


def _keywords(text: str, *, top_n: int = 24) -> list[str]:
    tokens = [m.group(0).lower() for m in _WORD_RE.finditer(text)]
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) >= 4]
    if not tokens:
        return []

    freq: dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1

    ranked = sorted(freq.items(), key=lambda kv: (kv[1], len(kv[0])), reverse=True)
    return [w for w, _ in ranked[:top_n]]


def _definition_candidates(text: str) -> list[tuple[str, str]]:
    # Returns (term, definition) pairs extracted from simple patterns.
    pairs: list[tuple[str, str]] = []
    for s in _sentences(text):
        lower = s.lower()
        for pat in [" is ", " are ", " refers to ", " means "]:
            if pat in lower:
                left, right = s.split(pat, 1)
                term = left.strip(" .,:;()[]{}\"'\n\t")
                definition = right.strip(" .,:;()[]{}\"'\n\t")
                if 1 <= len(term.split()) <= 6 and len(definition.split()) >= 5:
                    pairs.append((term, definition))
                break

    # Deduplicate terms
    seen = set()
    out: list[tuple[str, str]] = []
    for term, definition in pairs:
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append((term, definition))
    return out


def _stable_shuffle(items: list[Any], seed: str) -> list[Any]:
    rnd = random.Random(seed)
    items = list(items)
    rnd.shuffle(items)
    return items


@dataclass
class QuizGenerator:
    llm: LLM

    def generate(
        self,
        content: str,
        *,
        num_questions: int = 5,
        difficulty_target: int | None = None,
    ) -> dict[str, Any]:
        # Prefer LLM-backed generation if we have a real provider.
        if not isinstance(self.llm, OfflineLLM):
            try:
                quiz = self._generate_with_llm(content, num_questions=num_questions, difficulty_target=difficulty_target)
                if not validate_quiz(quiz):
                    return quiz
            except Exception:
                pass

        return self._generate_heuristic(content, num_questions=num_questions, difficulty_target=difficulty_target)

    def _generate_with_llm(
        self,
        content: str,
        *,
        num_questions: int,
        difficulty_target: int | None,
    ) -> dict[str, Any]:
        prompt = (
            "Generate a quiz from the content. Output ONLY valid JSON.\n\n"
            "Requirements:\n"
            f"- Generate {max(5, num_questions)} questions.\n"
            "- Use varied types: multiple_choice_single, multiple_choice_multi, fill_blank, matching, ordering.\n"
            "- multiple_choice_single: exactly 4 options; exactly 1 correct; explain why each distractor is wrong.\n"
            "- multiple_choice_multi: 5+ options; 2+ correct; explain why each incorrect option is wrong.\n"
            "- fill_blank: include text_with_blank containing '____', include answer and context.\n"
            "- matching: include 3-6 pairs of {left,right}.\n"
            "- ordering: include items list (3-6) and correct_order list of indices.\n"
            "- difficulty: integer 1-10 per question.\n"
            "- Avoid 'All of the above'/'None of the above'.\n"
            "- Pedagogical value: ask about concepts, not trivia.\n\n"
            "JSON schema:\n"
            "{\n"
            "  'version': '1',\n"
            "  'questions': [\n"
            "    {\n"
            "      'id': '...',\n"
            "      'type': 'multiple_choice_single' | 'multiple_choice_multi' | 'fill_blank' | 'matching' | 'ordering',\n"
            "      'prompt': '...',\n"
            "      'difficulty': 1-10,\n"
            "      ... type-specific fields ...\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Content:\n"
            + content[:12000]
        )

        quiz = self.llm.generate_json(prompt, temperature=0.2, max_tokens=1800)
        if not isinstance(quiz, dict):
            raise ValueError("LLM did not return a JSON object")

        quiz.setdefault("version", "1")
        for q in quiz.get("questions", []) if isinstance(quiz.get("questions"), list) else []:
            if isinstance(q, dict):
                q.setdefault("id", str(uuid.uuid4()))

        return quiz

    def _generate_heuristic(
        self,
        content: str,
        *,
        num_questions: int,
        difficulty_target: int | None,
    ) -> dict[str, Any]:
        seed = str(hash(content))
        defs = _definition_candidates(content)
        sents = _sentences(content)
        kw = _keywords(content)

        questions: list[dict[str, Any]] = []

        # Fill-in-the-blank
        if sents:
            s = _stable_shuffle(sents, seed + "fb")[0]
            target_word = None
            for w in _keywords(s, top_n=10):
                if w in kw:
                    target_word = w
                    break
            if target_word is None:
                # pick a longer word
                words = [m.group(0) for m in _WORD_RE.finditer(s) if len(m.group(0)) >= 7]
                if words:
                    target_word = _stable_shuffle(words, seed + "fbw")[0]

            if target_word:
                blanked = re.sub(rf"\b{re.escape(target_word)}\b", "____", s, count=1, flags=re.IGNORECASE)
                questions.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "fill_blank",
                        "prompt": "Fill in the blank with the most appropriate term from the passage.",
                        "text_with_blank": blanked,
                        "answer": target_word,
                        "context": s,
                        "difficulty": difficulty_target or estimate_difficulty_1_to_10(s),
                    }
                )

        # Matching
        if len(defs) >= 3:
            pairs = [{"left": t, "right": d} for t, d in _stable_shuffle(defs, seed + "m")[:4]]
            questions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "matching",
                    "prompt": "Match each concept to the best definition.",
                    "pairs": pairs,
                    "difficulty": difficulty_target or estimate_difficulty_1_to_10(" ".join(t for t, _ in defs)),
                }
            )

        # Ordering
        steps: list[str] = []
        for line in content.splitlines():
            line = line.strip()
            if re.match(r"^\d+[.)]\s+", line):
                steps.append(re.sub(r"^\d+[.)]\s+", "", line))
        if len(steps) < 3:
            for s in sents:
                if any(tok in s.lower() for tok in ["first", "second", "third", "then", "next", "finally"]):
                    steps.append(s)

        steps = [st.strip() for st in steps if len(st.split()) >= 4]
        if len(steps) >= 3:
            chosen = _stable_shuffle(steps, seed + "o")[: min(5, len(steps))]
            scrambled = _stable_shuffle(chosen, seed + "os")
            correct_order = [scrambled.index(x) for x in chosen]
            questions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "ordering",
                    "prompt": "Put the following steps in the correct order.",
                    "items": scrambled,
                    "correct_order": correct_order,
                    "rationale": "The correct sequence follows the logical/chronological flow described in the passage.",
                    "difficulty": difficulty_target or estimate_difficulty_1_to_10(" ".join(chosen)),
                }
            )

        # Multiple choice (single)
        if defs:
            term, definition = _stable_shuffle(defs, seed + "mc")[0]
            distractor_defs = [d for t, d in defs if t.lower() != term.lower()]
            distractor_defs = _stable_shuffle(distractor_defs, seed + "mcd")

            options = [
                {
                    "id": "A",
                    "text": definition,
                    "is_correct": True,
                    "explanation": f"This matches the passage's description of {term}.",
                }
            ]
            for idx, d in enumerate(distractor_defs[:3], start=1):
                label = chr(ord("A") + idx)
                options.append(
                    {
                        "id": label,
                        "text": d,
                        "is_correct": False,
                        "explanation": "This definition describes a different concept than the one asked about.",
                    }
                )

            if len(options) < 4 and sents:
                filler = _stable_shuffle(sents, seed + "mcf")
                for idx in range(len(options), 4):
                    label = chr(ord("A") + idx)
                    options.append(
                        {
                            "id": label,
                            "text": filler[idx % len(filler)],
                            "is_correct": False,
                            "explanation": "This statement is not the definition of the requested term.",
                        }
                    )

            questions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "multiple_choice_single",
                    "prompt": f"According to the passage, which option best defines '{term}'?",
                    "options": options[:4],
                    "difficulty": difficulty_target or estimate_difficulty_1_to_10(definition),
                }
            )

        # Multiple choice (multi)
        truths: list[str] = []
        for s in sents[:10]:
            if len(s.split()) <= 20:
                truths.append(s)
        truths = _stable_shuffle(truths, seed + "t")[:3]

        falsehoods: list[str] = []
        for t in truths:
            if " not " in t.lower():
                falsehoods.append(t.replace(" not ", " "))
            else:
                falsehoods.append("Not " + t[0].lower() + t[1:])
        falsehoods = [f for f in falsehoods if f and f.lower() not in {tr.lower() for tr in truths}]

        options_multi: list[dict[str, Any]] = []
        for s in truths:
            options_multi.append(
                {
                    "id": str(uuid.uuid4()),
                    "text": s,
                    "is_correct": True,
                    "explanation": "This statement is supported by the passage.",
                }
            )
        for s in _stable_shuffle(falsehoods, seed + "f")[:3]:
            options_multi.append(
                {
                    "id": str(uuid.uuid4()),
                    "text": s,
                    "is_correct": False,
                    "explanation": "This is not supported (or contradicts) what the passage states.",
                }
            )

        options_multi = _stable_shuffle(options_multi, seed + "ms")
        if len(options_multi) >= 5:
            questions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "multiple_choice_multi",
                    "prompt": "Select ALL statements that are supported by the passage.",
                    "options": options_multi,
                    "difficulty": difficulty_target or estimate_difficulty_1_to_10(" ".join(truths)),
                }
            )

        # Ensure minimum count and variety
        present_types = {q.get("type") for q in questions if isinstance(q, dict)}

        if "multiple_choice_single" not in present_types and sents and kw:
            focus = kw[0].title()
            related = [s for s in sents if kw[0] in s.lower()]
            correct = related[0] if related else sents[0]
            distractors = _stable_shuffle([s for s in sents if s != correct], seed + "mcs")[:3]
            options = [
                {
                    "id": "A",
                    "text": correct,
                    "is_correct": True,
                    "explanation": f"This statement about {focus} is directly supported by the passage.",
                }
            ]
            for idx, d in enumerate(distractors, start=1):
                options.append(
                    {
                        "id": chr(ord("A") + idx),
                        "text": d,
                        "is_correct": False,
                        "explanation": f"This does not answer what the passage states about {focus}.",
                    }
                )
            if len(options) == 4:
                questions.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice_single",
                        "prompt": f"Which statement is most supported by the passage about '{focus}'?",
                        "options": options,
                        "difficulty": difficulty_target or estimate_difficulty_1_to_10(correct),
                    }
                )

        if "matching" not in present_types and len(kw) >= 3 and sents:
            pairs: list[dict[str, str]] = []
            for term in kw[:4]:
                rel = next((s for s in sents if term in s.lower()), None)
                if rel is None:
                    continue
                definition = " ".join(rel.split()[:18]).strip(" .,:;()[]{}\"'")
                pairs.append({"left": term.title(), "right": definition})
            if len(pairs) >= 3:
                questions.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "matching",
                        "prompt": "Match each term to the snippet that best reflects its role in the passage.",
                        "pairs": pairs,
                        "difficulty": difficulty_target or estimate_difficulty_1_to_10(" ".join(p["right"] for p in pairs)),
                    }
                )

        if "ordering" not in present_types and len(sents) >= 3:
            chosen = _stable_shuffle(sents, seed + "oo")[: min(4, len(sents))]
            if len(chosen) >= 3:
                scrambled = _stable_shuffle(chosen, seed + "oos")
                correct_order = [scrambled.index(x) for x in chosen]
                questions.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "ordering",
                        "prompt": "Arrange the following points in the order they appear in the passage.",
                        "items": scrambled,
                        "correct_order": correct_order,
                        "rationale": "Ordering is based on the passage's presentation sequence.",
                        "difficulty": difficulty_target or estimate_difficulty_1_to_10(" ".join(chosen)),
                    }
                )

        if len(questions) < max(5, num_questions) and sents:
            # Add extra fill blanks from other sentences
            for s in _stable_shuffle(sents, seed + "x"):
                if len(questions) >= max(5, num_questions):
                    break
                words = [w for w in _keywords(s, top_n=8) if len(w) >= 4]
                if not words:
                    continue
                w = words[0]
                blanked = re.sub(rf"\b{re.escape(w)}\b", "____", s, count=1, flags=re.IGNORECASE)
                questions.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "fill_blank",
                        "prompt": "Fill in the blank.",
                        "text_with_blank": blanked,
                        "answer": w,
                        "context": s,
                        "difficulty": difficulty_target or estimate_difficulty_1_to_10(s),
                    }
                )

        quiz = {
            "version": "1",
            "generator": "heuristic",
            "questions": questions[: max(5, num_questions)],
        }

        issues = validate_quiz(quiz)
        if issues:
            # Best-effort repair: strip any invalid questions
            repaired = []
            for q in quiz["questions"]:
                if isinstance(q, dict) and q.get("type") in {
                    "multiple_choice_single",
                    "multiple_choice_multi",
                    "fill_blank",
                    "matching",
                    "ordering",
                }:
                    repaired.append(q)
            quiz["questions"] = repaired

        return json.loads(json.dumps(quiz))
