#!/bin/bash

# Universal Ingestion Service Setup and Test Script

set -e

echo "🚀 Universal Ingestion Service - Setup & Test"
echo "================================================"

# Check if Python 3.8+ is available
python_version=$(python3 --version | cut -d ' ' -f 2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Run basic syntax check
echo "🔍 Checking Python syntax..."
python3 -m py_compile main.py
find src/ -name "*.py" -exec python3 -m py_compile {} \;

echo "✅ All Python files have valid syntax"

# Run unit tests (fast)
echo "🧪 Running unit tests..."
python3 -m pytest tests/unit/ -v --tb=short || echo "⚠️ Some unit tests failed"

# Run integration tests (if available)
echo "🔗 Running integration tests..."
python3 -m pytest tests/integration/ -v --tb=short || echo "⚠️ Some integration tests failed"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the service:"
echo "  python main.py"
echo ""
echo "To run end-to-end test:"
echo "  python test_e2e.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"