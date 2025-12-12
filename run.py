#!/usr/bin/env python3
"""
Main entry point for the flashcard sync engine backend
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == '__main__':
    from backend.app import create_app
    
    app = create_app('development')
    
    print("🚀 Flashcard Sync Engine Backend Starting...")
    print("📍 Server will be available at: http://localhost:5000")
    print("📖 Health check: http://localhost:5000/health")
    print("🏁 Press Ctrl+C to stop the server")
    print("")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )