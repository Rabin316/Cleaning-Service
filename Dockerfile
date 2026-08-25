# Dockerfile for Clean Pro - Django + Railway

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        make \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r appuser \
    && useradd -r -g appuser appuser

# Copy Django project
COPY . .

# Create required directories
RUN mkdir -p /app/logs \
    /app/staticfiles \
    /app/media \
    && chown -R appuser:appuser /app

# Use non-root user
USER appuser

# Default port
EXPOSE 8000

# Start Django with Gunicorn
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120"]