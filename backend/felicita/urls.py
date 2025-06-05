"""
URLs principales del proyecto FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# URLs principales
urlpatterns = [
    # Administración Django
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # APIs de aplicaciones
    path('api/auth/', include('aplicaciones.usuarios.urls')),
    path('api/empresas/', include('aplicaciones.empresas.urls')),
    path('api/clientes/', include('aplicaciones.clientes.urls')),
    path('api/productos/', include('aplicaciones.productos.urls')),
    path('api/inventarios/', include('aplicaciones.inventarios.urls')),
    path('api/facturacion/', include('aplicaciones.facturacion.urls')),
    path('api/contabilidad/', include('aplicaciones.contabilidad.urls')),
    path('api/reportes/', include('aplicaciones.reportes.urls')),
    path('api/pos/', include('aplicaciones.pos.urls')),
    path('api/sunat/', include('aplicaciones.sunat.urls')),
    path('api/configuraciones/', include('aplicaciones.configuraciones.urls')),
    
    # Redirección por defecto a docs
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
]

# Configurar URLs para archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Personalizar admin
admin.site.site_header = 'FELICITA - Administración'
admin.site.site_title = 'FELICITA Admin'
admin.site.index_title = 'Sistema de Facturación Electrónica para Perú'