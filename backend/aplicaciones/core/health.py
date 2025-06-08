"""
HEALTH CHECK - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Endpoint de verificación de salud del sistema
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import connection
import redis
from django.conf import settings


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Endpoint de health check para verificar el estado del sistema
    """
    try:
        # Verificar base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Verificar Redis (opcional)
    redis_status = "not_configured"
    try:
        if hasattr(settings, 'REDIS_URL'):
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            redis_status = "healthy"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    # Estado general
    is_healthy = db_status == "healthy"
    
    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": timezone.now().isoformat(),
        "service": "felicita-backend",
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "redis": redis_status,
        }
    }
    
    status_code = 200 if is_healthy else 503
    
    return JsonResponse(response_data, status=status_code)