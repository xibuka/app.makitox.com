#!/bin/bash
# Makitox Platform Launcher Script
# Run from project root directory

set -e  # Exit on any error

echo "🚀 Makitox Platform Launcher"
echo "=================================="
echo "💻 Optimized for Mac & Linux"

# Check if we're in the right directory
if [[ ! -f "index.html" ]]; then
    echo "❌ Error: index.html not found"
    echo "💡 Please run this script from the project root directory"
    echo "💡 The directory should contain: index.html, api/, etc."
    exit 1
fi

if [[ ! -d "api" ]]; then
    echo "❌ Error: api/ directory not found"
    echo "💡 Make sure the api directory exists"
    exit 1
fi

echo "✅ Project structure verified"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found"
    echo "💡 Please install Python 3.7+ to run Makitox"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "✅ Python found: $PYTHON_CMD"

# Check if virtual environment exists, create if not
if [[ ! -d "api/venv" ]]; then
    echo "📦 Creating virtual environment..."
    cd api
    $PYTHON_CMD -m venv venv
    cd ..
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing/updating dependencies..."
source api/venv/bin/activate

# Install requirements
pip install -r api/requirements.txt > /dev/null 2>&1

echo "✅ Dependencies ready"
echo ""

# Start the server
echo "🌟 Starting Makitox unified server..."
echo "📍 Website: http://localhost:8000"
echo "📍 API: http://localhost:8000/api"
echo "📍 Status: http://localhost:8000/api/status"
echo "📍 Gold Prices: http://localhost:8000/api/gold-prices/yearly"
echo "=================================="
echo "💡 Press Ctrl+C to stop the server"
echo ""

# Run the server using the root-level launcher
$PYTHON_CMD server.py