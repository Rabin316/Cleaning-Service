FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        make \
        libpq-dev \
        postgresql-client \
        libjpeg-dev \
        zlib1g-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Non-root user
RUN groupadd -r appuser \
    && useradd -r -g appuser appuser

# Copy project
COPY . .

# Required directories
RUN mkdir -p /app/logs /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Start Django
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120"]