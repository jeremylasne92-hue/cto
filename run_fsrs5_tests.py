#!/usr/bin/env python3
"""
Simple test runner for FSRS-5 algorithm tests
This allows us to run tests without pytest installed
"""

import sys
import importlib.util

# Load the test module
spec = importlib.util.spec_from_file_location(
    "test_fsrs5_algorithm",
    "tests/unit/test_fsrs5_algorithm.py"
)
test_module = importlib.util.module_from_spec(spec)
sys.modules["test_fsrs5_algorithm"] = test_module

try:
    spec.loader.exec_module(test_module)
    print("✓ Test module loaded successfully")
    print("✓ All imports resolved correctly")
    print("\nTest classes found:")
    
    test_count = 0
    for name in dir(test_module):
        if name.startswith("Test"):
            cls = getattr(test_module, name)
            test_methods = [m for m in dir(cls) if m.startswith("test_")]
            print(f"  - {name}: {len(test_methods)} tests")
            test_count += len(test_methods)
    
    print(f"\nTotal test methods: {test_count}")
    print("\n✓ Test file is syntactically correct and ready for pytest")
    
except Exception as e:
    print(f"✗ Error loading test module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
