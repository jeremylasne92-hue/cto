import sys
import os
import importlib.util

# Hack to import ../database.py which is shadowed by this package
# This is needed because the repo has both 'database' directory and 'database.py' file
# and existing code in backend/__init__.py relies on database.py classes.

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    database_py_path = os.path.join(parent_dir, 'database.py')

    if os.path.exists(database_py_path):
        spec = importlib.util.spec_from_file_location("database_legacy", database_py_path)
        database_legacy = importlib.util.module_from_spec(spec)
        sys.modules["database_legacy"] = database_legacy
        spec.loader.exec_module(database_legacy)

        from database_legacy import SRSDatabase, Card, CardSRSState, ReviewLog
        
        # Also export them so 'from backend.database import SRSDatabase' works
        __all__ = ["SRSDatabase", "Card", "CardSRSState", "ReviewLog"]
except Exception as e:
    # If this fails, we just don't export them, but we shouldn't crash the module load
    pass
