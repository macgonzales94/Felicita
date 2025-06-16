"""
FELICITA - URLs Principales
Sistema de Facturación Electrónica para Perú

Configuración principal de URLs con todas las rutas del sistema
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
import logging

logger = logging.getLogger('felicita')

# ===========================================
# VISTAS DE SALUD DEL SISTEMA
# ===========================================

@require_http_methods(["GET"])
def health_check(request):
    """Health check básico para monitoreo"""
    return JsonResponse({
        'status': 'ok',
        'service': 'FELICITA',
        'version': '1.0.0',
        'environment': 'development' if settings.DEBUG else 'production'
    })

@require_http_methods(["GET"])
def health_detailed(request):
    """Health check detallado para monitoreo avanzado"""
    from django.db import connection
    from django.core.cache import cache
    import time
    
    health_data = {
        'status': 'ok',
        'timestamp': time.time(),
        'service': 'FELICITA',
        'version': '1.0.0',
        'environment': 'development' if settings.DEBUG else 'production',
        'checks': {}
    }
    
    # Verificar base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data['checks']['database'] = 'ok'
    except Exception as e:
        health_data['checks']['database'] = f'error: {str(e)}'
        health_data['status'] = 'error'
    
    # Verificar cache
    try:
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            health_data['checks']['cache'] = 'ok'
        else:
            health_data['checks']['cache'] = 'error: cache not working'
            health_data['status'] = 'error'
    except Exception as e:
        health_data['checks']['cache'] = f'error: {str(e)}'
        health_data['status'] = 'error'
    
    # Verificar sistema de archivos
    try:
        import os
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=True) as f:
            f.write(b'health check')
            f.flush()
            health_data['checks']['filesystem'] = 'ok'
    except Exception as e:
        health_data['checks']['filesystem'] = f'error: {str(e)}'
        health_data['status'] = 'error'
    
    status_code = 200 if health_data['status'] == 'ok' else 503
    return JsonResponse(health_data, status=status_code)

@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """Readiness check para Kubernetes/Docker"""
    from django.db import connection
    
    try:
        # Verificar que la base de datos esté lista
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            
        return JsonResponse({
            'status': 'ready',
            'service': 'FELICITA',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'service': 'FELICITA',
            'database': f'error: {str(e)}'
        }, status=503)

@csrf_exempt
@require_http_methods(["GET"])
def liveness_check(request):
    """Liveness check para Kubernetes/Docker"""
    return JsonResponse({
        'status': 'alive',
        'service': 'FELICITA'
    })

# ===========================================
# VISTA DE INFORMACIÓN DEL SISTEMA
# ===========================================

@require_http_methods(["GET"])
def system_info(request):
    """Información básica del sistema (solo para admins)"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    import sys
    import django
    import platform
    from django.db import connection
    
    return JsonResponse({
        'felicita_version': '1.0.0',
        'django_version': django.get_version(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'database': {
            'vendor': connection.vendor,
            'version': connection.mysql_version if hasattr(connection, 'mysql_version') else 'unknown'
        },
        'debug': settings.DEBUG,
        'environment': 'development' if settings.DEBUG else 'production'
    })

# ===========================================
# PATRONES DE URL PRINCIPALES
# ===========================================

urlpatterns = [
    # ===========================================
    # ADMIN DJANGO
    # ===========================================
    path('admin/', admin.site.urls),
    
    # ===========================================
    # HEALTH CHECKS
    # ===========================================
    path('health/', health_check, name='health_check'),
    path('health/detailed/', health_detailed, name='health_detailed'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),
    path('system/info/', system_info, name='system_info'),
    
    # ===========================================
    # API DOCUMENTATION
    # ===========================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ===========================================
    # APIs PRINCIPALES
    # ===========================================
    
    # API de Usuarios y Autenticación
    path('api/usuarios/', include('aplicaciones.usuarios.urls')),
    
    # API de Core (Empresas, Sucursales, Clientes, etc.)
    path('api/core/', include('aplicaciones.core.urls')),
    
    # API de Facturación
    path('api/facturacion/', include('aplicaciones.facturacion.urls')),
    
    # API de Inventario
    path('api/inventario/', include('aplicaciones.inventario.urls')),
    
    # API de Contabilidad
    path('api/contabilidad/', include('aplicaciones.contabilidad.urls')),
    
    # API de Punto de Venta
    path('api/punto-venta/', include('aplicaciones.punto_venta.urls')),
    
    # API de Reportes
    path('api/reportes/', include('aplicaciones.reportes.urls')),
    
    # API de Integraciones
    path('api/integraciones/', include('aplicaciones.integraciones.urls')),
]

# ===========================================
# CONFIGURACIÓN SEGÚN AMBIENTE
# ===========================================

# URLs para archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Herramientas de desarrollo
    if 'django_extensions' in settings.INSTALLED_APPS:
        try:
            import debug_toolbar
            urlpatterns += [
                path('__debug__/', include(debug_toolbar.urls)),
            ]
        except ImportError:
            pass

# ===========================================
# CONFIGURACIÓN DEL ADMIN
# ===========================================

# Personalización del admin
admin.site.site_header = 'FELICITA - Administración'
admin.site.site_title = 'FELICITA Admin'
admin.site.index_title = 'Panel de Administración'

# ===========================================
# HANDLERS DE ERROR PERSONALIZADOS
# ===========================================

def handler404(request, exception):
    """Handler personalizado para error 404"""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Recurso no encontrado',
            'detail': 'La URL solicitada no existe',
            'status_code': 404
        }, status=404)
    else:
        # Para requests no-API, podrías servir una página 404 personalizada
        from django.shortcuts import render
        return render(request, '404.html', status=404)

def handler500(request):
    """Handler personalizado para error 500"""
    logger.error(f"Error 500 en {request.path}", exc_info=True)
    
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Error interno del servidor',
            'detail': 'Ha ocurrido un error inesperado',
            'status_code': 500
        }, status=500)
    else:
        from django.shortcuts import render
        return render(request, '500.html', status=500)

def handler403(request, exception):
    """Handler personalizado para error 403"""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Acceso denegado',
            'detail': 'No tiene permisos para acceder a este recurso',
            'status_code': 403
        }, status=403)
    else:
        from django.shortcuts import render
        return render(request, '403.html', status=403)

def handler400(request, exception):
    """Handler personalizado para error 400"""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Petición incorrecta',
            'detail': 'Los datos enviados no son válidos',
            'status_code': 400
        }, status=400)
    else:
        from django.shortcuts import render
        return render(request, '400.html', status=400)

# ===========================================
# CONFIGURACIÓN DE URLS DE DESARROLLO
# ===========================================

if settings.DEBUG:
    # URLs adicionales para desarrollo
    from django.views.generic import TemplateView
    
    development_patterns = [
        # Página de prueba para email templates
        path('dev/email-test/', TemplateView.as_view(template_name='emails/test.html'), name='email_test'),
        
        # Endpoint para limpiar cache en desarrollo
        path('dev/clear-cache/', 
             lambda request: JsonResponse({'status': 'Cache cleared'}) if request.user.is_superuser else JsonResponse({'error': 'Forbidden'}, status=403),
             name='clear_cache'),
    ]
    
    urlpatterns += development_patterns

# ===========================================
# MIDDLEWARE DE LOGS
# ===========================================

class URLLoggingMiddleware:
    """Middleware para loguear todas las URLs accedidas"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log de la petición entrante (solo en desarrollo)
        if settings.DEBUG:
            logger.debug(f"Request: {request.method} {request.path}")
        
        response = self.get_response(request)
        
        # Log de la respuesta (solo errores en producción)
        if settings.DEBUG or response.status_code >= 400:
            logger.info(f"Response: {request.method} {request.path} -> {response.status_code}")
        
        return response

# ===========================================
# CONFIGURACIÓN FINAL
# ===========================================

# Asegurarse de que los handlers están configurados
handler404 = 'config.urls.handler404'
handler500 = 'config.urls.handler500'
handler403 = 'config.urls.handler403'
handler400 = 'config.urls.handler400'

# Log de inicio del sistema
logger.info("🚀 FELICITA URLs configuradas correctamente")
logger.info(f"🐛 DEBUG mode: {settings.DEBUG}")
logger.info(f"📡 Total URLs registradas: {len(urlpatterns)}")

if settings.DEBUG:
    logger.debug("📝 URLs de desarrollo habilitadas:")
    logger.debug("   - /api/docs/ - Documentación Swagger")
    logger.debug("   - /api/redoc/ - Documentación ReDoc")
    logger.debug("   - /health/ - Health checks")
    logger.debug("   - /admin/ - Panel de administración")
    logger.debug("   - /dev/ - Herramientas de desarrollo")