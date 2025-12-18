from __future__ import annotations

SOCRATIC_PROMPTS = {
    "meta": {
        "version": "1",
        "purpose": "Prompt templates for a Socratic tutor (foundation only; not conversational runtime).",
    },
    "difficulty_progression": {
        "easy": "Use concrete language. Ask about definitions and simple examples.",
        "medium": "Ask the learner to connect ideas, justify reasoning, and compare alternatives.",
        "hard": "Probe edge cases, hidden assumptions, implications, and trade-offs.",
    },
    "question_types": {
        "clarification": {
            "template": (
                "Topic: {topic}\n"
                "Student statement: {student_statement}\n\n"
                "Ask 1-2 clarification questions that help define terms, remove ambiguity, and make the claim precise."
            )
        },
        "exploration": {
            "template": (
                "Topic: {topic}\n"
                "Current understanding: {student_statement}\n\n"
                "Ask 2-3 questions that explore reasons, evidence, mechanisms, and examples."
            )
        },
        "implications": {
            "template": (
                "Topic: {topic}\n"
                "Student claim: {student_statement}\n\n"
                "Ask questions about consequences, downstream effects, and what would change if the claim were true."
            )
        },
        "perspective": {
            "template": (
                "Topic: {topic}\n"
                "Student view: {student_statement}\n\n"
                "Ask questions that surface alternative viewpoints, counterexamples, and stakeholder perspectives."
            )
        },
    },
}
