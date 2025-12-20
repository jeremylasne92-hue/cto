from sqlmodel import SQLModel, create_engine
import os
from pathlib import Path

APP_DATA_DIR = Path(os.getenv("APPDATA") or os.getenv("XDG_DATA_HOME") or Path.home() / ".local/share") / "Cognisphere"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DATA_DIR / "database.sqlite"
LANCEDB_PATH = APP_DATA_DIR / "lancedb"

engine = create_engine(f"sqlite:///{DB_PATH}")

def create_db_and_tables():
    print(f"Creating database tables at {DB_PATH}...")
    SQLModel.metadata.create_all(engine)
    print("Tables created.")
