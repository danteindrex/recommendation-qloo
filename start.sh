#!/bin/bash

echo "🌟 Starting CulturalOS Demo Services..."
echo "====================================="

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY environment variable is not set!"
    echo "Please set your Gemini API key in the .env file or environment."
    exit 1
fi

echo "✅ Gemini API key configured"

# Start FastAPI backend in the background
echo "🚀 Starting FastAPI Backend (port 8000)..."
cd /app
python demo_main.py &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 5

# Check if FastAPI started successfully
if ! kill -0 $FASTAPI_PID 2>/dev/null; then
    echo "❌ FastAPI failed to start!"
    exit 1
fi

echo "✅ FastAPI Backend started successfully"

# Start Streamlit demo
echo "📊 Starting Streamlit Demo (port 8501)..."
streamlit run streamlit_demo.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &
STREAMLIT_PID=$!

# Wait a moment for Streamlit to start
sleep 5

echo "✅ Streamlit Demo started successfully"
echo ""
echo "🎉 CulturalOS Demo is ready!"
echo "=========================="
echo "📊 Streamlit Demo: http://localhost:8501"
echo "🔗 API Documentation: http://localhost:8000/docs"
echo "❤️ Health Check: http://localhost:8000/health"
echo ""

# Keep the script running and monitor both processes
wait_for_process() {
    while kill -0 "$1" 2>/dev/null; do
        sleep 1
    done
}

echo "🔄 Monitoring services..."

# Wait for either process to exit
(wait_for_process $FASTAPI_PID; echo "FastAPI exited") &
(wait_for_process $STREAMLIT_PID; echo "Streamlit exited") &

wait -n

echo "❌ One of the services stopped unexpectedly!"
echo "Shutting down..."

# Kill remaining processes
kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null

exit 1