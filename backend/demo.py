import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.services.ingestion_service import IngestionService
from app.core.source_detector import SourceDetector
import tempfile

Base.metadata.create_all(bind=engine)


def demo_text_ingestion():
    print("\n=== Demo 1: Text Ingestion ===")
    
    db = SessionLocal()
    service = IngestionService(db)
    
    sample_text = """
    Artificial Intelligence and Machine Learning
    
    Artificial intelligence (AI) is transforming the world as we know it. 
    Machine learning, a subset of AI, enables computers to learn from data 
    and improve their performance over time without being explicitly programmed.
    
    Deep learning, which uses neural networks with multiple layers, has achieved 
    remarkable results in image recognition, natural language processing, and 
    game playing. These technologies are now being applied to solve real-world 
    problems in healthcare, finance, transportation, and many other fields.
    """
    
    try:
        source = service.ingest(sample_text)
        print(f"✓ Ingested text content")
        print(f"  Source ID: {source.id}")
        print(f"  Title: {source.title or 'N/A'}")
        print(f"  Hash: {source.hash[:16]}...")
        print(f"  Chunks created: {len(source.chunks)}")
        
        print("\n  Searching for 'machine learning'...")
        results = service.search("machine learning", limit=3, source_id=source.id)
        print(f"  Found {len(results)} results")
        if results:
            print(f"  Top result: {results[0]['text'][:100]}...")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    finally:
        db.close()


def demo_markdown_ingestion():
    print("\n=== Demo 2: Markdown File Ingestion ===")
    
    db = SessionLocal()
    service = IngestionService(db)
    
    markdown_content = """# Python Programming Guide

## Introduction

Python is a high-level, interpreted programming language known for its simplicity and readability.

## Key Features

- Easy to learn and use
- Extensive standard library
- Strong community support
- Versatile for various applications

## Code Example

```python
def hello_world():
    print("Hello, World!")

hello_world()
```

## Conclusion

Python continues to be one of the most popular programming languages worldwide.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(markdown_content)
        temp_file = f.name
    
    try:
        source = service.ingest(temp_file, temp_file)
        print(f"✓ Ingested markdown file")
        print(f"  Source ID: {source.id}")
        print(f"  Type: {source.source_type}")
        print(f"  Chunks created: {len(source.chunks)}")
        
        print("\n  Searching for 'Python features'...")
        results = service.search("Python features", limit=2, source_id=source.id)
        print(f"  Found {len(results)} results")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    finally:
        os.unlink(temp_file)
        db.close()


def demo_duplicate_detection():
    print("\n=== Demo 3: Duplicate Detection ===")
    
    db = SessionLocal()
    service = IngestionService(db)
    
    sample_text = "This is a test for duplicate detection."
    
    try:
        source1 = service.ingest(sample_text)
        print(f"✓ First ingestion - Source ID: {source1.id}")
        
        source2 = service.ingest(sample_text)
        print(f"✓ Second ingestion (duplicate detected) - Source ID: {source2.id}")
        
        if source1.id == source2.id:
            print("  ✓ Duplicate correctly detected - returned existing source")
        else:
            print("  ✗ Duplicate not detected")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    finally:
        db.close()


def demo_semantic_search():
    print("\n=== Demo 4: Semantic Search ===")
    
    db = SessionLocal()
    service = IngestionService(db)
    
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Python is a popular programming language for data science.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing helps computers understand human language.",
    ]
    
    try:
        print("Ingesting documents...")
        for i, doc in enumerate(documents):
            source = service.ingest(doc)
            print(f"  ✓ Document {i+1} ingested (ID: {source.id})")
        
        print("\nPerforming semantic searches...")
        
        queries = [
            "AI and neural networks",
            "programming languages",
            "animals and wildlife"
        ]
        
        for query in queries:
            print(f"\n  Query: '{query}'")
            results = service.search(query, limit=2)
            for i, result in enumerate(results):
                print(f"    {i+1}. {result['text']}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    finally:
        db.close()


def main():
    print("=" * 60)
    print("Universal Content Ingestion Pipeline - Demo")
    print("=" * 60)
    
    demo_text_ingestion()
    demo_markdown_ingestion()
    demo_duplicate_detection()
    demo_semantic_search()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
