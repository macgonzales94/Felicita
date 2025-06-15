"""
FELICITA - URLs Principal
Sistema de Facturación Electrónica para Perú

Configuración principal de URLs del proyecto
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
import logging

logger = logging.getLogger('felicita')

def api_root_view(request):
    """Vista raíz de la API con información del sistema"""
    return JsonResponse({
        'mensaje': '¡Bienvenido a FELICITA API!',
        'descripcion': 'Sistema de Facturación Electrónica para Perú',
        'version': '1.0.0',
        'ambiente': getattr(settings, 'ENVIRONMENT', 'desconocido'),
        'documentacion': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'schema': '/api/schema/',
        },
        'endpoints': {
            'autenticacion': '/api/auth/',
            'usuarios': '/api/usuarios/',
            'core': '/api/core/',
            'facturacion': '/api/facturacion/',
            'inventario': '/api/inventario/',
            'clientes': '/api/clientes/',
            'productos': '/api/productos/',
            'punto_venta': '/api/punto-venta/',
            'reportes': '/api/reportes/',
            'contabilidad': '/api/contabilidad/',
            'integraciones': '/api/integraciones/',
        },
        'soporte': {
            'email': 'soporte@felicita.pe',
            'documentacion': 'https://docs.felicita.pe',
            'github': 'https://github.com/macgonzales94/felicita',
        }
    })

def health_check_view(request):
    """Health check endpoint para monitoreo"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=503)

# ===========================================
# PATRONES DE URL PRINCIPALES
# ===========================================

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', health_check_view, name='health_check'),
    
    # API Root
    path('api/', api_root_view, name='api_root'),
    
    # Documentación API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # APIs de aplicaciones
    path('api/auth/', include('aplicaciones.usuarios.urls')),
    path('api/usuarios/', include('aplicaciones.usuarios.urls')),
    path('api/core/', include('aplicaciones.core.urls')),
    path('api/facturacion/', include('aplicaciones.facturacion.urls')),
    path('api/inventario/', include('aplicaciones.inventario.urls')),
    path('api/punto-venta/', include('aplicaciones.punto_venta.urls')),
    path('api/reportes/', include('aplicaciones.reportes.urls')),
    path('api/contabilidad/', include('aplicaciones.contabilidad.urls')),
    path('api/integraciones/', include('aplicaciones.integraciones.urls')),
]

# ===========================================
# CONFIGURACIÓN SEGÚN AMBIENTE
# ===========================================

# URLs para desarrollo
if settings.DEBUG:
    import debug_toolbar
    
    urlpatterns += [
        # Debug toolbar
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    
    # Servir archivos media en desarrollo
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )
    
    # Servir archivos estáticos en desarrollo
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=settings.STATIC_ROOT
    )
    
    logger.info("🔧 URLs de desarrollo cargadas")

# URLs para producción
else:
    # Redirigir root a documentación en producción
    urlpatterns += [
        path('', TemplateView.as_view(
            template_name='index.html',
            extra_context={
                'title': 'FELICITA API',
                'description': 'Sistema de Facturación Electrónica para Perú'
            }
        ), name='root'),
    ]

# ===========================================
# MANEJO DE ERRORES
# ===========================================

from django.views.defaults import (
    bad_request, 
    permission_denied, 
    page_not_found, 
    server_error
)

# Views de error personalizadas
def custom_400_view(request, exception=None):
    """Vista personalizada para error 400"""
    return JsonResponse({
        'error': 'Bad Request',
        'message': 'La solicitud no pudo ser procesada debido a un error del cliente.',
        'status_code': 400,
        'timestamp': timezone.now().isoformat(),
    }, status=400)

def custom_403_view(request, exception=None):
    """Vista personalizada para error 403"""
    return JsonResponse({
        'error': 'Forbidden',
        'message': 'No tienes permisos para acceder a este recurso.',
        'status_code': 403,
        'timestamp': timezone.now().isoformat(),
    }, status=403)

def custom_404_view(request, exception=None):
    """Vista personalizada para error 404"""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'El recurso solicitado no fue encontrado.',
        'status_code': 404,
        'timestamp': timezone.now().isoformat(),
    }, status=404)

def custom_500_view(request):
    """Vista personalizada para error 500"""
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'Ocurrió un error interno del servidor.',
        'status_code': 500,
        'timestamp': timezone.now().isoformat(),
    }, status=500)

# Asignar handlers de error personalizados
handler400 = custom_400_view
handler403 = custom_403_view
handler404 = custom_404_view
handler500 = custom_500_view

# ===========================================
# CONFIGURACIÓN ADMIN
# ===========================================

# Personalizar admin site
admin.site.site_header = "FELICITA - Administración"
admin.site.site_title = "FELICITA Admin"
admin.site.index_title = "Panel de Administración FELICITA"

# ===========================================
# LOGGING URLS
# ===========================================

from django.utils import timezone

logger.info("🌐 URLs principales de FELICITA cargadas correctamente")
logger.info(f"📍 Total de patrones URL: {len(urlpatterns)}")
logger.info(f"🔧 Modo DEBUG: {settings.DEBUG}")
logger.info(f"🌍 Ambiente: {getattr(settings, 'ENVIRONMENT', 'desconocido')}")

# ===========================================
# MIDDLEWARE DE LOGGING
# ===========================================

if settings.DEBUG:
    def log_requests_middleware(get_response):
        """Middleware para log de requests en desarrollo"""
        def middleware(request):
            start_time = timezone.now()
            response = get_response(request)
            duration = timezone.now() - start_time
            
            logger.debug(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration.total_seconds():.3f}s"
            )
            
            return response
        return middleware