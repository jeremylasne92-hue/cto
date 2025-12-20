# Pedagogy Engine

AI-driven pedagogical transformation module that generates quizzes and mind maps from ingested content using hybrid local/cloud LLM selection.

## Features

### Quiz Generation
- **Multiple Choice Questions (MCQ)**: Generate 4-option questions with explanations
- **Fill in the Blank**: Create context-based fill-in-the-blank questions
- **Matching**: Generate matching pair questions for concepts and definitions

### Mind Map Generation
- **Hierarchical Structure**: Automatic organization into tree structure
- **Configurable Depth**: Control hierarchy depth (1-10 levels)
- **Branching Control**: Limit children per node (2-20)
- **Summaries**: Optional node summaries for better understanding

### Hybrid Model Selection
- **Hardware Benchmarking**: Automatic CPU, RAM, and GPU detection
- **Local Models**:
  - Mistral-7B (Premium tier): 16GB RAM, 8GB GPU required
  - Phi-2 (Standard tier): 8GB RAM, 4GB GPU required
- **Cloud Fallback**: Automatic fallback to cloud API when hardware insufficient
- **Model Caching**: Cache availability checks to optimize performance
- **Lazy Loading**: Models loaded on-demand to conserve resources

## Architecture

```
┌─────────────────────┐
│  Ingested Chunks    │
│  (from documents)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Prompt Builder     │
│  - MCQ templates    │
│  - Fill blank       │
│  - Matching         │
│  - Mind map         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐      ┌──────────────────┐
│  Model Manager      │─────▶│  Hardware        │
│  - Benchmark HW     │      │  Benchmarking    │
│  - Select model     │      └──────────────────┘
│  - Load/Generate    │
└──────────┬──────────┘
           │
           ├──────────┬──────────────┐
           ▼          ▼              ▼
    ┌──────────┐ ┌─────────┐  ┌──────────┐
    │Mistral-7B│ │  Phi-2  │  │  Cloud   │
    │ Premium  │ │Standard │  │   API    │
    └────┬─────┘ └────┬────┘  └─────┬────┘
         │            │             │
         └────────────┴─────────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │  Post-Processor     │
           │  - Parse JSON       │
           │  - Validate format  │
           │  - Structure data   │
           └──────────┬──────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │  SQLite Storage     │
           │  - Quizzes          │
           │  - Questions        │
           │  - Mind maps        │
           │  - Nodes            │
           └─────────────────────┘
```

## Installation

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# For local models (optional)
pip install torch transformers accelerate
```

### Environment Variables

```bash
# Cloud API configuration (optional, for fallback)
export CLOUD_LLM_API_URL="https://api.your-llm-provider.com/generate"
export CLOUD_LLM_API_KEY="your-api-key"
```

## Usage

### REST API Endpoints

#### Generate Quiz

```http
POST /pedagogy/quiz
Content-Type: application/json

{
  "source_id": "doc-123",           # Or use chunk_ids
  "config": {
    "quiz_type": "mcq",             # mcq | fill_blank | matching
    "num_questions": 5,
    "difficulty": "medium",         # easy | medium | hard
    "include_explanations": true
  }
}

Response:
{
  "quiz_id": "quiz-abc-123",
  "message": "Quiz generation started (mcq)",
  "status_endpoint": "/pedagogy/quiz/quiz-abc-123",
  "config": { ... }
}
```

#### Retrieve Quiz

```http
GET /pedagogy/quiz/{quiz_id}

Response:
{
  "quiz_id": "quiz-abc-123",
  "status": "completed",
  "quiz_type": "mcq",
  "questions": [
    {
      "question_text": "What is machine learning?",
      "question_type": "mcq",
      "options": [
        {"text": "A subset of AI", "is_correct": true},
        {"text": "A programming language", "is_correct": false},
        ...
      ],
      "explanation": "Machine learning is a subset of AI...",
      "metadata": {}
    }
  ],
  "model_used": "mistral-7b",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "error_message": null
}
```

#### Generate Mind Map

```http
POST /pedagogy/mindmap
Content-Type: application/json

{
  "source_id": "doc-123",
  "config": {
    "max_depth": 4,
    "max_children_per_node": 7,
    "include_summaries": true
  }
}

Response:
{
  "mindmap_id": "mindmap-xyz-789",
  "message": "Mind map generation started",
  "status_endpoint": "/pedagogy/mindmap/mindmap-xyz-789",
  "config": { ... }
}
```

#### Retrieve Mind Map

```http
GET /pedagogy/mindmap/{mindmap_id}

Response:
{
  "mindmap_id": "mindmap-xyz-789",
  "status": "completed",
  "root_node": {
    "id": "node-1",
    "content": "Machine Learning",
    "summary": "Overview of ML concepts",
    "level": 0,
    "parent_id": null,
    "children_ids": ["node-2", "node-3"],
    "metadata": {}
  },
  "nodes": [ ... ],
  "model_used": "phi-2",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "error_message": null
}
```

#### Check Model Status

```http
GET /pedagogy/models/status

Response:
{
  "hardware": {
    "cpu_score": 8.5,
    "ram_gb": 16.0,
    "gpu_available": true,
    "gpu_memory_gb": 8.0
  },
  "models": {
    "mistral-7b": {
      "tier": "premium",
      "available": true,
      "loaded": false,
      "requirements": {
        "ram_gb": 16.0,
        "gpu_gb": 8.0
      }
    },
    "phi-2": {
      "tier": "standard",
      "available": true,
      "loaded": false,
      "requirements": {
        "ram_gb": 8.0,
        "gpu_gb": 4.0
      }
    }
  },
  "cloud_configured": true,
  "selected_model": "mistral-7b"
}
```

### Python SDK

```python
from src.models import QuizType, QuizRequest, QuizConfig, MindMapRequest
from src.services.pedagogy import PedagogyService

# Initialize service
service = PedagogyService()

# Generate MCQ quiz
quiz_request = QuizRequest(
    source_id="doc-123",
    config=QuizConfig(
        quiz_type=QuizType.MCQ,
        num_questions=5,
        difficulty="medium"
    )
)
quiz_id = service.generate_quiz(quiz_request)

# Retrieve quiz (after generation completes)
quiz = service.get_quiz(quiz_id)
print(f"Quiz has {len(quiz.questions)} questions")

# Generate mind map
mindmap_request = MindMapRequest(
    source_id="doc-123",
    config={"max_depth": 4}
)
mindmap_id = service.generate_mindmap(mindmap_request)

# Retrieve mind map
mindmap = service.get_mindmap(mindmap_id)
print(f"Mind map has {len(mindmap.nodes)} nodes")
```

## Model Selection Logic

### Hardware Requirements

| Model | Tier | RAM | GPU | CPU Score |
|-------|------|-----|-----|-----------|
| Mistral-7B | Premium | 16GB | 8GB | 8.0+ |
| Phi-2 | Standard | 8GB | 4GB | 4.0+ |
| Cloud API | Fallback | - | - | - |

### Selection Algorithm

1. **Benchmark Hardware**: Detect CPU, RAM, and GPU specifications
2. **Check Premium Model**: If Mistral-7B requirements met, use it
3. **Check Standard Model**: If Phi-2 requirements met, use it
4. **Fallback to Cloud**: If no local models available, use cloud API
5. **Cache Results**: Cache availability for 1 hour to avoid re-checking

### CPU Score Calculation

```
CPU Score = (Physical Cores) × (Frequency in GHz)
```

Example:
- 4 cores @ 2.5 GHz = 10.0 score
- 8 cores @ 2.0 GHz = 16.0 score

## Prompt Templates

### MCQ Template

```
You are an expert educational content creator. Based on the following content, 
generate {num_questions} multiple-choice questions at {difficulty} difficulty level.

Content:
{content}

Requirements:
1. Each question should have exactly 4 options (A, B, C, D)
2. Only ONE option should be correct
3. Questions should test understanding, not just memorization
4. Include a brief explanation for the correct answer
5. Ensure questions are clear and unambiguous

Output format (JSON): ...
```

### Mind Map Template

```
You are an expert at creating hierarchical mind maps. Based on the following content, 
create a structured mind map with a maximum depth of {max_depth} levels and 
maximum {max_children} children per node.

Content:
{content}

Requirements:
1. Start with a single root concept that captures the main topic
2. Each node should have a concise content/title (3-8 words)
3. Organize information hierarchically from general to specific
4. Balance the tree - avoid one branch being much deeper than others
...
```

## Database Schema

### Quizzes Table

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Quiz UUID |
| source_id | STRING | Source document ID |
| quiz_type | STRING | mcq, fill_blank, or matching |
| status | STRING | pending, running, completed, failed |
| model_used | STRING | Model that generated the quiz |
| metadata_json | JSON | Configuration and metadata |
| created_at | DATETIME | Creation timestamp |
| completed_at | DATETIME | Completion timestamp |
| error_message | TEXT | Error details if failed |

### Questions Table

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Question UUID |
| quiz_id | STRING | Parent quiz ID |
| question_text | TEXT | Question text |
| question_type | STRING | Quiz type |
| question_data | JSON | Options/answers/pairs |
| explanation | TEXT | Answer explanation |
| metadata_json | JSON | Additional metadata |
| created_at | DATETIME | Creation timestamp |

### Mind Maps Table

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Mind map UUID |
| source_id | STRING | Source document ID |
| status | STRING | pending, running, completed, failed |
| model_used | STRING | Model that generated the map |
| root_node_id | STRING | Root node UUID |
| metadata_json | JSON | Configuration and metadata |
| created_at | DATETIME | Creation timestamp |
| completed_at | DATETIME | Completion timestamp |
| error_message | TEXT | Error details if failed |

### Mind Map Nodes Table

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Node UUID |
| mindmap_id | STRING | Parent mind map ID |
| parent_id | STRING | Parent node ID (null for root) |
| content | TEXT | Node content/title |
| summary | TEXT | Optional node summary |
| level | INTEGER | Depth in tree (0 = root) |
| metadata_json | JSON | Additional metadata |
| created_at | DATETIME | Creation timestamp |

## Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/test_pedagogy.py -v

# Test specific components
pytest tests/unit/test_pedagogy.py::TestPromptTemplates -v
pytest tests/unit/test_pedagogy.py::TestModelManager -v
pytest tests/unit/test_pedagogy.py::TestPedagogyService -v
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/test_pedagogy_integration.py -v
pytest tests/integration/test_pedagogy_api.py -v

# Run with coverage
pytest tests/ --cov=src.services.pedagogy --cov-report=html
```

### Demo Script

```bash
# Run interactive demo
python demo_pedagogy.py
```

## Performance

### Quiz Generation

| Quiz Type | Questions | Avg Time (local) | Avg Time (cloud) |
|-----------|-----------|------------------|------------------|
| MCQ | 5 | 8-15s | 3-8s |
| Fill Blank | 5 | 6-12s | 2-6s |
| Matching | 5 | 7-14s | 3-7s |

### Mind Map Generation

| Depth | Nodes | Avg Time (local) | Avg Time (cloud) |
|-------|-------|------------------|------------------|
| 3 | 10-20 | 10-20s | 4-10s |
| 4 | 20-40 | 15-30s | 6-15s |
| 5 | 40-80 | 25-50s | 10-25s |

*Times vary based on content complexity and hardware*

## Error Handling

### Common Errors

1. **No Source Data**: Ensure document/chunks are ingested before generation
2. **Hardware Insufficient**: Configure cloud API as fallback
3. **Invalid JSON**: LLM response parsing fails, will retry with better prompts
4. **Model Load Failed**: Fallback to cloud API automatically

### Status Codes

- `pending`: Generation queued but not started
- `running`: Currently generating
- `completed`: Successfully generated
- `failed`: Generation failed (see error_message)

## Troubleshooting

### Local Models Not Loading

```bash
# Check hardware requirements
curl http://localhost:8000/pedagogy/models/status

# Manually download models
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('microsoft/phi-2')"
```

### Cloud API Issues

```bash
# Verify API configuration
echo $CLOUD_LLM_API_URL
echo $CLOUD_LLM_API_KEY

# Test API connectivity
curl -X POST $CLOUD_LLM_API_URL \
  -H "Authorization: Bearer $CLOUD_LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "max_tokens": 10}'
```

### Generation Failures

Check quiz/mindmap status for error messages:

```bash
curl http://localhost:8000/pedagogy/quiz/{quiz_id}
```

Common issues:
- Insufficient content in chunks
- LLM output format invalid
- Model generation timeout

## Future Enhancements

- [ ] Add more quiz types (True/False, Short Answer)
- [ ] Support for images in questions
- [ ] Difficulty auto-adjustment based on content
- [ ] Multi-language support
- [ ] Quiz validation and quality scoring
- [ ] Mind map visualization endpoint
- [ ] Batch generation for multiple sources
- [ ] Custom prompt template support
- [ ] Model fine-tuning for better education content

## License

MIT License - see LICENSE file for details.
