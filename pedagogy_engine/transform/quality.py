from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str


def validate_quiz(quiz: dict[str, Any]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    questions = quiz.get("questions")
    if not isinstance(questions, list) or len(questions) < 5:
        issues.append(QualityIssue("quiz.too_few_questions", "Quiz must contain at least 5 questions"))
        return issues

    types = [q.get("type") for q in questions if isinstance(q, dict)]
    if len(set(types)) < 3:
        issues.append(QualityIssue("quiz.not_varied", "Quiz should include varied question types"))

    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            issues.append(QualityIssue("quiz.bad_question", f"Question {i} is not an object"))
            continue

        qtype = q.get("type")
        if qtype == "multiple_choice_single":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) != 4:
                issues.append(QualityIssue("quiz.mc_single.options", f"Question {i} must have exactly 4 options"))
            correct = [o for o in opts or [] if isinstance(o, dict) and o.get("is_correct") is True]
            if len(correct) != 1:
                issues.append(QualityIssue("quiz.mc_single.correct", f"Question {i} must have exactly 1 correct option"))
            for o in opts or []:
                if isinstance(o, dict) and not o.get("is_correct"):
                    exp = o.get("explanation")
                    if not isinstance(exp, str) or len(exp.strip()) < 10:
                        issues.append(
                            QualityIssue("quiz.mc_single.distractor_explanation", f"Question {i} distractors need explanations")
                        )

        if qtype == "multiple_choice_multi":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) < 5:
                issues.append(QualityIssue("quiz.mc_multi.options", f"Question {i} must have 5+ options"))
            correct = [o for o in opts or [] if isinstance(o, dict) and o.get("is_correct") is True]
            if len(correct) < 2:
                issues.append(QualityIssue("quiz.mc_multi.correct", f"Question {i} must have at least 2 correct options"))

        if qtype == "fill_blank":
            if not isinstance(q.get("text_with_blank"), str) or "____" not in q.get("text_with_blank", ""):
                issues.append(QualityIssue("quiz.fill_blank.format", f"Question {i} must include text_with_blank containing ____"))
            if not isinstance(q.get("answer"), str) or not q.get("answer"):
                issues.append(QualityIssue("quiz.fill_blank.answer", f"Question {i} must include answer"))

        if qtype == "matching":
            pairs = q.get("pairs")
            if not isinstance(pairs, list) or len(pairs) < 3:
                issues.append(QualityIssue("quiz.matching.pairs", f"Question {i} must include at least 3 pairs"))

        if qtype == "ordering":
            items = q.get("items")
            if not isinstance(items, list) or len(items) < 3:
                issues.append(QualityIssue("quiz.ordering.items", f"Question {i} must include at least 3 items"))
            if not isinstance(q.get("correct_order"), list) or len(q.get("correct_order")) != len(items or []):
                issues.append(QualityIssue("quiz.ordering.correct_order", f"Question {i} must include correct_order indices"))

    return issues


def validate_mindmap(mindmap: dict[str, Any]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    root = mindmap.get("root")
    if not isinstance(root, dict):
        issues.append(QualityIssue("mindmap.root", "Mind map must include root node"))
        return issues

    children = root.get("children")
    if not isinstance(children, list) or not (3 <= len(children) <= 7):
        issues.append(QualityIssue("mindmap.branches", "Root should have 3-7 major branches"))

    def _validate_node(node: dict[str, Any], depth: int) -> None:
        name = node.get("name")
        if not isinstance(name, str) or not name.strip():
            issues.append(QualityIssue("mindmap.node.name", f"Node missing name at depth {depth}"))
        kids = node.get("children")
        if kids is not None and not isinstance(kids, list):
            issues.append(QualityIssue("mindmap.node.children", f"children must be list at depth {depth}"))

    _validate_node(root, 0)
    for c in children or []:
        if isinstance(c, dict):
            _validate_node(c, 1)
            for sc in c.get("children") or []:
                if isinstance(sc, dict):
                    _validate_node(sc, 2)

    return issues
