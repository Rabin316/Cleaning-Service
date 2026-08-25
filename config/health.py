"""
Health check view for the application
"""
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
import logging


logger = logging.getLogger(__name__)


@never_cache
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns a JSON response with status 'healthy' if the app is running correctly.
    """
    from django.db import connection
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        logger.exception('Health check database query failed')
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected'
        }, status=503)

    return JsonResponse({
        'status': 'healthy',
        'database': 'connected',
        'services_ok': True,
    })