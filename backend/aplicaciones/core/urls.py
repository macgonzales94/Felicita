"""
FELICITA - URLs Core
Sistema de Facturación Electrónica para Perú

URLs para las entidades base del sistema
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmpresaViewSet,
    SucursalViewSet,
    ClienteViewSet,
    ConfiguracionViewSet,
    TipoComprobanteViewSet,
    SerieComprobanteViewSet,
)

# ===========================================
# ROUTER PRINCIPAL
# ===========================================

router = DefaultRouter()

# Registrar ViewSets
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'sucursales', SucursalViewSet, basename='sucursal')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'configuraciones', ConfiguracionViewSet, basename='configuracion')
router.register(r'tipos-comprobante', TipoComprobanteViewSet, basename='tipo-comprobante')
router.register(r'series-comprobante', SerieComprobanteViewSet, basename='serie-comprobante')

# ===========================================
# PATRONES DE URL
# ===========================================

urlpatterns = [
    # Router principal
    path('', include(router.urls)),
    
    # URLs adicionales específicas se pueden agregar aquí si es necesario
    # path('especial/', vista_especial, name='especial'),
]

# ===========================================
# NOMBRES DE URL GENERADOS
# ===========================================

"""
El router genera automáticamente las siguientes URLs:

EMPRESAS:
- GET    /api/core/empresas/                    - Lista de empresas
- POST   /api/core/empresas/                    - Crear empresa
- GET    /api/core/empresas/{id}/               - Detalle de empresa
- PUT    /api/core/empresas/{id}/               - Actualizar empresa
- PATCH  /api/core/empresas/{id}/               - Actualizar parcial empresa
- DELETE /api/core/empresas/{id}/               - Eliminar empresa
- PATCH  /api/core/empresas/{id}/toggle_active/ - Activar/desactivar empresa
- GET    /api/core/empresas/{id}/estadisticas/  - Estadísticas de empresa
- POST   /api/core/empresas/{id}/configurar_series/ - Configurar series

SUCURSALES:
- GET    /api/core/sucursales/                  - Lista de sucursales
- POST   /api/core/sucursales/                  - Crear sucursal
- GET    /api/core/sucursales/{id}/             - Detalle de sucursal
- PUT    /api/core/sucursales/{id}/             - Actualizar sucursal
- PATCH  /api/core/sucursales/{id}/             - Actualizar parcial sucursal
- DELETE /api/core/sucursales/{id}/             - Eliminar sucursal
- PATCH  /api/core/sucursales/{id}/toggle_active/ - Activar/desactivar sucursal
- POST   /api/core/sucursales/{id}/establecer_principal/ - Establecer como principal

CLIENTES:
- GET    /api/core/clientes/                    - Lista de clientes
- POST   /api/core/clientes/                    - Crear cliente
- GET    /api/core/clientes/{id}/               - Detalle de cliente
- PUT    /api/core/clientes/{id}/               - Actualizar cliente
- PATCH  /api/core/clientes/{id}/               - Actualizar parcial cliente
- DELETE /api/core/clientes/{id}/               - Eliminar cliente
- PATCH  /api/core/clientes/{id}/toggle_active/ - Activar/desactivar cliente
- GET    /api/core/clientes/simple/             - Lista simplificada
- GET    /api/core/clientes/autocompletar/      - Autocompletado
- POST   /api/core/clientes/validar_documento/  - Validar documento
- POST   /api/core/clientes/importar/           - Importar desde Excel/CSV
- POST   /api/core/clientes/exportar/           - Exportar a Excel/CSV

CONFIGURACIONES:
- GET    /api/core/configuraciones/             - Lista de configuraciones
- POST   /api/core/configuraciones/             - Crear configuración
- GET    /api/core/configuraciones/{id}/        - Detalle de configuración
- PUT    /api/core/configuraciones/{id}/        - Actualizar configuración
- PATCH  /api/core/configuraciones/{id}/        - Actualizar parcial configuración
- DELETE /api/core/configuraciones/{id}/        - Eliminar configuración
- GET    /api/core/configuraciones/mi_configuracion/ - Mi configuración

TIPOS DE COMPROBANTE:
- GET    /api/core/tipos-comprobante/           - Lista de tipos (solo lectura)
- GET    /api/core/tipos-comprobante/{id}/      - Detalle de tipo
- GET    /api/core/tipos-comprobante/principales/ - Tipos principales

SERIES DE COMPROBANTE:
- GET    /api/core/series-comprobante/          - Lista de series
- POST   /api/core/series-comprobante/          - Crear serie
- GET    /api/core/series-comprobante/{id}/     - Detalle de serie
- PUT    /api/core/series-comprobante/{id}/     - Actualizar serie
- PATCH  /api/core/series-comprobante/{id}/     - Actualizar parcial serie
- DELETE /api/core/series-comprobante/{id}/     - Eliminar serie
- PATCH  /api/core/series-comprobante/{id}/toggle_active/ - Activar/desactivar serie
- GET    /api/core/series-comprobante/por_tipo/ - Series por tipo
- POST   /api/core/series-comprobante/{id}/obtener_siguiente_numero/ - Siguiente número
- POST   /api/core/series-comprobante/{id}/reiniciar_numeracion/ - Reiniciar numeración

PARÁMETROS DE FILTRADO:

Empresas:
- ?activo=true/false               - Filtrar por estado activo
- ?search=texto                    - Buscar en RUC, razón social, nombre comercial
- ?ordering=razon_social           - Ordenar por campo

Sucursales:
- ?empresa=ID                      - Filtrar por empresa
- ?es_principal=true/false         - Filtrar sucursales principales
- ?activo=true/false               - Filtrar por estado activo
- ?search=texto                    - Buscar en código, nombre, dirección
- ?ordering=nombre                 - Ordenar por campo

Clientes:
- ?empresa=ID                      - Filtrar por empresa
- ?tipo_documento=dni/ruc/etc      - Filtrar por tipo de documento
- ?activo=true/false               - Filtrar por estado activo
- ?search=texto                    - Buscar en documento, razón social, email
- ?ordering=razon_social           - Ordenar por campo

Configuraciones:
- ?empresa=ID                      - Filtrar por empresa

Series de Comprobante:
- ?empresa=ID                      - Filtrar por empresa
- ?tipo_comprobante=ID             - Filtrar por tipo de comprobante
- ?sucursal=ID                     - Filtrar por sucursal
- ?activo=true/false               - Filtrar por estado activo
- ?search=texto                    - Buscar en serie
- ?ordering=serie                  - Ordenar por campo

EJEMPLOS DE USO:

# Obtener todas las empresas activas
GET /api/core/empresas/?activo=true

# Buscar clientes por documento
GET /api/core/clientes/?search=12345678

# Obtener sucursales de una empresa específica
GET /api/core/sucursales/?empresa=1

# Obtener series de un tipo de comprobante específico
GET /api/core/series-comprobante/por_tipo/?tipo_comprobante=1

# Validar un RUC
POST /api/core/clientes/validar_documento/
{
    "tipo_documento": "ruc",
    "numero_documento": "20123456789"
}

# Importar clientes desde Excel
POST /api/core/clientes/importar/
Form-data:
- archivo: [archivo.xlsx]
- empresa: 1
- sobrescribir_existentes: true

# Obtener estadísticas de una empresa
GET /api/core/empresas/1/estadisticas/

# Obtener siguiente número de una serie
POST /api/core/series-comprobante/1/obtener_siguiente_numero/
"""