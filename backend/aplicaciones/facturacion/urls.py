"""
URLS DE FACTURACIÓN - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

URLs y rutas para el módulo de facturación electrónica
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# =============================================================================
# CONFIGURACIÓN DEL ROUTER
# =============================================================================
router = DefaultRouter()

# Registrar ViewSets principales
router.register(r'facturas', views.FacturaViewSet, basename='facturas')
router.register(r'boletas', views.BoletaViewSet, basename='boletas')
router.register(r'notas-credito', views.NotaCreditoViewSet, basename='notas-credito')
router.register(r'series', views.SerieComprobanteViewSet, basename='series')

# Registrar ViewSets auxiliares
router.register(r'estadisticas', views.EstadisticasFacturacionView, basename='estadisticas')

app_name = 'facturacion'

# =============================================================================
# PATRONES DE URL
# =============================================================================
urlpatterns = [
    # URLs del router principal
    path('', include(router.urls)),
    
    # =============================================================================
    # URLs ADICIONALES PERSONALIZADAS
    # =============================================================================
    
    # Endpoints para acciones masivas
    path('facturas/acciones-masivas/', 
         views.AccionesMasivasFacturasView.as_view(), 
         name='facturas-acciones-masivas'),
    
    path('boletas/acciones-masivas/', 
         views.AccionesMasivasBoletasView.as_view(), 
         name='boletas-acciones-masivas'),
    
    # Endpoints para validaciones previas
    path('validar-numeracion/', 
         views.ValidarNumeracionView.as_view(), 
         name='validar-numeracion'),
    
    path('validar-cliente-comprobante/', 
         views.ValidarClienteComprobanteView.as_view(), 
         name='validar-cliente-comprobante'),
    
    # Endpoints para consultas SUNAT
    path('consultar-ruc/<str:ruc>/', 
         views.ConsultarRucView.as_view(), 
         name='consultar-ruc'),
    
    path('consultar-dni/<str:dni>/', 
         views.ConsultarDniView.as_view(), 
         name='consultar-dni'),
    
    # Endpoints para reportes específicos
    path('reportes/ventas-diarias/', 
         views.ReporteVentasDiariasView.as_view(), 
         name='reporte-ventas-diarias'),
    
    path('reportes/top-clientes/', 
         views.ReporteTopClientesView.as_view(), 
         name='reporte-top-clientes'),
    
    path('reportes/top-productos/', 
         views.ReporteTopProductosView.as_view(), 
         name='reporte-top-productos'),
    
    path('reportes/estado-sunat/', 
         views.ReporteEstadoSunatView.as_view(), 
         name='reporte-estado-sunat'),
    
    # Endpoints para exportación
    path('exportar/facturas-excel/', 
         views.ExportarFacturasExcelView.as_view(), 
         name='exportar-facturas-excel'),
    
    path('exportar/boletas-excel/', 
         views.ExportarBoletasExcelView.as_view(), 
         name='exportar-boletas-excel'),
    
    path('exportar/notas-credito-excel/', 
         views.ExportarNotasCreditoExcelView.as_view(), 
         name='exportar-notas-credito-excel'),
    
    # Endpoints para libros electrónicos PLE
    path('ple/registro-ventas/', 
         views.GenerarPLERegistroVentasView.as_view(), 
         name='ple-registro-ventas'),
    
    path('ple/libro-diario/', 
         views.GenerarPLELibroDiarioView.as_view(), 
         name='ple-libro-diario'),
    
    # Endpoints para synchronización con Nubefact
    path('sync/estados-sunat/', 
         views.SincronizarEstadosSunatView.as_view(), 
         name='sync-estados-sunat'),
    
    path('sync/reenviar-pendientes/', 
         views.ReenviarComprobantePendientesView.as_view(), 
         name='sync-reenviar-pendientes'),
    
    # Endpoints para utilidades
    path('utilidades/limpiar-borradores/', 
         views.LimpiarBorradoresView.as_view(), 
         name='limpiar-borradores'),
    
    path('utilidades/corregir-numeracion/', 
         views.CorregirNumeracionView.as_view(), 
         name='corregir-numeracion'),
    
    # Endpoints para configuración
    path('configuracion/series-activas/', 
         views.SeriesActivasView.as_view(), 
         name='series-activas'),
    
    path('configuracion/proximos-numeros/', 
         views.ProximosNumerosView.as_view(), 
         name='proximos-numeros'),
    
    # =============================================================================
    # URLs PARA PUNTO DE VENTA
    # =============================================================================
    
    # Endpoint especializado para POS
    path('pos/crear-venta/', 
         views.CrearVentaPOSView.as_view(), 
         name='pos-crear-venta'),
    
    path('pos/buscar-cliente/', 
         views.BuscarClientePOSView.as_view(), 
         name='pos-buscar-cliente'),
    
    path('pos/buscar-producto/', 
         views.BuscarProductoPOSView.as_view(), 
         name='pos-buscar-producto'),
    
    path('pos/calcular-totales/', 
         views.CalcularTotalesPOSView.as_view(), 
         name='pos-calcular-totales'),
    
    path('pos/aplicar-descuento/', 
         views.AplicarDescuentoPOSView.as_view(), 
         name='pos-aplicar-descuento'),
    
    # =============================================================================
    # URLs PARA INTEGRACIONES
    # =============================================================================
    
    # Endpoints para integraciones con sistemas externos
    path('integraciones/importar-ventas/', 
         views.ImportarVentasView.as_view(), 
         name='importar-ventas'),
    
    path('integraciones/exportar-contabilidad/', 
         views.ExportarContabilidadView.as_view(), 
         name='exportar-contabilidad'),
    
    # =============================================================================
    # URLs PARA DASHBOARDS Y ANALYTICS
    # =============================================================================
    
    # Endpoints para métricas en tiempo real
    path('analytics/kpis-tiempo-real/', 
         views.KPIsTiempoRealView.as_view(), 
         name='kpis-tiempo-real'),
    
    path('analytics/grafico-ventas-mes/', 
         views.GraficoVentasMesView.as_view(), 
         name='grafico-ventas-mes'),
    
    path('analytics/comparativo-periodos/', 
         views.ComparativoPeriodosView.as_view(), 
         name='comparativo-periodos'),
    
    path('analytics/tendencias-cliente/', 
         views.TendenciasClienteView.as_view(), 
         name='tendencias-cliente'),
    
    # =============================================================================
    # URLs PARA ADMINISTRACIÓN
    # =============================================================================
    
    # Endpoints para administradores
    path('admin/reset-numeracion/', 
         views.ResetNumeracionView.as_view(), 
         name='admin-reset-numeracion'),
    
    path('admin/audit-log/', 
         views.AuditLogView.as_view(), 
         name='admin-audit-log'),
    
    path('admin/health-check/', 
         views.HealthCheckFacturacionView.as_view(), 
         name='admin-health-check'),
    
    # =============================================================================
    # URLs PARA MÓVIL/APP
    # =============================================================================
    
    # Endpoints optimizados para aplicaciones móviles
    path('mobile/resumen-dia/', 
         views.ResumenDiaMobileView.as_view(), 
         name='mobile-resumen-dia'),
    
    path('mobile/ultimas-ventas/', 
         views.UltimasVentasMobileView.as_view(), 
         name='mobile-ultimas-ventas'),
    
    path('mobile/sync-offline/', 
         views.SyncOfflineMobileView.as_view(), 
         name='mobile-sync-offline'),
]

# =============================================================================
# DOCUMENTACIÓN DE ENDPOINTS
# =============================================================================
"""
DOCUMENTACIÓN DE ENDPOINTS DE FACTURACIÓN

=== ENDPOINTS PRINCIPALES ===

1. FACTURAS (/api/facturas/)
   - GET /           : Listar facturas con filtros
   - POST /          : Crear nueva factura
   - GET /{id}/      : Obtener factura específica
   - PUT /{id}/      : Actualizar factura completa
   - PATCH /{id}/    : Actualización parcial
   - DELETE /{id}/   : Eliminar factura

   Acciones especiales:
   - POST /{id}/enviar_sunat/     : Enviar a SUNAT
   - GET /{id}/consultar_estado/  : Consultar estado SUNAT
   - POST /{id}/anular/           : Anular comprobante
   - GET /{id}/descargar_xml/     : Descargar XML
   - GET /{id}/descargar_pdf/     : Descargar PDF
   - GET /resumen_diario/         : Resumen del día
   - GET /por_cliente/            : Facturas por cliente

2. BOLETAS (/api/boletas/)
   - Mismas operaciones que facturas
   - Validaciones específicas para DNI

3. NOTAS DE CRÉDITO (/api/notas-credito/)
   - Mismas operaciones básicas
   - POST /desde_factura/         : Crear desde factura

4. SERIES (/api/series/)
   - CRUD completo de series
   - GET /por_tipo/               : Series por tipo
   - POST /{id}/reiniciar_numeracion/ : Reiniciar numeración

=== ENDPOINTS ESPECIALIZADOS ===

5. PUNTO DE VENTA (/api/pos/)
   - POST /crear-venta/           : Crear venta optimizada POS
   - GET /buscar-cliente/         : Búsqueda rápida cliente
   - GET /buscar-producto/        : Búsqueda rápida producto
   - POST /calcular-totales/      : Calcular totales en tiempo real

6. REPORTES (/api/reportes/)
   - GET /ventas-diarias/         : Reporte ventas por día
   - GET /top-clientes/           : Top clientes por ventas
   - GET /top-productos/          : Top productos vendidos
   - GET /estado-sunat/           : Estado de envíos SUNAT

7. EXPORTACIÓN (/api/exportar/)
   - GET /facturas-excel/         : Exportar facturas a Excel
   - GET /boletas-excel/          : Exportar boletas a Excel

8. PLE (/api/ple/)
   - GET /registro-ventas/        : Generar PLE registro ventas
   - GET /libro-diario/           : Generar PLE libro diario

9. SINCRONIZACIÓN (/api/sync/)
   - POST /estados-sunat/         : Sync estados desde SUNAT
   - POST /reenviar-pendientes/   : Reenviar comprobantes pendientes

=== FILTROS DISPONIBLES ===

Todos los endpoints de listado soportan:
- fecha_desde, fecha_hasta       : Rango de fechas
- periodo                        : hoy, ayer, semana, mes, año
- cliente, cliente_documento     : Filtro por cliente
- serie, numero                  : Filtro por numeración
- total_desde, total_hasta       : Rango de montos
- estado_sunat                   : PENDIENTE, ACEPTADO, RECHAZADO
- moneda                         : PEN, USD, EUR

Filtros específicos por tipo:
- Facturas: condicion_pago, medio_pago, vencidas
- Boletas: solo_dni, monto_menor
- Notas: codigo_motivo, documento_modificado

=== CÓDIGOS DE RESPUESTA ===

200 OK                  : Operación exitosa
201 Created            : Recurso creado
400 Bad Request        : Datos inválidos
401 Unauthorized       : No autenticado
403 Forbidden          : Sin permisos
404 Not Found          : Recurso no encontrado
409 Conflict           : Conflicto (ej: numeración duplicada)
422 Unprocessable      : Error de validación SUNAT
500 Internal Error     : Error del servidor

=== EJEMPLOS DE USO ===

# Crear factura
POST /api/facturas/
{
    "cliente": 1,
    "serie": "F001",
    "moneda": "PEN",
    "items": [
        {
            "producto_id": 1,
            "descripcion": "Producto A",
            "cantidad": 2,
            "precio_unitario": 100.00
        }
    ]
}

# Filtrar facturas del mes
GET /api/facturas/?periodo=mes&estado_sunat=ACEPTADO

# Buscar cliente en POS
GET /api/pos/buscar-cliente/?q=12345678

# Exportar facturas
GET /api/exportar/facturas-excel/?fecha_desde=2024-01-01&fecha_hasta=2024-01-31
"""