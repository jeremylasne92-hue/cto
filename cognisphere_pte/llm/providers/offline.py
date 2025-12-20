from __future__ import annotations

import re
from dataclasses import dataclass

from .base import LLMGenerationConfig


def _extract_content(prompt: str) -> str:
    m = re.search(r"\nContent:\n(.+)$", prompt, flags=re.DOTALL)
    return (m.group(1) if m else prompt).strip()


def _top_terms(text: str, *, k: int = 8) -> list[str]:
    words = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", text)]
    stop = {
        "that",
        "this",
        "with",
        "from",
        "they",
        "have",
        "were",
        "which",
        "their",
        "into",
        "also",
        "than",
        "then",
        "when",
        "where",
        "what",
        "your",
        "will",
        "would",
        "should",
        "could",
        "these",
        "those",
        "about",
        "there",
        "because",
    }
    freq: dict[str, int] = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]


@dataclass
class OfflineHeuristicLLMClient:
    """Fallback client that produces valid JSON without external dependencies.

    Intended for dev/test environments where neither local models nor cloud keys are available.
    """

    def generate(self, prompt: str, *, config: LLMGenerationConfig | None = None) -> str:
        p = prompt.lower()
        content = _extract_content(prompt)
        terms = _top_terms(content)
        title = (" ".join(terms[:3]) or "Topic").title()

        if "generate a high-quality quiz" in p:
            # Always produce 5 questions; caller can truncate.
            questions = [
                {
                    "type": "multiple_choice_single",
                    "difficulty": 4,
                    "learning_objective": "Identify a key concept.",
                    "question": f"Which term is most central to the passage?",
                    "options": [terms[0] if terms else "concept", "detail", "example", "aside"],
                    "correct_options": [0],
                    "explanations": {
                        "correct": "It appears most frequently and anchors the discussion.",
                        "distractors": {
                            "1": "Too generic to capture the core idea.",
                            "2": "An instance rather than the overarching concept.",
                            "3": "Not emphasized as central in the passage.",
                        },
                    },
                },
                {
                    "type": "fill_blank",
                    "difficulty": 5,
                    "learning_objective": "Recall and apply a key term in context.",
                    "question": "Complete the key idea.",
                    "fill_blank": {
                        "text_with_blank": f"A key theme discussed is ____.",
                        "answer": terms[0] if terms else "the main concept",
                        "context": content[:220],
                    },
                },
                {
                    "type": "matching",
                    "difficulty": 6,
                    "learning_objective": "Map concepts to short definitions.",
                    "question": "Match each term to a short description.",
                    "matching": {
                        "pairs": [
                            {"left": (terms[0] if len(terms) > 0 else "concept"), "right": "central idea in the text"},
                            {"left": (terms[1] if len(terms) > 1 else "mechanism"), "right": "supporting idea or mechanism"},
                            {"left": (terms[2] if len(terms) > 2 else "example"), "right": "illustrative detail"},
                        ],
                        "distractors_right": ["historical footnote", "unrelated term"],
                    },
                },
                {
                    "type": "ordering",
                    "difficulty": 6,
                    "learning_objective": "Order a reasonable learning progression.",
                    "question": "Order these steps for studying the topic.",
                    "ordering": {
                        "items": [
                            "Identify key terms",
                            "Summarize the main argument",
                            "Connect supporting examples",
                            "Test understanding with questions",
                        ],
                        "correct_order": [0, 1, 2, 3],
                        "rationale": "Start with vocabulary, then the main idea, then evidence, then self-testing.",
                    },
                },
                {
                    "type": "multiple_choice_multi",
                    "difficulty": 7,
                    "learning_objective": "Distinguish core concepts from supporting details.",
                    "question": "Select all items that are emphasized as important in the passage.",
                    "options": (terms[:6] if len(terms) >= 6 else (terms + ["assumption", "constraint", "implication"]))[:6],
                    "correct_options": [0, 1] if len(terms) > 1 else [0],
                    "explanations": {
                        "correct": "The most frequent/relevant terms align with the passage focus.",
                        "distractors": {"2": "Less emphasized.", "3": "Less emphasized.", "4": "Less emphasized.", "5": "Less emphasized."},
                    },
                },
            ]
            return __import__("json").dumps({"quiz_title": title, "questions": questions}, ensure_ascii=False)

        if "create a mind map" in p:
            branches = (terms[:6] if terms else ["overview", "components", "process", "examples", "pitfalls"])
            children = []
            for i, br in enumerate(branches[:5], start=1):
                children.append(
                    {
                        "id": f"b{i}",
                        "label": br.title(),
                        "children": [
                            {"id": f"b{i}_1", "label": f"Definition of {br}"},
                            {"id": f"b{i}_2", "label": f"Why {br} matters"},
                            {"id": f"b{i}_3", "label": f"Example related to {br}"},
                        ],
                    }
                )
            return __import__("json").dumps({"root": {"id": "root", "label": title, "children": children}}, ensure_ascii=False)

        if "multi-level summaries" in p:
            brief = " ".join(content.split()[:50])
            medium = " ".join(content.split()[:200])
            detailed = " ".join(content.split()[:500])
            key_concepts = [{"term": t, "description": "Key term mentioned in the text."} for t in terms[:8]]
            related = [t + " (related)" for t in (terms[:6] if terms else ["background", "applications", "limitations", "examples", "theory"])]
            related_links = [
                {"label": t.title(), "url": f"https://en.wikipedia.org/wiki/{t.replace(' ', '_')}"}
                for t in (terms[:5] if terms else ["Learning", "Education", "Knowledge"])
            ]
            return __import__("json").dumps(
                {
                    "brief": brief,
                    "medium": medium,
                    "detailed": detailed,
                    "key_concepts": key_concepts,
                    "related_topics": related,
                    "related_links": related_links,
                },
                ensure_ascii=False,
            )

        return __import__("json").dumps({"text": content[:800]}, ensure_ascii=False)
