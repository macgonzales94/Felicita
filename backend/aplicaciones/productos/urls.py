from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'productos'

# Router para ViewSets
router = DefaultRouter()
# router.register(r'productos', ProductoViewSet)
# router.register(r'categorias', CategoriaProductoViewSet)

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # URLs personalizadas
    # path('buscar/', BuscarProductoView.as_view(), name='buscar'),
    # path('codigo-barras/', BuscarPorCodigoBarrasView.as_view(), name='codigo_barras'),
    # path('stock-bajo/', ProductosStockBajoView.as_view(), name='stock_bajo'),
    # path('importar/', ImportarProductosView.as_view(), name='importar'),
]