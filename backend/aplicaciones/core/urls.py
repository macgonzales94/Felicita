"""
URLs CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

URLs para el módulo core (empresas, clientes, productos, etc.)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# =============================================================================
# CONFIGURACIÓN DEL ROUTER
# =============================================================================
router = DefaultRouter()
router.register(r'empresas', views.EmpresaViewSet, basename='empresa')
router.register(r'sucursales', views.SucursalViewSet, basename='sucursal')
router.register(r'clientes', views.ClienteViewSet, basename='cliente')
router.register(r'proveedores', views.ProveedorViewSet, basename='proveedor')
router.register(r'categorias-productos', views.CategoriaProductoViewSet, basename='categoriaproducto')
router.register(r'productos', views.ProductoViewSet, basename='producto')
router.register(r'unidades-medida', views.UnidadMedidaViewSet, basename='unidadmedida')
router.register(r'monedas', views.MonedaViewSet, basename='moneda')
router.register(r'tipos-cambio', views.TipoCambioViewSet, basename='tipocambio')
router.register(r'configuraciones', views.ConfiguracionSistemaViewSet, basename='configuracion')

# =============================================================================
# URLs PRINCIPALES
# =============================================================================
urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # =============================================================================
    # ENDPOINTS ESPECÍFICOS DE EMPRESA
    # =============================================================================
    path('empresas/<uuid:pk>/configuracion/', 
         views.ConfiguracionEmpresaView.as_view(), 
         name='empresa-configuracion'),
    
    path('empresas/<uuid:pk>/series-comprobantes/', 
         views.SeriesComprobantesEmpresaView.as_view(), 
         name='empresa-series'),
    
    path('empresas/<uuid:pk>/plan-cuentas/', 
         views.PlanCuentasEmpresaView.as_view(), 
         name='empresa-plan-cuentas'),
    
    # =============================================================================
    # ENDPOINTS ESPECÍFICOS DE CLIENTE
    # =============================================================================
    path('clientes/buscar/', 
         views.BuscarClienteView.as_view(), 
         name='buscar-cliente'),
    
    path('clientes/validar-documento/', 
         views.ValidarDocumentoClienteView.as_view(), 
         name='validar-documento-cliente'),
    
    path('clientes/<uuid:pk>/historial-compras/', 
         views.HistorialComprasClienteView.as_view(), 
         name='cliente-historial-compras'),
    
    path('clientes/<uuid:pk>/estado-cuenta/', 
         views.EstadoCuentaClienteView.as_view(), 
         name='cliente-estado-cuenta'),
    
    path('clientes/importar/', 
         views.ImportarClientesView.as_view(), 
         name='importar-clientes'),
    
    path('clientes/exportar/', 
         views.ExportarClientesView.as_view(), 
         name='exportar-clientes'),
    
    # =============================================================================
    # ENDPOINTS ESPECÍFICOS DE PRODUCTO
    # =============================================================================
    path('productos/buscar/', 
         views.BuscarProductoView.as_view(), 
         name='buscar-producto'),
    
    path('productos/por-codigo-barras/', 
         views.ProductoPorCodigoBarrasView.as_view(), 
         name='producto-codigo-barras'),
    
    path('productos/<uuid:pk>/stock/', 
         views.StockProductoView.as_view(), 
         name='producto-stock'),
    
    path('productos/<uuid:pk>/precios/', 
         views.PreciosProductoView.as_view(), 
         name='producto-precios'),
    
    path('productos/<uuid:pk>/movimientos/', 
         views.MovimientosProductoView.as_view(), 
         name='producto-movimientos'),
    
    path('productos/importar/', 
         views.ImportarProductosView.as_view(), 
         name='importar-productos'),
    
    path('productos/exportar/', 
         views.ExportarProductosView.as_view(), 
         name='exportar-productos'),
    
    path('productos/stock-bajo/', 
         views.ProductosStockBajoView.as_view(), 
         name='productos-stock-bajo'),
    
    # =============================================================================
    # ENDPOINTS DE CATEGORÍAS
    # =============================================================================
    path('categorias-productos/<uuid:pk>/productos/', 
         views.ProductosPorCategoriaView.as_view(), 
         name='productos-por-categoria'),
    
    path('categorias-productos/<uuid:pk>/subcategorias/', 
         views.SubcategoriasView.as_view(), 
         name='subcategorias'),
    
    # =============================================================================
    # ENDPOINTS DE CONFIGURACIÓN SISTEMA
    # =============================================================================
    path('configuraciones/por-clave/<str:clave>/', 
         views.ConfiguracionPorClaveView.as_view(), 
         name='configuracion-por-clave'),
    
    path('configuraciones/actualizar-multiple/', 
         views.ActualizarConfiguracionesView.as_view(), 
         name='actualizar-configuraciones'),
    
    # =============================================================================
    # ENDPOINTS DE ESTADÍSTICAS Y DASHBOARD
    # =============================================================================
    path('estadisticas/dashboard/', 
         views.EstadisticasDashboardView.as_view(), 
         name='estadisticas-dashboard'),
    
    path('estadisticas/ventas/', 
         views.EstadisticasVentasView.as_view(), 
         name='estadisticas-ventas'),
    
    path('estadisticas/inventario/', 
         views.EstadisticasInventarioView.as_view(), 
         name='estadisticas-inventario'),
    
    path('estadisticas/clientes/', 
         views.EstadisticasClientesView.as_view(), 
         name='estadisticas-clientes'),
    
    # =============================================================================
    # ENDPOINTS DE UTILIDADES
    # =============================================================================
    path('utilidades/validar-ruc/', 
         views.ValidarRUCView.as_view(), 
         name='validar-ruc'),
    
    path('utilidades/validar-dni/', 
         views.ValidarDNIView.as_view(), 
         name='validar-dni'),
    
    path('utilidades/consultar-tipo-cambio/', 
         views.ConsultarTipoCambioView.as_view(), 
         name='consultar-tipo-cambio'),
    
    path('utilidades/ubigeos/', 
         views.UbigeosView.as_view(), 
         name='ubigeos'),
    
    path('utilidades/codigos-sunat/', 
         views.CodigosSunatView.as_view(), 
         name='codigos-sunat'),
    
    # =============================================================================
    # ENDPOINTS DE BACKUP Y MANTENIMIENTO
    # =============================================================================
    path('mantenimiento/limpiar-cache/', 
         views.LimpiarCacheView.as_view(), 
         name='limpiar-cache'),
    
    path('mantenimiento/verificar-integridad/', 
         views.VerificarIntegridadView.as_view(), 
         name='verificar-integridad'),
    
    path('backup/exportar-datos/', 
         views.ExportarDatosView.as_view(), 
         name='exportar-datos'),
    
    path('backup/importar-datos/', 
         views.ImportarDatosView.as_view(), 
         name='importar-datos'),
]

# =============================================================================
# NAMESPACE DE LA APLICACIÓN
# =============================================================================
app_name = 'core'