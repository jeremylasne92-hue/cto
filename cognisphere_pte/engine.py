from __future__ import annotations

from dataclasses import dataclass

from cognisphere_pte.cache import TransformationCache
from cognisphere_pte.llm.selector import HybridLLM
from cognisphere_pte.prompts import SOCRATIC_PROMPT_TEMPLATES
from cognisphere_pte.transformers.mindmap import MindMap, MindMapGenerator
from cognisphere_pte.transformers.quiz import Quiz, QuizGenerator
from cognisphere_pte.transformers.summary import MultiSummary, SummaryGenerator


@dataclass
class TransformationEngine:
    llm: HybridLLM | None = None
    cache: TransformationCache | None = None

    def __post_init__(self) -> None:
        self.llm = self.llm or HybridLLM()
        self.cache = self.cache or TransformationCache()

        self._quiz = QuizGenerator(llm=self.llm, cache=self.cache)
        self._mindmap = MindMapGenerator(llm=self.llm, cache=self.cache)
        self._summary = SummaryGenerator(llm=self.llm, cache=self.cache)

    def generate_quiz(self, chunks: list[str], *, num_questions: int = 5) -> Quiz:
        return self._quiz.generate(chunks, num_questions=num_questions)

    def generate_mindmap(self, text: str) -> MindMap:
        return self._mindmap.generate(text)

    def generate_summary(self, text: str) -> MultiSummary:
        return self._summary.generate(text)

    def socratic_prompt_templates(self) -> dict[str, str]:
        return dict(SOCRATIC_PROMPT_TEMPLATES)
