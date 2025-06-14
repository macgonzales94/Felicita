"""
URLS DE INVENTARIO - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

URLs básicas para el módulo de inventario
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Router básico (vacío por ahora)
router = DefaultRouter()

# TODO: Agregar ViewSets cuando se implementen
# from . import views
# router.register(r'productos', views.ProductoViewSet, basename='productos')
# router.register(r'categorias', views.CategoriaViewSet, basename='categorias')
# router.register(r'almacenes', views.AlmacenViewSet, basename='almacenes')

app_name = 'inventario'

# Patrones de URL básicos
urlpatterns = [
    path('', include(router.urls)),
]

# TODO: Agregar URLs personalizadas cuando sea necesario
# urlpatterns += [
#     path('kardex/<int:producto_id>/', views.KardexProductoView.as_view(), name='kardex-producto'),
#     path('stock-actual/', views.StockActualView.as_view(), name='stock-actual'),
#     path('productos-agotados/', views.ProductosAgotadosView.as_view(), name='productos-agotados'),
# ]