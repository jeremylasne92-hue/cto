from fastapi import FastAPI
import lancedb
from db import create_db_and_tables, APP_DATA_DIR, DB_PATH, LANCEDB_PATH

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Initialize LanceDB
    # db = lancedb.connect(str(LANCEDB_PATH)) # Commented out to avoid unused var warning if logic not present yet
    lancedb.connect(str(LANCEDB_PATH))
    print(f"Backend started. Data directory: {APP_DATA_DIR}")

@app.get("/")
def read_root():
    return {"message": "Cognisphere Backend Running"}

@app.get("/status")
def status():
    return {"status": "ok", "db_path": str(DB_PATH)}

# Hardware Detection Placeholder
@app.get("/hardware")
def get_hardware_info():
    # TODO: Implement real hardware detection
    return {
        "cpu": "Unknown",
        "gpu": "Unknown",
        "ram": "Unknown",
        "accelerator": "None"
    }

@app.post("/models/download")
def download_model(model_id: str):
    """
    Lazy download model to the app data directory.
    """
    model_path = APP_DATA_DIR / "models" / model_id
    if model_path.exists():
        return {"status": "exists", "path": str(model_path)}
    
    # Placeholder for download logic
    # e.g. requests.get(url, stream=True)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "w") as f:
        f.write("dummy model content")
        
    return {"status": "downloaded", "path": str(model_path)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
