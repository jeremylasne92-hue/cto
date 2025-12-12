#!/bin/bash

# Flashcard Sync Engine - Backend Startup Script

set -e

echo "🚀 Starting Flashcard Sync Engine Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python scripts/init_db.py init

# Start the server
echo "🌐 Starting Flask server on http://localhost:5000"
echo "📖 API Documentation available at http://localhost:5000/health"
echo "🏁 Press Ctrl+C to stop the server"
echo ""

export FLASK_APP=backend.app
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000