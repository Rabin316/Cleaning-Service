# Dockerfile for Clean Pro - Production-Ready Django Application
FROM python:3.12-slim

# Set work directory
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

# Create required directories
RUN mkdir -p /app/logs /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

# Copy project
COPY . .

# Ensure appuser owns application files
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

# Run Gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --preload config.wsgi:application"]