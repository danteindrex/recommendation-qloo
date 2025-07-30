#!/bin/bash

echo "🌍 CulturalOS Docker Deployment"
echo "==============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it with your Gemini API key."
    echo "Example:"
    echo "GEMINI_API_KEY=your_api_key_here"
    exit 1
fi

# Build the Docker image
echo "🔨 Building CulturalOS Docker image..."
docker build -t culturalus-demo:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully!"

# Stop any existing container
echo "🛑 Stopping existing containers..."
docker stop culturalus-api-demo 2>/dev/null || true
docker rm culturalus-api-demo 2>/dev/null || true

# Run the container
echo "🚀 Starting CulturalOS Demo..."
docker run -d \
    --name culturalus-api-demo \
    -p 8000:8000 \
    -p 8501:8501 \
    --env-file .env \
    culturalus-demo:latest

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container!"
    exit 1
fi

echo ""
echo "🎉 CulturalOS Demo is starting up!"
echo "=================================="
echo ""
echo "📊 Streamlit Demo: http://localhost:8501"
echo "🔗 API Documentation: http://localhost:8000/docs"
echo "❤️ Health Check: http://localhost:8000/health"
echo ""
echo "⏳ Please wait 30-60 seconds for services to start..."
echo ""
echo "🐳 Container Logs:"
echo "docker logs -f culturalus-api-demo"
echo ""
echo "🛑 To stop:"
echo "docker stop culturalus-api-demo"

# Wait a bit and check if it's running
sleep 5
if docker ps | grep -q culturalus-api-demo; then
    echo "✅ Container is running!"
else
    echo "❌ Container failed to start. Check logs:"
    echo "docker logs culturalus-api-demo"
fi