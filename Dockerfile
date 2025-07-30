# Multi-stage Dockerfile for CulturalOS API + Streamlit Demo
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt /app/backend_requirements.txt
COPY requirements.txt /app/streamlit_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend_requirements.txt
RUN pip install --no-cache-dir -r streamlit_requirements.txt

# Copy backend application
COPY backend/ /app/backend/

# Copy demo files
COPY streamlit_demo.py /app/
COPY demo_main.py /app/
COPY start.sh /app/
COPY DEMO_README.md /app/
COPY PROJECT_SUBMISSION.md /app/

# Copy environment template
COPY .env /app/.env

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start both services
CMD ["/app/start.sh"]