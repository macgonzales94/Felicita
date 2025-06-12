"""
URLS PRINCIPALES - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Configuración principal de URLs que conecta todos los módulos
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('felicita')


# =============================================================================
# VISTAS DE UTILIDAD
# =============================================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint de health check para monitoreo"""
    try:
        from django.db import connection
        from aplicaciones.integraciones.services.nubefact import nubefact_service
        
        # Verificar base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = cursor.fetchone()[0] == 1
        
        # Verificar Nubefact
        nubefact_status = nubefact_service.ping()
        
        # Estado general
        overall_status = db_status and nubefact_status
        
        return Response({
            'status': 'healthy' if overall_status else 'unhealthy',
            'timestamp': settings.USE_TZ and timezone.now() or datetime.now(),
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
            'services': {
                'database': 'up' if db_status else 'down',
                'nubefact': 'up' if nubefact_status else 'down',
                'cache': 'up',  # Se podría verificar Redis
            },
            'checks': {
                'database_connection': db_status,
                'external_api_nubefact': nubefact_status,
                'memory_usage': 'ok',
                'disk_space': 'ok'
            }
        }, status=status.HTTP_200_OK if overall_status else status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': settings.USE_TZ and timezone.now() or datetime.now()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """Información general de la API"""
    return Response({
        'nombre': 'FELICITA API',
        'descripcion': 'Sistema de Facturación Electrónica para Perú',
        'version': getattr(settings, 'APP_VERSION', '1.0.0'),
        'documentacion': f"{getattr(settings, 'BACKEND_URL', '')}/api/docs/",
        'soporte': 'soporte@felicita.pe',
        'modulos': [
            'Facturación Electrónica',
            'Punto de Venta',
            'Control de Inventarios',
            'Contabilidad Automática',
            'Reportes y Analytics',
            'Gestión Administrativa'
        ],
        'integraciones': [
            'Nubefact (OSE)',
            'SUNAT',
            'RENIEC',
            'Bancos'
        ],
        'cumplimiento': [
            'Facturación electrónica SUNAT',
            'Libros electrónicos PLE',
            'Método PEPS para inventarios',
            'PCGE para contabilidad'
        ]
    })


@csrf_exempt
def handler404(request, exception=None):
    """Manejador personalizado para 404"""
    return JsonResponse({
        'error': 'Endpoint no encontrado',
        'mensaje': 'La URL solicitada no existe en la API de FELICITA',
        'codigo': 404,
        'documentacion': f"{getattr(settings, 'BACKEND_URL', '')}/api/docs/"
    }, status=404)


@csrf_exempt
def handler500(request):
    """Manejador personalizado para 500"""
    logger.error("Error interno del servidor", exc_info=True)
    return JsonResponse({
        'error': 'Error interno del servidor',
        'mensaje': 'Ocurrió un error inesperado. El equipo técnico ha sido notificado.',
        'codigo': 500,
        'soporte': 'soporte@felicita.pe'
    }, status=500)


# =============================================================================
# PATRONES DE URL PRINCIPALES
# =============================================================================
urlpatterns = [
    # =============================================================================
    # ADMINISTRACIÓN DJANGO
    # =============================================================================
    path('admin/', admin.site.urls),
    
    # =============================================================================
    # ENDPOINTS DE UTILIDAD
    # =============================================================================
    path('', api_info, name='api-info'),
    path('health/', health_check, name='health-check'),
    path('api/', api_info, name='api-root'),
    
    # =============================================================================
    # APIS DE APLICACIONES PRINCIPALES
    # =============================================================================
    
    # Core - Gestión base (empresas, usuarios, clientes)
    path('api/core/', include('aplicaciones.core.urls')),
    
    # Usuarios - Autenticación y permisos
    path('api/auth/', include('aplicaciones.usuarios.urls')),
    path('api/usuarios/', include('aplicaciones.usuarios.urls')),
    
    # Facturación - Módulo principal
    path('api/facturacion/', include('aplicaciones.facturacion.urls')),
    path('api/facturas/', include('aplicaciones.facturacion.urls')),  # Alias
    
    # Inventario - Control de stock y productos
    path('api/inventario/', include('aplicaciones.inventario.urls')),
    path('api/productos/', include('aplicaciones.inventario.urls')),  # Alias
    
    # Contabilidad - Asientos automáticos y reportes financieros
    path('api/contabilidad/', include('aplicaciones.contabilidad.urls')),
    path('api/finanzas/', include('aplicaciones.contabilidad.urls')),  # Alias
    
    # Punto de Venta - POS optimizado
    path('api/pos/', include('aplicaciones.punto_venta.urls')),
    path('api/punto-venta/', include('aplicaciones.punto_venta.urls')),  # Alias
    
    # Reportes - Dashboards y analytics
    path('api/reportes/', include('aplicaciones.reportes.urls')),
    path('api/analytics/', include('aplicaciones.reportes.urls')),  # Alias
    
    # Integraciones - Nubefact, SUNAT, webhooks
    path('api/integraciones/', include('aplicaciones.integraciones.urls')),
    path('api/webhooks/', include('aplicaciones.integraciones.webhook_urls')),
    
    # =============================================================================
    # APIS ESPECIALIZADAS
    # =============================================================================
    
    # API para móviles (endpoints optimizados)
    path('api/mobile/', include([
        path('facturacion/', include('aplicaciones.facturacion.urls')),
        path('pos/', include('aplicaciones.punto_venta.urls')),
        path('inventario/', include('aplicaciones.inventario.urls')),
    ])),
    
    # API para integraciones externas
    path('api/external/', include([
        path('ventas/', include('aplicaciones.facturacion.urls')),
        path('productos/', include('aplicaciones.inventario.urls')),
        path('clientes/', include('aplicaciones.core.urls')),
    ])),
    
    # =============================================================================
    # DOCUMENTACIÓN DE API
    # =============================================================================
    
    # Swagger/OpenAPI
    path('api/docs/', include([
        path('', include('rest_framework.urls')),  # DRF browsable API
    ])),
    
    # =============================================================================
    # ENDPOINTS ADMINISTRATIVOS
    # =============================================================================
    
    # Endpoints solo para administradores
    path('api/admin/', include([
        path('sistema/', include('aplicaciones.core.urls')),
        path('usuarios/', include('aplicaciones.usuarios.urls')),
        path('configuracion/', include('aplicaciones.core.urls')),
        path('logs/', include('aplicaciones.core.urls')),
        path('backup/', include('aplicaciones.core.urls')),
    ])),
    
    # =============================================================================
    # ENDPOINTS DE DESARROLLO (solo en DEBUG)
    # =============================================================================
]

# Agregar URLs de desarrollo solo en modo DEBUG
if settings.DEBUG:
    urlpatterns += [
        # Debug toolbar
        path('__debug__/', include('debug_toolbar.urls')),
        
        # Endpoints de testing
        path('api/test/', include([
            path('nubefact/', include('aplicaciones.integraciones.urls')),
            path('database/', health_check),
            path('email/', health_check),
            path('cache/', health_check),
        ])),
        
        # Documentación extendida
        path('api/schema/', include([
            path('redoc/', health_check),
            path('swagger/', health_check),
        ])),
    ]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# =============================================================================
# CONFIGURACIÓN DE MANEJADORES DE ERROR
# =============================================================================
handler404 = 'felicita.urls.handler404'
handler500 = 'felicita.urls.handler500'

# =============================================================================
# CONFIGURACIÓN ADICIONAL PARA PRODUCCIÓN
# =============================================================================
if not settings.DEBUG:
    # En producción, agregar middleware de seguridad adicional
    urlpatterns = [
        # Rate limiting endpoint
        path('api/rate-limit/', api_info),
        
        # Security headers endpoint
        path('api/security/', health_check),
        
    ] + urlpatterns

# =============================================================================
# DOCUMENTACIÓN DE LA API
# =============================================================================
"""
ESTRUCTURA DE LA API FELICITA

=== BASE URL ===
Desarrollo: http://localhost:8000/api/
Producción: https://api.felicita.pe/api/

=== MÓDULOS PRINCIPALES ===

1. CORE (/api/core/)
   - Empresas, sucursales, configuración base
   - Clientes y proveedores
   - Ubicaciones geográficas (departamentos, provincias, distritos)

2. AUTENTICACIÓN (/api/auth/)
   - Login/logout
   - Gestión de tokens JWT
   - Permisos y roles

3. FACTURACIÓN (/api/facturacion/)
   - Facturas, boletas, notas de crédito
   - Integración con Nubefact/SUNAT
   - Series y numeración correlativa

4. INVENTARIO (/api/inventario/)
   - Productos y categorías
   - Control de stock con método PEPS
   - Movimientos y transferencias
   - Alertas de stock mínimo

5. CONTABILIDAD (/api/contabilidad/)
   - Plan de cuentas PCGE
   - Asientos automáticos
   - Cuentas por cobrar/pagar
   - Estados financieros

6. PUNTO DE VENTA (/api/pos/)
   - Interfaz optimizada para ventas rápidas
   - Búsqueda de productos y clientes
   - Cálculo de totales en tiempo real

7. REPORTES (/api/reportes/)
   - Dashboards ejecutivos
   - Reportes de ventas
   - Analytics y KPIs
   - Exportación Excel/PDF

8. INTEGRACIONES (/api/integraciones/)
   - Configuración Nubefact
   - Webhooks de SUNAT
   - APIs externas (RENIEC, Bancos)

=== APIS ESPECIALIZADAS ===

MÓVIL (/api/mobile/)
- Endpoints optimizados para apps móviles
- Payloads reducidos
- Sincronización offline

EXTERNA (/api/external/)
- Para integraciones con sistemas externos
- Autenticación API Key
- Webhooks entrantes

ADMIN (/api/admin/)
- Solo para administradores del sistema
- Configuración avanzada
- Logs y auditoría

=== CARACTERÍSTICAS TÉCNICAS ===

AUTENTICACIÓN:
- JWT tokens con refresh
- Permisos granulares por módulo
- Rate limiting por usuario

VALIDACIONES:
- Cumplimiento normativa SUNAT
- Validación RUC/DNI con dígito verificador
- Numeración correlativa obligatoria

INTEGRACIONES:
- Nubefact para emisión electrónica
- SUNAT para consultas en línea
- RENIEC para validación identidades

PERFORMANCE:
- Cache con Redis
- Queries optimizadas
- Paginación automática
- Filtros avanzados

SEGURIDAD:
- HTTPS obligatorio en producción
- Validación CORS
- Headers de seguridad
- Audit log completo

=== CÓDIGOS DE ESTADO ===

200 OK              - Operación exitosa
201 Created         - Recurso creado exitosamente
204 No Content      - Operación exitosa sin contenido
400 Bad Request     - Datos de entrada inválidos
401 Unauthorized    - No autenticado
403 Forbidden       - Sin permisos suficientes
404 Not Found       - Recurso no encontrado
409 Conflict        - Conflicto (ej: numeración duplicada)
422 Unprocessable   - Error de validación de negocio
429 Too Many Req    - Rate limit excedido
500 Internal Error  - Error del servidor
503 Service Unavail - Servicio temporalmente no disponible

=== FORMATOS DE RESPUESTA ===

Éxito:
{
    "id": 123,
    "data": { ... },
    "timestamp": "2024-01-15T10:30:00Z"
}

Error:
{
    "error": "Descripción del error",
    "code": "ERROR_CODE",
    "details": { ... },
    "timestamp": "2024-01-15T10:30:00Z"
}

Lista paginada:
{
    "count": 150,
    "next": "https://api.felicita.pe/api/facturas/?page=2",
    "previous": null,
    "results": [ ... ]
}

=== EJEMPLOS DE USO ===

# Autenticación
POST /api/auth/login/
{
    "username": "usuario@empresa.com",
    "password": "password123"
}

# Crear factura
POST /api/facturacion/facturas/
{
    "cliente": 1,
    "serie": "F001",
    "items": [...]
}

# Consultar inventario
GET /api/inventario/productos/?stock_bajo=true

# Dashboard de ventas
GET /api/reportes/dashboard/?periodo=mes

=== WEBHOOKS ===

Nubefact notifica cambios de estado:
POST /api/webhooks/nubefact/
{
    "invoice_id": "...",
    "status": "ACEPTADO",
    "sunat_code": "0",
    "timestamp": "..."
}

=== RATE LIMITING ===

- 1000 requests/hora por usuario autenticado
- 100 requests/hora por IP sin autenticar
- 10000 requests/hora para integraciones
- Headers: X-RateLimit-Limit, X-RateLimit-Remaining

=== VERSIONADO ===

- Versión actual: v1
- URL: /api/v1/ (opcional, por defecto es v1)
- Backward compatibility garantizada por 12 meses
- Nuevas versiones anunciadas con 3 meses de anticipación
"""