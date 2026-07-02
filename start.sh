#!/bin/bash

# AI Video Creator Agent - Startup Script

echo "🎬 AI Video Creator Agent"
echo "=========================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install backend dependencies if needed
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    python3 -m venv "$BACKEND_DIR/venv"
    source "$BACKEND_DIR/venv/bin/activate"
    pip install -q -r "$BACKEND_DIR/requirements.txt"
else
    source "$BACKEND_DIR/venv/bin/activate"
fi

# Check if .env exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    echo "📝 Please edit $BACKEND_DIR/.env and add your API keys."
fi

# Start the backend server
echo "🚀 Starting backend server..."
cd "$BACKEND_DIR"
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend server started on http://localhost:8000"
else
    echo "❌ Backend server failed to start. Check logs for errors."
    exit 1
fi

echo ""
echo "🎉 AI Video Creator Agent is ready!"
echo "   Frontend: http://localhost:8000 (or use a separate web server)"
echo "   API:      http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server."

# Wait for interrupt
wait $BACKEND_PID
