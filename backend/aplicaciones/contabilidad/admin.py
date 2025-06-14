"""
ADMIN CONTABILIDAD - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Configuración del panel de administración para módulo contable
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe


from aplicaciones.contabilidad.models import (
    PlanCuentas, CuentaContable, AsientoContable, DetalleAsientoContable,
    PeriodoContable, BalanceComprobacion, CuentaPorCobrar, CuentaPorPagar,
    LibroMayor
)


class DetalleAsientoInline(admin.TabularInline):
    """Inline para detalles de asientos"""
    model = DetalleAsientoContable
    extra = 2
    fields = [
        'numero_linea', 'cuenta', 'concepto', 'debe', 'haber',
        'centro_gasto', 'moneda', 'tipo_cambio'
    ]
    
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 2


@admin.register(PlanCuentas)
class PlanCuentasAdmin(admin.ModelAdmin):
    """Admin para planes de cuentas"""
    list_display = ['codigo', 'nombre', 'tipo_plan', 'anio_vigencia', 'es_plan_activo', 'empresa']
    list_filter = ['tipo_plan', 'anio_vigencia', 'es_plan_activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['empresa', 'anio_vigencia', 'codigo']


@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    """Admin para cuentas contables"""
    list_display = [
        'codigo', 'nombre', 'nivel', 'naturaleza', 'tipo_cuenta',
        'acepta_movimientos', 'plan_cuentas'
    ]
    list_filter = ['nivel', 'naturaleza', 'tipo_cuenta', 'acepta_movimientos']
    search_fields = ['codigo', 'nombre']
    ordering = ['plan_cuentas', 'codigo']
    list_editable = ['acepta_movimientos']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('plan_cuentas', 'codigo', 'nombre', 'descripcion')
        }),
        ('Jerarquía', {
            'fields': ('cuenta_padre', 'nivel')
        }),
        ('Características Contables', {
            'fields': ('naturaleza', 'tipo_cuenta')
        }),
        ('Control', {
            'fields': (
                'acepta_movimientos', 'requiere_centro_gasto',
                'requiere_documento', 'requiere_tercero'
            )
        })
    )


@admin.register(PeriodoContable)
class PeriodoContableAdmin(admin.ModelAdmin):
    """Admin para períodos contables"""
    list_display = [
        'nombre', 'año', 'mes', 'fecha_inicio', 'fecha_fin',
        'estado_badge', 'es_periodo_principal'
    ]
    list_filter = ['año', 'estado', 'es_periodo_principal']
    search_fields = ['nombre', 'año']
    ordering = ['-año', '-mes']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'año', 'mes', 'nombre')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Estado', {
            'fields': ('estado', 'es_periodo_principal', 'permite_reapertura')
        }),
        ('Cierre', {
            'fields': ('fecha_cierre', 'usuario_cierre', 'observaciones_cierre'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['fecha_cierre', 'usuario_cierre']
    
    def estado_badge(self, obj):
        colors = {
            'abierto': 'green',
            'cerrado': 'red',
            'auditoria': 'orange',
            'bloqueado': 'gray'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado.upper()
        )
    estado_badge.short_description = 'Estado'


@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    """Admin para asientos contables"""
    list_display = [
        'numero_asiento', 'fecha_asiento', 'tipo_asiento',
        'concepto_corto', 'total_debe', 'total_haber', 'estado_badge'
    ]
    list_filter = ['fecha_asiento', 'tipo_asiento', 'estado', 'moneda']
    search_fields = ['numero_asiento', 'concepto', 'documento_referencia']
    date_hierarchy = 'fecha_asiento'
    ordering = ['-fecha_asiento', '-numero_asiento']
    inlines = [DetalleAsientoInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('numero_asiento', 'fecha_asiento', 'tipo_asiento')
        }),
        ('Descripción', {
            'fields': ('concepto', 'documento_referencia')
        }),
        ('Totales', {
            'fields': ('total_debe', 'total_haber', 'moneda', 'tipo_cambio')
        }),
        ('Control', {
            'fields': ('estado', 'periodo', 'usuario_creacion'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['total_debe', 'total_haber', 'usuario_creacion']
    
    def concepto_corto(self, obj):
        return obj.concepto[:50] + "..." if len(obj.concepto) > 50 else obj.concepto
    concepto_corto.short_description = 'Concepto'
    
    def estado_badge(self, obj):
        colors = {
            'borrador': 'orange',
            'contabilizado': 'green',
            'anulado': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado.upper()
        )
    estado_badge.short_description = 'Estado'


@admin.register(BalanceComprobacion)
class BalanceComprobacionAdmin(admin.ModelAdmin):
    """Admin para balances de comprobación"""
    list_display = [
        'cuenta_codigo', 'cuenta_nombre', 'periodo', 'fecha_desde', 'fecha_hasta',
        'saldo_final_debe', 'saldo_final_haber', 'es_balance_oficial'
    ]
    list_filter = [
        'fecha_desde', 'fecha_hasta', 'periodo', 'es_balance_oficial',
        'cuenta__tipo_cuenta'
    ]
    search_fields = ['cuenta__codigo', 'cuenta__nombre']
    ordering = ['cuenta__codigo', 'fecha_desde']
    
    def cuenta_codigo(self, obj):
        return obj.cuenta.codigo
    cuenta_codigo.short_description = 'Código Cuenta'
    
    def cuenta_nombre(self, obj):
        return obj.cuenta.nombre
    cuenta_nombre.short_description = 'Nombre Cuenta'


@admin.register(CuentaPorCobrar)
class CuentaPorCobrarAdmin(admin.ModelAdmin):
    """Admin para cuentas por cobrar"""
    list_display = [
        'cliente', 'numero_documento', 'fecha_emision', 'fecha_vencimiento',
        'monto_original', 'monto_pendiente', 'estado_badge', 'dias_vencimiento'
    ]
    list_filter = ['estado', 'tipo_documento', 'moneda', 'fecha_vencimiento']
    search_fields = ['cliente__razon_social', 'numero_documento']
    date_hierarchy = 'fecha_vencimiento'
    ordering = ['fecha_vencimiento', 'cliente__razon_social']
    
    def estado_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'PARCIAL': 'blue',
            'CANCELADO': 'green',
            'VENCIDO': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado
        )
    estado_badge.short_description = 'Estado'
    
    def dias_vencimiento(self, obj):
        from datetime import date
        if obj.fecha_vencimiento and obj.estado in ['PENDIENTE', 'PARCIAL']:
            dias = (date.today() - obj.fecha_vencimiento).days
            if dias > 0:
                return format_html('<span style="color: red;">{} días</span>', dias)
            elif dias < 0:
                return format_html('<span style="color: green;">{} días</span>', abs(dias))
            else:
                return 'Vence hoy'
        return '-'
    dias_vencimiento.short_description = 'Días Vencimiento'


@admin.register(CuentaPorPagar)
class CuentaPorPagarAdmin(admin.ModelAdmin):
    """Admin para cuentas por pagar"""
    list_display = [
        'proveedor_nombre', 'numero_documento', 'fecha_emision', 'fecha_vencimiento',
        'monto_original', 'monto_pendiente', 'estado_badge', 'dias_vencimiento'
    ]
    list_filter = ['estado', 'tipo_documento', 'moneda', 'fecha_vencimiento']
    search_fields = ['proveedor_nombre', 'proveedor_documento', 'numero_documento']
    date_hierarchy = 'fecha_vencimiento'
    ordering = ['fecha_vencimiento', 'proveedor_nombre']
    
    def estado_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'PARCIAL': 'blue',
            'CANCELADO': 'green',
            'VENCIDO': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado
        )
    estado_badge.short_description = 'Estado'
    
    def dias_vencimiento(self, obj):
        from datetime import date
        if obj.fecha_vencimiento and obj.estado in ['PENDIENTE', 'PARCIAL']:
            dias = (date.today() - obj.fecha_vencimiento).days
            if dias > 0:
                return format_html('<span style="color: red;">{} días</span>', dias)
            elif dias < 0:
                return format_html('<span style="color: green;">{} días</span>', abs(dias))
            else:
                return 'Vence hoy'
        return '-'
    dias_vencimiento.short_description = 'Días Vencimiento'


# =============================================================================
# URLs PARA FACTURACIÓN (backend/aplicaciones/facturacion/urls.py)
# =============================================================================

"""
# Agregar estas líneas al urls.py existente de facturación:

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FacturaViewSet, BoletaViewSet, NotaCreditoViewSet, NotaDebitoViewSet,
    GuiaRemisionViewSet, SerieComprobanteViewSet
)

router = DefaultRouter()
router.register(r'facturas', FacturaViewSet)
router.register(r'boletas', BoletaViewSet)
router.register(r'notas-credito', NotaCreditoViewSet)
router.register(r'notas-debito', NotaDebitoViewSet)  # NUEVA LÍNEA
router.register(r'guias-remision', GuiaRemisionViewSet)  # NUEVA LÍNEA
router.register(r'series', SerieComprobanteViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # URLs adicionales...
]
"""


# =============================================================================
# URLs PARA CONTABILIDAD (backend/aplicaciones/contabilidad/urls.py)
# =============================================================================

"""
# Crear nuevo archivo backend/aplicaciones/contabilidad/urls.py:

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlanCuentasViewSet, CuentaContableViewSet, AsientoContableViewSet,
    PeriodoContableViewSet, BalanceComprobacionViewSet, CuentaPorCobrarViewSet,
    CuentaPorPagarViewSet, LibroMayorViewSet
)

router = DefaultRouter()
router.register(r'planes-cuentas', PlanCuentasViewSet)
router.register(r'cuentas', CuentaContableViewSet)
router.register(r'asientos', AsientoContableViewSet)
router.register(r'periodos', PeriodoContableViewSet)
router.register(r'balances', BalanceComprobacionViewSet)
router.register(r'cuentas-cobrar', CuentaPorCobrarViewSet)
router.register(r'cuentas-pagar', CuentaPorPagarViewSet)
router.register(r'libro-mayor', LibroMayorViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
"""


# =============================================================================
# SETTINGS ADICIONALES
# =============================================================================

"""
# Agregar en backend/config/settings/base.py:

# Configuración específica de SUNAT
SUNAT_CONFIG = {
    'igv_tasa': 0.18,  # 18% IGV
    'monedas_soportadas': ['PEN', 'USD', 'EUR'],
    'tipos_documento': {
        'DNI': '1',
        'CE': '4', 
        'RUC': '6',
        'PASSPORT': '7'
    },
    'codigos_afectacion_igv': {
        'gravado': '10',
        'exonerado': '20',
        'inafecto': '30',
        'exportacion': '40'
    }
}

# Configuración de Nubefact (si aplica)
NUBEFACT_CONFIG = {
    'auto_send': True,  # Envío automático a SUNAT
    'retry_attempts': 3,  # Intentos de reenvío
    'timeout': 30,  # Timeout en segundos
}

# Configuración contable
CONTABILIDAD_CONFIG = {
    'plan_cuentas_default': 'PCGE',
    'generar_asientos_automaticos': True,
    'permitir_edicion_asientos_contabilizados': False,
    'periodo_actual_auto': True
}
"""