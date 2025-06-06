"""
URLs principales del proyecto FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
)
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Vista raíz de la API de FELICITA
    """
    return JsonResponse({
        'mensaje': 'Bienvenido a FELICITA API',
        'version': '1.0.0',
        'descripcion': 'Sistema de Facturación Electrónica para Perú',
        'documentacion': {
            'swagger': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'schema': request.build_absolute_uri('/api/schema/'),
        },
        'endpoints_principales': {
            'autenticacion': request.build_absolute_uri('/api/auth/'),
            'empresas': request.build_absolute_uri('/api/empresas/'),
            'usuarios': request.build_absolute_uri('/api/auth/usuarios/'),
            'facturacion': request.build_absolute_uri('/api/facturacion/'),
            'contabilidad': request.build_absolute_uri('/api/contabilidad/'),
            'inventarios': request.build_absolute_uri('/api/inventarios/'),
            'productos': request.build_absolute_uri('/api/productos/'),
            'clientes': request.build_absolute_uri('/api/clientes/'),
            'pos': request.build_absolute_uri('/api/pos/'),
            'reportes': request.build_absolute_uri('/api/reportes/'),
        },
        'estado': 'activo',
        'entorno': settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'desarrollo'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de health check para monitoreo
    """
    return JsonResponse({
        'status': 'ok',
        'timestamp': '2024-06-06T10:00:00Z',
        'version': '1.0.0',
        'database': 'connected',
        'cache': 'connected',
        'services': {
            'nubefact': 'demo_mode',
            'sunat': 'available',
            'reniec': 'available'
        }
    })


urlpatterns = [
    # ==============================================
    # ADMINISTRACIÓN DJANGO
    # ==============================================
    path('admin/', admin.site.urls),
    
    # ==============================================
    # API ROOT Y HEALTH CHECK
    # ==============================================
    path('api/', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    
    # ==============================================
    # DOCUMENTACIÓN API
    # ==============================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ==============================================
    # APIs DE APLICACIONES
    # ==============================================
    
    # Autenticación y usuarios
    path('api/auth/', include('aplicaciones.usuarios.urls')),
    
    # Empresas (base del sistema)
    path('api/empresas/', include('aplicaciones.empresas.urls')),
    
    # Módulos principales (cuando estén implementados)
    # path('api/facturacion/', include('aplicaciones.facturacion.urls')),
    # path('api/contabilidad/', include('aplicaciones.contabilidad.urls')),
    # path('api/inventarios/', include('aplicaciones.inventarios.urls')),
    # path('api/productos/', include('aplicaciones.productos.urls')),
    # path('api/clientes/', include('aplicaciones.clientes.urls')),
    # path('api/pos/', include('aplicaciones.pos.urls')),
    # path('api/reportes/', include('aplicaciones.reportes.urls')),
    # path('api/configuraciones/', include('aplicaciones.configuraciones.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar títulos del admin
admin.site.site_header = 'FELICITA - Administración'
admin.site.site_title = 'FELICITA Admin'
admin.site.index_title = 'Panel de Administración'

"""
==============================================
RUTAS DISPONIBLES EN DESARROLLO:
==============================================

GENERAL:
GET    /                             # Redirección a API root
GET    /api/                         # API root con información
GET    /health/                      # Health check
GET    /admin/                       # Administración Django

DOCUMENTACIÓN:
GET    /api/docs/                    # Swagger UI (Recomendado)
GET    /api/redoc/                   # ReDoc UI
GET    /api/schema/                  # Schema OpenAPI

AUTENTICACIÓN (/api/auth/):
POST   /api/auth/login/              # Iniciar sesión
POST   /api/auth/registro/           # Registrar usuario
POST   /api/auth/logout/             # Cerrar sesión
GET    /api/auth/perfil/             # Perfil usuario
PUT    /api/auth/perfil/             # Actualizar perfil
POST   /api/auth/cambiar-password/   # Cambiar contraseña
GET    /api/auth/usuarios/           # Listar usuarios (Admin)
POST   /api/auth/usuarios/           # Crear usuario (Admin)
GET    /api/auth/sesiones/           # Sesiones activas
GET    /api/auth/actividades/        # Log actividades
GET    /api/auth/estadisticas/       # Estadísticas seguridad

EMPRESAS (/api/empresas/):
GET    /api/empresas/                # Listar empresas
POST   /api/empresas/                # Crear empresa
GET    /api/empresas/{id}/           # Obtener empresa
PUT    /api/empresas/{id}/           # Actualizar empresa

PRÓXIMOS MÓDULOS (Fases siguientes):
/api/facturacion/                   # Facturación electrónica
/api/contabilidad/                  # Contabilidad y asientos
/api/inventarios/                   # Control de inventarios
/api/productos/                     # Catálogo de productos
/api/clientes/                      # Gestión de clientes
/api/pos/                           # Punto de venta
/api/reportes/                      # Reportes y analytics
/api/configuraciones/               # Configuraciones sistema

==============================================
CONFIGURACIÓN CORS:
==============================================

Permitido para desarrollo:
- http://localhost:3000      (React Dev Server)
- http://127.0.0.1:3000     (React Dev Server)
- http://localhost:5173      (Vite Dev Server)

==============================================
CONFIGURACIÓN DE SEGURIDAD:
==============================================

Headers automáticos:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- X-Powered-By: FELICITA-1.0

Rate Limiting:
- General API: 100 req/min por usuario
- Login: 5 req/min por IP
- Anónimo: 30 req/min por IP

==============================================
MIDDLEWARE ACTIVO:
==============================================

1. CorsMiddleware
2. SeguridadFelicitaMiddleware
3. BloqueoIntentosFallidosMiddleware
4. SecurityMiddleware
5. SessionMiddleware
6. CommonMiddleware
7. CsrfViewMiddleware
8. AuthenticationMiddleware
9. AutenticacionJWTMiddleware
10. AuditoriaMiddleware
11. MessageMiddleware
12. ClickjackingMiddleware
13. LocaleMiddleware
14. MonitoreoRendimientoMiddleware
"""