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

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r appuser \
    && useradd -r -g appuser appuser

# Copy Django project
COPY . .

# Create required directories
RUN mkdir -p /app/logs /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Railway assigns the actual port at runtime
EXPOSE 8000

# Start Gunicorn
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --preload config.wsgi:application"]