from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'reportes'

# Router para ViewSets
router = DefaultRouter()

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs de reportes
    # path('ventas/', ReporteVentasView.as_view(), name='ventas'),
    # path('compras/', ReporteComprasView.as_view(), name='compras'),
    # path('inventario/', ReporteInventarioView.as_view(), name='inventario'),
    # path('clientes/', ReporteClientesView.as_view(), name='clientes'),
    # path('productos-mas-vendidos/', ProductosMasVendidosView.as_view(), name='productos_mas_vendidos'),
    # path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # path('ple/', ReportePLEView.as_view(), name='ple'),
]
