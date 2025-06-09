"""
URLs PRINCIPALES - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Configuración principal de URLs del proyecto
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# =============================================================================
# VISTAS BÁSICAS DE SISTEMA
# =============================================================================
@api_view(['GET'])
@permission_classes([AllowAny]) 
def health_check(request):
    """
    Endpoint para verificar el estado del sistema
    """
    return Response({
        'status': 'ok',
        'timestamp': timezone.now(),
        'version': '1.0.0',
        'environment': settings.DEBUG and 'development' or 'production',
        'database': 'connected',
        'message': 'FELICITA Sistema de Facturación Electrónica - Estado OK'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def sistema_info(request):
    """
    Información general del sistema
    """
    return Response({
        'nombre': 'FELICITA',
        'descripcion': 'Sistema de Facturación Electrónica para Perú',
        'version': '1.0.0',
        'pais': 'Perú',
        'normativa': 'SUNAT',
        'stack': {
            'backend': 'Django + DRF',
            'frontend': 'React + TypeScript',
            'database': 'PostgreSQL',
            'ose': 'Nubefact'
        },
        'modulos': [
            'Facturación Electrónica',
            'Punto de Venta',
            'Control de Inventarios',
            'Contabilidad',
            'Reportes y Analytics',
            'Gestión Administrativa'
        ],
        'cumplimiento': [
            'Facturación Electrónica SUNAT',
            'Libros Electrónicos PLE',
            'Método PEPS para inventarios',
            'Plan Contable General Empresarial'
        ]
    })

def handler404(request, exception):
    """Manejador personalizado para error 404"""
    return JsonResponse({
        'error': 'Endpoint no encontrado',
        'codigo': 404,
        'mensaje': 'La ruta solicitada no existe en FELICITA'
    }, status=404)

def handler500(request):
    """Manejador personalizado para error 500"""
    return JsonResponse({
        'error': 'Error interno del servidor',
        'codigo': 500,
        'mensaje': 'Ha ocurrido un error interno en FELICITA'
    }, status=500)

# =============================================================================
# CONFIGURACIÓN PRINCIPAL DE URLs
# =============================================================================
urlpatterns = [
    # =============================================================================
    # ADMINISTRACIÓN DJANGO
    # =============================================================================
    path('admin/', admin.site.urls),
    
    # =============================================================================
    # ENDPOINTS DE SISTEMA
    # =============================================================================
    path('health/', health_check, name='health_check'),
    path('info/', sistema_info, name='sistema_info'),
    
    # =============================================================================
    # API PRINCIPAL
    # =============================================================================
    path('api/', include([
        
        path('health/', health_check, name='api_health_check'),
        # Autenticación y usuarios
        #path('auth/', include('aplicaciones.usuarios.urls')),
        
        # Autenticación y usuarios
        path('usuarios/', include('aplicaciones.usuarios.urls')),
        
        # Módulos principales
        path('core/', include('aplicaciones.core.urls'))
        #path('facturacion/', include('aplicaciones.facturacion.urls')),
        #path('inventario/', include('aplicaciones.inventario.urls')),
        #path('contabilidad/', include('aplicaciones.contabilidad.urls')),
        #path('pos/', include('aplicaciones.punto_venta.urls')),
        #path('reportes/', include('aplicaciones.reportes.urls')),
        #path('integraciones/', include('aplicaciones.integraciones.urls')),
    ])),
    
    # =============================================================================
    # DOCUMENTACIÓN API
    # =============================================================================
    #path('docs/', include([
    #    path('', TemplateView.as_view(
    #        template_name='docs/api_docs.html',
    #        extra_context={'title': 'FELICITA API Documentation'}
    #    ), name='api_docs'),
    #    path('swagger/', TemplateView.as_view(
    #        template_name='docs/swagger.html',
    #        extra_context={'title': 'FELICITA API Swagger'}
    #    ), name='swagger_docs'),
    #    path('redoc/', TemplateView.as_view(
    #        template_name='docs/redoc.html',
    #        extra_context={'title': 'FELICITA API ReDoc'}
     #   ), name='redoc_docs'),
    #])),
    
    # =============================================================================
    # WEBHOOKS
    # =============================================================================
    path('webhooks/', include([
        path('nubefact/', include('aplicaciones.integraciones.webhook_urls')),
    ])),
    
    # =============================================================================
    # PÁGINA PRINCIPAL (DESARROLLO)
    # =============================================================================
    path('', TemplateView.as_view(
        template_name='index.html',
        extra_context={
            'title': 'FELICITA - Sistema de Facturación Electrónica',
            'description': 'Sistema completo de facturación electrónica para Perú',
            'version': '1.0.0'
        }
    ), name='home'),
]

# =============================================================================
# CONFIGURACIÓN PARA DESARROLLO
# =============================================================================
if settings.DEBUG:
    # Archivos estáticos y media en desarrollo
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
    
    # Endpoints adicionales para desarrollo
    urlpatterns += [
        path('dev/', include([
            path('test/', TemplateView.as_view(
                template_name='dev/test.html'
            ), name='dev_test'),
            path('models/', TemplateView.as_view(
                template_name='dev/models.html'
            ), name='dev_models'),
        ])),
    ]

# =============================================================================
# CONFIGURACIÓN DEL ADMIN
# =============================================================================
admin.site.site_header = 'FELICITA - Administración'
admin.site.site_title = 'FELICITA Admin'
admin.site.index_title = 'Panel de Administración - Sistema de Facturación Electrónica'

# =============================================================================
# HANDLERS DE ERROR
# =============================================================================
handler404 = handler404
handler500 = handler500