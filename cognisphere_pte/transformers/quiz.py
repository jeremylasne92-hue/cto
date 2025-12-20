from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from cognisphere_pte.cache import TransformationCache
from cognisphere_pte.llm.providers.base import LLMGenerationConfig
from cognisphere_pte.llm.selector import HybridLLM
from cognisphere_pte.prompts import build_quiz_prompt
from cognisphere_pte.utils.json import extract_json


_ALLOWED_TYPES = {
    "multiple_choice_single",
    "multiple_choice_multi",
    "fill_blank",
    "matching",
    "ordering",
}


def _coerce_int_1_10(v: Any) -> int:
    try:
        n = int(v)
    except Exception:
        return 5
    return max(1, min(10, n))


def _estimate_difficulty_from_text(text: str) -> int:
    words = re.findall(r"[A-Za-z]+", text)
    if not words:
        return 3
    avg_len = sum(len(w) for w in words) / len(words)
    unique_ratio = len(set(w.lower() for w in words)) / len(words)
    score = 2 + (avg_len - 4.0) * 1.3 + unique_ratio * 4.5
    return _coerce_int_1_10(round(score))


@dataclass
class Quiz:
    quiz_title: str
    questions: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {"quiz_title": self.quiz_title, "questions": self.questions}


class QuizGenerator:
    def __init__(self, *, llm: HybridLLM | None = None, cache: TransformationCache | None = None):
        self.llm = llm or HybridLLM()
        self.cache = cache or TransformationCache()

    def generate(self, chunks: list[str], *, num_questions: int = 5) -> Quiz:
        content = "\n\n".join(chunks)
        params = {"num_questions": num_questions}

        hit = self.cache.get(content=content, transform_type="quiz", params=params)
        if hit:
            payload = hit.payload
            return Quiz(quiz_title=payload.get("quiz_title", "Quiz"), questions=payload.get("questions", []))

        prompt = build_quiz_prompt(chunks, num_questions=num_questions)
        raw = self.llm.generate(
            prompt,
            config=LLMGenerationConfig(temperature=0.35, max_tokens=1700, top_p=0.95),
        )
        payload = extract_json(raw)

        payload = self._normalize_and_check(payload, expected=num_questions)

        self.cache.set(content=content, transform_type="quiz", params=params, payload=payload)
        return Quiz(quiz_title=payload["quiz_title"], questions=payload["questions"])

    def _normalize_and_check(self, payload: Any, *, expected: int) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Quiz payload must be an object")
        questions = payload.get("questions")
        if not isinstance(questions, list):
            raise ValueError("Quiz payload missing 'questions' array")

        out_questions: list[dict[str, Any]] = []
        seen_types: set[str] = set()

        for q in questions[:expected]:
            if not isinstance(q, dict):
                continue
            q_type = str(q.get("type", "")).strip()
            if q_type not in _ALLOWED_TYPES:
                continue

            question_text = str(q.get("question") or q.get("fill_blank", {}).get("text_with_blank") or "").strip()
            if not question_text:
                continue

            q["difficulty"] = _coerce_int_1_10(q.get("difficulty") or _estimate_difficulty_from_text(question_text))

            if q_type.startswith("multiple_choice"):
                options = q.get("options")
                correct = q.get("correct_options")
                if not isinstance(options, list) or len(options) < (4 if q_type == "multiple_choice_single" else 5):
                    continue
                if any(isinstance(o, str) and o.strip().lower() in {"all of the above", "none of the above"} for o in options):
                    continue
                if not isinstance(correct, list) or not correct:
                    continue
                if q_type == "multiple_choice_single" and len(correct) != 1:
                    continue

                exp = q.get("explanations")
                if not isinstance(exp, dict) or not isinstance(exp.get("distractors"), dict) or not exp.get("correct"):
                    continue

            out_questions.append(q)
            seen_types.add(q_type)

        if len(out_questions) < expected:
            raise ValueError(f"Quiz quality check failed: expected {expected} usable questions, got {len(out_questions)}")

        # Encourage variety: at least 3 types, ideally 4+.
        if len(seen_types) < 3:
            raise ValueError("Quiz quality check failed: insufficient question type variety")

        title = str(payload.get("quiz_title") or "Quiz").strip() or "Quiz"
        return {"quiz_title": title, "questions": out_questions[:expected]}
