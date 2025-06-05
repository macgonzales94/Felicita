from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'sunat'

# Router para ViewSets
router = DefaultRouter()

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs de integración SUNAT
    # path('consultar-ruc/', ConsultarRucView.as_view(), name='consultar_ruc'),
    # path('consultar-dni/', ConsultarDniView.as_view(), name='consultar_dni'),
    # path('enviar-comprobante/', EnviarComprobanteView.as_view(), name='enviar_comprobante'),
    # path('consultar-estado/', ConsultarEstadoView.as_view(), name='consultar_estado'),
    # path('comunicacion-baja/', ComunicacionBajaView.as_view(), name='comunicacion_baja'),
]