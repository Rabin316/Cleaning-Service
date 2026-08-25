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
RUN groupadd -r appuser && useradd -r -gp appuser appuser

# Create logs directory
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Copy project
COPY . .

# Create staticfiles directory
RUN mkdir -p /app/staticfiles /app/media

# Make appuser the owner of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--preload", "config.wsgi:application"]

# Production notes:
# - Set environment variables via Docker compose or environment
# - Use proper secrets management (not hardcoded env vars)
# - Consider using a production database (PostgreSQL/MySQL)
# - Set up proper logging and monitoring
# - Use HTTPS termination at the load balancer/reverse proxy level