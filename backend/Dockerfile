FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (includes static/ with built React frontend)
COPY . .

# Expose port
EXPOSE 8000

# Default port (Railway provides $PORT)
ENV PORT=8000

# Run application - use shell form so $PORT is expanded
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
