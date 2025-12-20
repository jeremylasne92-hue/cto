#!/usr/bin/env python3
"""
Demo script for the Pedagogy Engine
Shows how to generate quizzes and mind maps from ingested content
"""

import asyncio
import json
from datetime import datetime

from src.models import (
    QuizType, QuizRequest, QuizConfig, MindMapRequest, MindMapConfig,
    PedagogyStatus
)
from src.services.database import DatabaseManager
from src.services.pedagogy import PedagogyService


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_quiz(quiz):
    """Pretty print a quiz"""
    print(f"\nQuiz ID: {quiz.quiz_id}")
    print(f"Type: {quiz.quiz_type.value}")
    print(f"Status: {quiz.status.value}")
    print(f"Model Used: {quiz.model_used}")
    print(f"Created: {quiz.created_at}")
    print(f"\nQuestions ({len(quiz.questions)}):")
    
    for idx, q in enumerate(quiz.questions, 1):
        print(f"\n  {idx}. {q['question_text']}")
        
        if q['question_type'] == 'mcq':
            for opt_idx, opt in enumerate(q['options'], ord('A')):
                marker = "✓" if opt['is_correct'] else " "
                print(f"     {chr(opt_idx)}) [{marker}] {opt['text']}")
        
        elif q['question_type'] == 'fill_blank':
            print(f"     Sentence: {q['sentence_with_blank']}")
            print(f"     Answer: {q['answer']['text']}")
            if q['answer'].get('alternatives'):
                print(f"     Alternatives: {', '.join(q['answer']['alternatives'])}")
        
        elif q['question_type'] == 'matching':
            print(f"     Pairs:")
            for pair in q['pairs']:
                print(f"       {pair['left']} → {pair['right']}")
        
        if q.get('explanation'):
            print(f"     Explanation: {q['explanation']}")


def print_mindmap(mindmap, max_depth=None):
    """Pretty print a mind map"""
    print(f"\nMind Map ID: {mindmap.mindmap_id}")
    print(f"Status: {mindmap.status.value}")
    print(f"Model Used: {mindmap.model_used}")
    print(f"Total Nodes: {len(mindmap.nodes)}")
    print(f"Created: {mindmap.created_at}")
    
    if mindmap.root_node:
        print("\nHierarchy:")
        _print_node(mindmap, mindmap.root_node, 0, max_depth)


def _print_node(mindmap, node, depth, max_depth):
    """Recursively print a node and its children"""
    if max_depth is not None and depth > max_depth:
        return
    
    indent = "  " * depth
    marker = "└─" if depth > 0 else "●"
    
    print(f"{indent}{marker} {node.content}")
    if node.summary:
        print(f"{indent}   ({node.summary})")
    
    for child_id in node.children_ids:
        child_node = next((n for n in mindmap.nodes if n.id == child_id), None)
        if child_node:
            _print_node(mindmap, child_node, depth + 1, max_depth)


def setup_sample_data(db_manager: DatabaseManager) -> str:
    """Set up sample data for demo"""
    doc_id = "demo-doc-ml"
    
    existing = db_manager.get_chunks_by_document_id(doc_id)
    if existing:
        print("Sample data already exists, using existing data...")
        return doc_id
    
    doc_data = {
        "id": doc_id,
        "source_type": "plain_text",
        "content": """
Machine learning is a subset of artificial intelligence that focuses on 
building systems that can learn from and make decisions based on data. 
It encompasses various techniques and algorithms.

Supervised learning involves training models with labeled data. In this 
approach, the algorithm learns from input-output pairs to make predictions 
on new, unseen data. Common examples include classification and regression tasks.

Unsupervised learning works with unlabeled data to discover hidden patterns 
or structures. Clustering algorithms like K-means and hierarchical clustering 
are popular unsupervised techniques.

Deep learning is a specialized subset of machine learning that uses neural 
networks with multiple layers. These deep neural networks can automatically 
learn hierarchical representations of data, making them powerful for tasks 
like image recognition and natural language processing.

Neural networks consist of interconnected nodes (neurons) organized in layers. 
The input layer receives data, hidden layers process it, and the output layer 
produces predictions. Training involves adjusting connection weights to minimize 
prediction errors.
        """,
        "metadata_json": {"title": "Introduction to Machine Learning", "topic": "AI"},
        "hash_sha256": "demo_hash_ml_intro",
        "status": "completed"
    }
    
    db_manager.insert_document(doc_data)
    
    content_parts = [
        "Machine learning is a subset of artificial intelligence that focuses on building systems that can learn from and make decisions based on data.",
        "Supervised learning involves training models with labeled data. In this approach, the algorithm learns from input-output pairs to make predictions on new, unseen data.",
        "Unsupervised learning works with unlabeled data to discover hidden patterns or structures. Clustering algorithms like K-means and hierarchical clustering are popular unsupervised techniques.",
        "Deep learning is a specialized subset of machine learning that uses neural networks with multiple layers. These deep neural networks can automatically learn hierarchical representations of data.",
        "Neural networks consist of interconnected nodes (neurons) organized in layers. The input layer receives data, hidden layers process it, and the output layer produces predictions."
    ]
    
    chunks_data = []
    start_pos = 0
    
    for idx, content in enumerate(content_parts):
        chunk_data = {
            "id": f"demo-chunk-{idx}",
            "document_id": doc_id,
            "content": content,
            "chunk_index": idx,
            "start_char": start_pos,
            "end_char": start_pos + len(content),
            "chunk_hash": f"chunk_hash_{idx}",
            "metadata_json": {"part": idx + 1}
        }
        chunks_data.append(chunk_data)
        start_pos += len(content) + 10
    
    db_manager.insert_chunks(chunks_data)
    
    print(f"Created sample document with {len(chunks_data)} chunks")
    return doc_id


def demo_quiz_generation(service: PedagogyService, doc_id: str):
    """Demo quiz generation for all types"""
    print_section("QUIZ GENERATION DEMO")
    
    print("\n1. Generating MCQ Quiz...")
    mcq_request = QuizRequest(
        source_id=doc_id,
        config=QuizConfig(
            quiz_type=QuizType.MCQ,
            num_questions=3,
            difficulty="medium",
            include_explanations=True
        )
    )
    
    print("   Note: This will use hardware-based model selection")
    print("   Premium: Mistral-7B (requires 16GB RAM, 8GB GPU)")
    print("   Standard: Phi-2 (requires 8GB RAM, 4GB GPU)")
    print("   Fallback: Cloud API")
    print("\n   Generating... (this is synchronous in demo)")
    
    try:
        quiz_id = service.generate_quiz(mcq_request)
        print(f"   Quiz generation started: {quiz_id}")
        
        import time
        time.sleep(1)
        
        quiz = service.get_quiz(quiz_id)
        if quiz and quiz.status == PedagogyStatus.COMPLETED:
            print_quiz(quiz)
        else:
            print(f"   Quiz status: {quiz.status if quiz else 'Not found'}")
            if quiz and quiz.error_message:
                print(f"   Error: {quiz.error_message}")
    
    except Exception as e:
        print(f"   Error: {e}")
        print("   Note: This is expected if model generation is not configured")


def demo_mindmap_generation(service: PedagogyService, doc_id: str):
    """Demo mind map generation"""
    print_section("MIND MAP GENERATION DEMO")
    
    print("\n1. Generating Hierarchical Mind Map...")
    mindmap_request = MindMapRequest(
        source_id=doc_id,
        config=MindMapConfig(
            max_depth=4,
            max_children_per_node=6,
            include_summaries=True
        )
    )
    
    print("   Generating... (this is synchronous in demo)")
    
    try:
        mindmap_id = service.generate_mindmap(mindmap_request)
        print(f"   Mind map generation started: {mindmap_id}")
        
        import time
        time.sleep(1)
        
        mindmap = service.get_mindmap(mindmap_id)
        if mindmap and mindmap.status == PedagogyStatus.COMPLETED:
            print_mindmap(mindmap, max_depth=3)
        else:
            print(f"   Mind map status: {mindmap.status if mindmap else 'Not found'}")
            if mindmap and mindmap.error_message:
                print(f"   Error: {mindmap.error_message}")
    
    except Exception as e:
        print(f"   Error: {e}")
        print("   Note: This is expected if model generation is not configured")


def demo_model_selection(service: PedagogyService):
    """Demo model selection logic"""
    print_section("MODEL SELECTION DEMO")
    
    model_manager = service.model_manager
    
    print("\n1. Hardware Benchmark:")
    hw = model_manager.hardware_benchmark
    print(f"   CPU Score: {hw.cpu_score:.2f}")
    print(f"   RAM: {hw.ram_gb:.2f} GB")
    print(f"   GPU Available: {'Yes' if hw.gpu_available else 'No'}")
    if hw.gpu_available:
        print(f"   GPU Memory: {hw.gpu_memory_gb:.2f} GB")
    
    print("\n2. Model Availability:")
    
    for model_name in ["mistral-7b", "phi-2"]:
        availability = model_manager.check_model_availability(model_name)
        print(f"\n   {model_name.upper()}:")
        print(f"     Tier: {availability.tier.value}")
        print(f"     Available: {'✓' if availability.available else '✗'}")
        print(f"     Requirements:")
        print(f"       - RAM: {availability.ram_requirement_gb} GB")
        print(f"       - GPU: {availability.gpu_requirement_gb} GB")
    
    print("\n3. Selected Model:")
    selected_model, tier = model_manager.select_model()
    print(f"   Model: {selected_model}")
    print(f"   Tier: {tier.value}")
    
    if tier.value == "cloud":
        print(f"   Cloud API Configured: {'Yes' if model_manager.cloud_api_url else 'No'}")


def main():
    """Run the complete demo"""
    print("\n" + "=" * 70)
    print("  PEDAGOGY ENGINE DEMO")
    print("  AI-Driven Quiz and Mind Map Generation")
    print("=" * 70)
    
    db_manager = DatabaseManager("demo_pedagogy.db")
    db_manager.create_tables()
    
    service = PedagogyService(db_manager=db_manager)
    
    doc_id = setup_sample_data(db_manager)
    
    demo_model_selection(service)
    
    print("\n\nNote: The following demos will attempt to generate content using LLMs.")
    print("If models are not available or configured, you'll see errors (expected).")
    print("In production, configure cloud API endpoints or ensure local models are available.")
    
    input("\nPress Enter to continue with quiz generation demo...")
    demo_quiz_generation(service, doc_id)
    
    input("\nPress Enter to continue with mind map generation demo...")
    demo_mindmap_generation(service, doc_id)
    
    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Configure cloud LLM API (set CLOUD_LLM_API_URL env var)")
    print("2. Or ensure local models are downloaded and hardware meets requirements")
    print("3. Use the REST API endpoints in production:")
    print("   - POST /pedagogy/quiz")
    print("   - GET /pedagogy/quiz/{quiz_id}")
    print("   - POST /pedagogy/mindmap")
    print("   - GET /pedagogy/mindmap/{mindmap_id}")
    print("   - GET /pedagogy/models/status")


if __name__ == "__main__":
    main()
