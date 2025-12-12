# Cognisphere Pedagogical Transformation Engine (PTE)

Phase 1 foundation for AI-powered content transformation:

- Hardware-aware hybrid LLM selector (local GGUF via `llama.cpp` when available, cloud fallback)
- Quiz generation (varied question types + basic quality checks)
- Mind map generation (hierarchical D3-ready JSON)
- Multi-level summaries
- Socratic tutor prompt templates
- On-disk caching with similarity reuse

## Quickstart (library)

```python
from cognisphere_pte.engine import TransformationEngine

engine = TransformationEngine()
quiz = engine.generate_quiz(["Your content chunk..."], num_questions=5)
print(quiz.to_dict())
```

## CLI

```bash
cognisphere-pte quiz --text-file chapter.txt --num-questions 6
cognisphere-pte mindmap --text-file article.txt
cognisphere-pte summary --text-file article.txt
```

> Local model inference requires installing extras: `pip install .[local-llm]` and enough RAM/GPU.
