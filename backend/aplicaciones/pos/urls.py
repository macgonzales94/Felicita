from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'pos'

# Router para ViewSets
router = DefaultRouter()

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs del POS
    # path('productos/', ProductosPOSView.as_view(), name='productos'),
    # path('buscar-cliente/', BuscarClientePOSView.as_view(), name='buscar_cliente'),
    # path('procesar-venta/', ProcesarVentaView.as_view(), name='procesar_venta'),
    # path('metodos-pago/', MetodosPagoView.as_view(), name='metodos_pago'),
    # path('caja/', EstadoCajaView.as_view(), name='estado_caja'),
]