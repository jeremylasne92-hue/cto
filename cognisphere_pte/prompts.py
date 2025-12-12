from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Literal


def truncate_to_word_budget(text: str, *, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


QuizDifficulty = Literal["easy", "medium", "hard"]


@dataclass(frozen=True)
class PromptBudgets:
    # Roughly keeps local models under typical 4k context.
    quiz_context_words: int = 2200
    mindmap_context_words: int = 2600
    summary_context_words: int = 3000


FEWSHOT_QUIZ_EXAMPLE = {
    "quiz_title": "Photosynthesis (micro-example)",
    "questions": [
        {
            "type": "multiple_choice_single",
            "difficulty": 4,
            "question": "Which molecule is the primary pigment that absorbs light in plants?",
            "options": ["Chlorophyll", "Hemoglobin", "Keratin", "Cellulose"],
            "correct_options": [0],
            "explanations": {
                "correct": "Chlorophyll absorbs light energy to drive the light-dependent reactions.",
                "distractors": {
                    "1": "Hemoglobin transports oxygen in animals, not light absorption in plants.",
                    "2": "Keratin is a structural protein in animals.",
                    "3": "Cellulose forms plant cell walls; it does not absorb light for photosynthesis.",
                },
            },
        }
    ],
}


def build_quiz_prompt(chunks: list[str], *, num_questions: int, budgets: PromptBudgets | None = None) -> str:
    b = budgets or PromptBudgets()
    joined = "\n\n".join(chunks)
    joined = truncate_to_word_budget(joined, max_words=b.quiz_context_words)

    schema = {
        "quiz_title": "string",
        "questions": [
            {
                "type": "multiple_choice_single | multiple_choice_multi | fill_blank | matching | ordering",
                "difficulty": "integer 1-10",
                "learning_objective": "string",
                "question": "string",
                "options": "array of strings (for MC types)",
                "correct_options": "array of indices (for MC types)",
                "explanations": {
                    "correct": "string",
                    "distractors": "object mapping option_index->explanation (for MC)"
                },
                "fill_blank": {
                    "text_with_blank": "string",
                    "answer": "string",
                    "context": "string"
                },
                "matching": {
                    "pairs": [{"left": "string", "right": "string"}],
                    "distractors_right": ["string"]
                },
                "ordering": {
                    "items": ["string"],
                    "correct_order": "array of indices",
                    "rationale": "string"
                },
            }
        ],
    }

    return textwrap.dedent(
        f"""
        You are a pedagogical content transformation engine.

        TASK: Generate a high-quality quiz in JSON from the provided content.

        Requirements:
        - Create exactly {num_questions} questions.
        - Use varied types across the quiz: include at least 4 of these 5 types:
          (1) multiple_choice_single (4 options, 1 correct)
          (2) multiple_choice_multi (>=5 options, 2+ correct)
          (3) fill_blank
          (4) matching
          (5) ordering
        - For multiple choice questions:
          - avoid trivial cues (no obviously longer/shorter correct option)
          - avoid "all of the above" / "none of the above"
          - explain why each distractor is plausible but wrong
        - Each question must include a difficulty rating 1-10.
          - base it on vocabulary + concept complexity + inference needed
        - Ensure pedagogical value: each question should probe understanding, not memorization.

        IMPORTANT:
        - Think step-by-step internally to craft strong questions, but DO NOT output reasoning.
        - Output ONLY valid JSON (no markdown, no commentary).

        JSON schema (informal):
        {schema}

        Few-shot example (structure reference):
        {FEWSHOT_QUIZ_EXAMPLE}

        Content:
        {joined}
        """
    ).strip()


def build_mindmap_prompt(text: str, *, budgets: PromptBudgets | None = None) -> str:
    b = budgets or PromptBudgets()
    text = truncate_to_word_budget(text, max_words=b.mindmap_context_words)

    return textwrap.dedent(
        f"""
        You are a pedagogical content transformation engine.

        TASK: Create a mind map as a hierarchical JSON tree suitable for D3.js.

        Constraints:
        - Root: exactly 1 main theme.
        - Branches: 3-7 major categories.
        - Sub-branches: 2-5 details/examples per branch.
        - Leaves: specific, concrete items.

        Output format:
        {{
          "root": {{
            "id": "root",
            "label": "...",
            "children": [
              {{"id": "b1", "label": "...", "children": [ ... ]}},
              ...
            ]
          }}
        }}

        IMPORTANT: Output ONLY valid JSON.

        Content:
        {text}
        """
    ).strip()


def build_summary_prompt(text: str, *, budgets: PromptBudgets | None = None) -> str:
    b = budgets or PromptBudgets()
    text = truncate_to_word_budget(text, max_words=b.summary_context_words)

    return textwrap.dedent(
        f"""
        You are a pedagogical content transformation engine.

        TASK: Produce multi-level summaries + key concepts.

        Output ONLY valid JSON:
        {{
          "brief": "~50 words",
          "medium": "~200 words",
          "detailed": "~500 words",
          "key_concepts": [{{"term": "...", "description": "..."}}],
          "related_topics": ["..."],
          "related_links": [{{"label": "...", "url": "https://..."}}]
        }}

        Requirements:
        - Keep the summaries faithful and coherent.
        - Highlight key concepts (5-12 terms).
        - Suggest 5-10 related topics.
        - Provide 3-8 related_links to reputable sources (best-effort URLs).

        Content:
        {text}
        """
    ).strip()


SOCRATIC_PROMPT_TEMPLATES: dict[str, str] = {
    "clarification_easy": "Ask one simple clarification question that checks basic understanding of the learner's statement.",
    "clarification_hard": "Ask a precise clarification question that exposes ambiguity and forces definitions.",
    "exploration_easy": "Ask one exploratory question that invites an example or analogy.",
    "exploration_hard": "Ask an exploratory question that requires linking the idea to a deeper mechanism or model.",
    "implications_easy": "Ask what would happen in a straightforward consequence if the statement were true.",
    "implications_hard": "Ask about second-order implications, tradeoffs, or boundary conditions.",
    "perspective_easy": "Ask how someone from a different role or stakeholder might view this.",
    "perspective_hard": "Ask for a strong alternative viewpoint and what evidence would change minds.",
}
