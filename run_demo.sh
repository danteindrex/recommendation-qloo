#!/bin/bash

echo "🌍 CulturalOS API Demo Setup"
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Install Streamlit requirements
echo "📦 Installing Streamlit requirements..."
source venv/bin/activate && pip install -r streamlit_requirements.txt

# Check if API is running
echo "🔍 Checking if API is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running on http://localhost:8000"
else
    echo "⚠️  API is not running. Please start the API first:"
    echo "   cd backend && python main.py"
    echo ""
    echo "💡 You can still run the demo, but some features will show connection errors."
fi

echo ""
echo "🚀 Starting Streamlit Demo..."
echo "📊 Demo will be available at: http://localhost:8501"
echo ""
echo "🎯 For Judges:"
echo "   1. Open http://localhost:8501 in your browser"
echo "   2. Navigate through different sections using the sidebar"
echo "   3. Test all API endpoints interactively"
echo "   4. View live AI responses from Google Gemini"
echo ""

# Start Streamlit
source venv/bin/activate && streamlit run streamlit_demo.py --server.port 8501 --server.address 0.0.0.0