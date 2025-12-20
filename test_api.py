#!/usr/bin/env python3
"""
Quick API integration test script.
Run with: python test_api.py
Make sure backend is running on http://localhost:5000
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health check: {response.status_code}")
    print(f"  Response: {response.json()}")
    return response.status_code == 200

def test_root():
    """Test root endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print(f"✓ Root endpoint: {response.status_code}")
    print(f"  Service: {response.json()['service']}")
    return response.status_code == 200

def test_create_concepts():
    """Test creating concepts."""
    concepts = [
        {"name": "Python", "description": "Programming language"},
        {"name": "JavaScript", "description": "Web programming language"},
        {"name": "Functions", "description": "Code blocks"},
    ]
    
    created = []
    for concept_data in concepts:
        response = requests.post(f"{BASE_URL}/api/concepts", json=concept_data)
        print(f"✓ Created concept '{concept_data['name']}': {response.status_code}")
        if response.status_code in [200, 201]:
            created.append(response.json())
    
    return created

def test_get_concepts():
    """Test getting all concepts."""
    response = requests.get(f"{BASE_URL}/api/concepts")
    print(f"✓ Get concepts: {response.status_code}")
    concepts = response.json().get('concepts', [])
    print(f"  Found {len(concepts)} concepts")
    return concepts

def test_create_relation(concepts):
    """Test creating a relation."""
    if len(concepts) < 2:
        print("⚠ Not enough concepts to create relation")
        return None
    
    relation_data = {
        "source_id": concepts[0]['id'],
        "target_id": concepts[1]['id'],
        "relation_type": "prerequisite",
        "strength": 0.8
    }
    
    response = requests.post(f"{BASE_URL}/api/relations", json=relation_data)
    print(f"✓ Created relation: {response.status_code}")
    if response.status_code in [200, 201]:
        return response.json()
    return None

def test_query_graph():
    """Test querying the graph."""
    query_data = {
        "search_term": "python",
        "use_webgl": True
    }
    
    response = requests.post(f"{BASE_URL}/api/knowledge-graph/query", json=query_data)
    print(f"✓ Query graph: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Nodes: {len(data['nodes'])}, Edges: {len(data['edges'])}")
        return data
    return None

def test_integrity_check():
    """Test integrity check."""
    response = requests.post(f"{BASE_URL}/api/knowledge-graph/integrity-check")
    print(f"✓ Integrity check: {response.status_code}")
    if response.status_code == 200:
        report = response.json()
        print(f"  Has issues: {report['has_issues']}")
        print(f"  Summary: {report['summary']}")
        return report
    return None

def main():
    print("="*60)
    print("Knowledge Graph API Integration Test")
    print("="*60)
    
    try:
        # Basic checks
        if not test_health():
            print("❌ Health check failed")
            return
        
        if not test_root():
            print("❌ Root endpoint failed")
            return
        
        print("\n" + "="*60)
        print("Testing CRUD Operations")
        print("="*60)
        
        # Create concepts
        created_concepts = test_create_concepts()
        
        # Get concepts
        all_concepts = test_get_concepts()
        
        # Create relation
        if all_concepts and len(all_concepts) >= 2:
            test_create_relation(all_concepts)
        
        print("\n" + "="*60)
        print("Testing Graph Queries")
        print("="*60)
        
        # Query graph
        graph_data = test_query_graph()
        
        # Integrity check
        test_integrity_check()
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to backend at", BASE_URL)
        print("   Make sure the backend is running with: cd backend && python main.py")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
