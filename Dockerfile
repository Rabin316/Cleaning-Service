# Dockerfile for Clean Pro - Railway Production

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

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r appuser \
    && useradd -r -g appuser appuser

# Create application directories
RUN mkdir -p /app/logs \
    /app/staticfiles \
    /app/media

# Copy application
COPY . .

# Copy startup script
COPY start.sh /app/start.sh

# Set permissions
RUN chmod +x /app/start.sh \
    && chown -R appuser:appuser /app

# Use non-root user
USER appuser

# Default port
EXPOSE 8000

# Start application
CMD ["/app/start.sh"]