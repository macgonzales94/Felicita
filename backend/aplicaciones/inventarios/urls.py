from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'inventarios'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'almacenes', AlmacenViewSet)
# router.register(r'stocks', StockViewSet)
# router.register(r'movimientos', MovimientoInventarioViewSet)

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('kardex/', KardexView.as_view(), name='kardex'),
    # path('transferencias/', TransferenciaView.as_view(), name='transferencias'),
    # path('ajustes/', AjusteInventarioView.as_view(), name='ajustes'),
    # path('reporte-stock/', ReporteStockView.as_view(), name='reporte_stock'),
]