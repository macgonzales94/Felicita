from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'facturacion'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'comprobantes', ComprobanteViewSet)
# router.register(r'series', SerieComprobanteViewSet)

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('emitir-factura/', EmitirFacturaView.as_view(), name='emitir_factura'),
    # path('emitir-boleta/', EmitirBoletaView.as_view(), name='emitir_boleta'),
    # path('nota-credito/', NotaCreditoView.as_view(), name='nota_credito'),
    # path('nota-debito/', NotaDebitoView.as_view(), name='nota_debito'),
    # path('enviar-sunat/<int:pk>/', EnviarSunatView.as_view(), name='enviar_sunat'),
    # path('anular/<int:pk>/', AnularComprobanteView.as_view(), name='anular'),
    # path('pdf/<int:pk>/', GenerarPDFView.as_view(), name='pdf'),
]