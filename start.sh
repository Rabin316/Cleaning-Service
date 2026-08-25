#!/bin/sh

PORT="${PORT:-8000}"

echo "Starting Django application on port ${PORT}"

exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers 4 \
    --preload \
    config.wsgi:application