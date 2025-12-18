# Pedagogy Engine – Quiz & Mind Map Transformation

This repository contains a small transformation engine that can:

- Select an LLM backend based on hardware tier (local GGUF via `llama.cpp`, or cloud fallback)
- Generate quizzes (5+ questions, varied types)
- Generate hierarchical mind maps ready for D3.js rendering
- Generate multi-level summaries
- Provide Socratic tutor prompt templates
- Cache/reuse generated artifacts and reuse for near-duplicate content via similarity search

## Quickstart (no external dependencies)

The engine works out-of-the-box in **offline mode** using deterministic heuristics (useful for CI/dev). For better results, configure a cloud key or install local model dependencies.

```bash
python -m pedagogy_engine quiz path/to/chapter.txt
python -m pedagogy_engine mindmap https://example.com/article
python -m pedagogy_engine summary path/to/chapter.txt
python -m pedagogy_engine socratic
```

## Local models (Premium/Standard tiers)

Local inference is implemented via `llama-cpp-python` + GGUF weights.

- Premium: Mistral-7B-Instruct-v0.2 (Q4_K_M)
- Standard: Phi-2 (Q4_K_M)
- Minimum: Cloud fallback

You can override behavior using environment variables:

- `PEDAGOGY_ENGINE_TIER=premium|standard|minimum`
- `PEDAGOGY_ENGINE_MODE=local|cloud|hybrid`
- `PEDAGOGY_ENGINE_MODEL_PATH=/path/to/model.gguf`
- `PEDAGOGY_ENGINE_ALLOW_DOWNLOAD=0|1`

## Cloud fallback

Supported (no SDK required):

- OpenAI: `OPENAI_API_KEY` (+ optional `OPENAI_MODEL`, `OPENAI_BASE_URL`)
- Groq (OpenAI-compatible): `GROQ_API_KEY` (+ optional `GROQ_MODEL`, `GROQ_BASE_URL`)
- Anthropic: `ANTHROPIC_API_KEY` (+ optional `ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`)

## Library usage

```python
from pedagogy_engine import TransformationEngine

engine = TransformationEngine()
quiz = engine.generate_quiz(content_text, num_questions=7)
mindmap = engine.generate_mind_map(article_text)
summaries = engine.generate_summaries(content_text)
```
