import sys
import os

# Add parent directory to path so we can import from db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import create_db_and_tables

if __name__ == "__main__":
    create_db_and_tables()
