#!/usr/bin/env python3
"""
Validation script to ensure all pedagogy engine components are implemented
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ MISSING {description}: {filepath}")
        return False

def check_code_structure():
    """Validate code structure"""
    print("\n" + "="*70)
    print("CODE STRUCTURE VALIDATION")
    print("="*70)
    
    checks = [
        ("src/models.py", "Data Models"),
        ("src/services/prompts.py", "Prompt Templates"),
        ("src/services/model_manager.py", "Model Manager"),
        ("src/services/pedagogy.py", "Pedagogy Service"),
        ("src/api/pedagogy.py", "API Endpoints"),
    ]
    
    passed = sum(check_file_exists(f, d) for f, d in checks)
    total = len(checks)
    
    return passed == total

def check_database_updates():
    """Check database updates"""
    print("\n" + "="*70)
    print("DATABASE UPDATES VALIDATION")
    print("="*70)
    
    db_file = "src/services/database.py"
    
    if not Path(db_file).exists():
        print(f"✗ Database file not found: {db_file}")
        return False
    
    with open(db_file, 'r') as f:
        content = f.read()
    
    required_classes = [
        "QuizDB",
        "QuestionDB", 
        "MindMapDB",
        "MindMapNodeDB"
    ]
    
    required_methods = [
        "insert_quiz",
        "get_quiz",
        "insert_questions",
        "get_questions_by_quiz_id",
        "insert_mindmap",
        "get_mindmap",
        "insert_mindmap_nodes",
        "get_mindmap_nodes"
    ]
    
    all_passed = True
    
    for cls in required_classes:
        if f"class {cls}" in content:
            print(f"✓ Database table: {cls}")
        else:
            print(f"✗ MISSING database table: {cls}")
            all_passed = False
    
    for method in required_methods:
        if f"def {method}" in content:
            print(f"✓ Database method: {method}")
        else:
            print(f"✗ MISSING database method: {method}")
            all_passed = False
    
    return all_passed

def check_tests():
    """Check test files"""
    print("\n" + "="*70)
    print("TESTS VALIDATION")
    print("="*70)
    
    checks = [
        ("tests/unit/test_pedagogy.py", "Unit Tests"),
        ("tests/integration/test_pedagogy_integration.py", "Integration Tests"),
        ("tests/integration/test_pedagogy_api.py", "API Tests"),
    ]
    
    passed = sum(check_file_exists(f, d) for f, d in checks)
    total = len(checks)
    
    return passed == total

def check_documentation():
    """Check documentation"""
    print("\n" + "="*70)
    print("DOCUMENTATION VALIDATION")
    print("="*70)
    
    checks = [
        ("PEDAGOGY_ENGINE.md", "Pedagogy Engine Documentation"),
        ("IMPLEMENTATION_SUMMARY.md", "Implementation Summary"),
        ("demo_pedagogy.py", "Demo Script"),
        ("README.md", "Updated README"),
    ]
    
    passed = sum(check_file_exists(f, d) for f, d in checks)
    total = len(checks)
    
    return passed == total

def check_api_integration():
    """Check API integration"""
    print("\n" + "="*70)
    print("API INTEGRATION VALIDATION")
    print("="*70)
    
    api_file = "src/api/__init__.py"
    
    if not Path(api_file).exists():
        print(f"✗ API file not found: {api_file}")
        return False
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    if "from .pedagogy import router as pedagogy_router" in content:
        print("✓ Pedagogy router imported")
    else:
        print("✗ MISSING pedagogy router import")
        return False
    
    if "app.include_router(pedagogy_router)" in content:
        print("✓ Pedagogy router registered")
    else:
        print("✗ MISSING pedagogy router registration")
        return False
    
    return True

def check_requirements():
    """Check requirements updates"""
    print("\n" + "="*70)
    print("REQUIREMENTS VALIDATION")
    print("="*70)
    
    req_file = "requirements.txt"
    
    if not Path(req_file).exists():
        print(f"✗ Requirements file not found: {req_file}")
        return False
    
    with open(req_file, 'r') as f:
        content = f.read()
    
    required_packages = [
        "torch",
        "transformers",
        "psutil"
    ]
    
    all_passed = True
    
    for package in required_packages:
        if package in content:
            print(f"✓ Dependency added: {package}")
        else:
            print(f"✗ MISSING dependency: {package}")
            all_passed = False
    
    return all_passed

def check_models_and_enums():
    """Check models file for required enums and classes"""
    print("\n" + "="*70)
    print("MODELS & ENUMS VALIDATION")
    print("="*70)
    
    models_file = "src/models.py"
    
    if not Path(models_file).exists():
        print(f"✗ Models file not found: {models_file}")
        return False
    
    with open(models_file, 'r') as f:
        content = f.read()
    
    required_items = [
        ("QuizType", "enum"),
        ("ModelTier", "enum"),
        ("PedagogyStatus", "enum"),
        ("QuizRequest", "model"),
        ("QuizResponse", "model"),
        ("MindMapRequest", "model"),
        ("MindMapResponse", "model"),
        ("MindMapNode", "model"),
        ("HardwareBenchmark", "model"),
        ("ModelAvailability", "model"),
    ]
    
    all_passed = True
    
    for item, item_type in required_items:
        if f"class {item}" in content:
            print(f"✓ {item_type.capitalize()}: {item}")
        else:
            print(f"✗ MISSING {item_type}: {item}")
            all_passed = False
    
    return all_passed

def main():
    """Run all validation checks"""
    print("\n" + "="*70)
    print("PEDAGOGY ENGINE IMPLEMENTATION VALIDATION")
    print("="*70)
    
    results = {
        "Code Structure": check_code_structure(),
        "Database Updates": check_database_updates(),
        "Tests": check_tests(),
        "Documentation": check_documentation(),
        "API Integration": check_api_integration(),
        "Requirements": check_requirements(),
        "Models & Enums": check_models_and_enums(),
    }
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for category, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {category}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Implementation Complete!")
    else:
        print("✗ SOME CHECKS FAILED - Review output above")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
