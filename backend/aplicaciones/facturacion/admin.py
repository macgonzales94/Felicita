# =============================================================================
# ADMIN PARA FACTURACIÓN (backend/aplicaciones/facturacion/admin.py)
# =============================================================================

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SerieComprobante, Factura, Boleta, NotaCredito, NotaDebito, GuiaRemision,
    ItemFactura, ItemBoleta, ItemNotaCredito, ItemNotaDebito, ItemGuiaRemision
)


# Inlines para Items
class ItemFacturaInline(admin.TabularInline):
    """Inline para items de facturas"""
    model = ItemFactura
    extra = 1
    fields = [
        'numero_item', 'producto', 'descripcion', 'unidad_medida',
        'cantidad', 'precio_unitario', 'descuento_unitario',
        'valor_venta', 'igv', 'precio_total'
    ]
    readonly_fields = ['valor_venta', 'igv', 'precio_total']


class ItemBoletaInline(admin.TabularInline):
    """Inline para items de boletas"""
    model = ItemBoleta
    extra = 1
    fields = [
        'numero_item', 'producto', 'descripcion', 'unidad_medida',
        'cantidad', 'precio_unitario', 'descuento_unitario',
        'valor_venta', 'igv', 'precio_total'
    ]
    readonly_fields = ['valor_venta', 'igv', 'precio_total']


class ItemNotaCreditoInline(admin.TabularInline):
    """Inline para items de notas de crédito"""
    model = ItemNotaCredito
    extra = 1
    fields = [
        'numero_item', 'producto', 'descripcion', 'unidad_medida',
        'cantidad', 'precio_unitario', 'descuento_unitario',
        'valor_venta', 'igv', 'precio_total'
    ]
    readonly_fields = ['valor_venta', 'igv', 'precio_total']


class ItemNotaDebitoInline(admin.TabularInline):
    """Inline para items de notas de débito"""
    model = ItemNotaDebito
    extra = 1
    fields = [
        'numero_item', 'producto', 'descripcion', 'unidad_medida',
        'cantidad', 'precio_unitario', 'descuento_unitario',
        'valor_venta', 'igv', 'precio_total'
    ]
    readonly_fields = ['valor_venta', 'igv', 'precio_total']


class ItemGuiaRemisionInline(admin.TabularInline):
    """Inline para items de guías de remisión"""
    model = ItemGuiaRemision
    extra = 1
    fields = [
        'numero_item', 'producto', 'descripcion', 'unidad_medida',
        'cantidad', 'peso_unitario', 'peso_total'
    ]
    readonly_fields = ['peso_total']


# Admins principales
@admin.register(SerieComprobante)
class SerieComprobanteAdmin(admin.ModelAdmin):
    """Admin para series de comprobantes"""
    list_display = [
        'serie', 'tipo_comprobante', 'numero_actual', 'numero_maximo',
        'activa', 'punto_venta', 'empresa'
    ]
    list_filter = ['tipo_comprobante', 'activa', 'empresa']
    search_fields = ['serie', 'tipo_comprobante']
    list_editable = ['activa', 'numero_maximo']
    ordering = ['empresa', 'tipo_comprobante', 'serie']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'tipo_comprobante', 'serie', 'punto_venta')
        }),
        ('Numeración', {
            'fields': ('numero_actual', 'numero_maximo', 'activa')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    """Admin para facturas"""
    list_display = [
        'numero_completo', 'fecha_emision', 'cliente', 'total',
        'moneda', 'estado_sunat_badge', 'condicion_pago'
    ]
    list_filter = [
        'fecha_emision', 'estado_sunat', 'moneda', 'condicion_pago',
        'sujeta_detraccion'
    ]
    search_fields = [
        'numero', 'serie_comprobante__serie', 'cliente__razon_social',
        'cliente__numero_documento'
    ]
    date_hierarchy = 'fecha_emision'
    ordering = ['-fecha_emision', '-numero']
    inlines = [ItemFacturaInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('serie_comprobante', 'numero', 'fecha_emision', 'fecha_vencimiento')
        }),
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Moneda y Cambio', {
            'fields': ('moneda', 'tipo_cambio')
        }),
        ('Totales', {
            'fields': ('subtotal', 'descuento_global', 'igv', 'total'),
            'classes': ('collapse',)
        }),
        ('Condiciones', {
            'fields': ('condicion_pago', 'orden_compra')
        }),
        ('Detracción', {
            'fields': (
                'sujeta_detraccion', 'codigo_detraccion',
                'porcentaje_detraccion', 'monto_detraccion'
            ),
            'classes': ('collapse',)
        }),
        ('SUNAT', {
            'fields': ('estado_sunat', 'nubefact_id', 'hash_cpe'),
            'classes': ('collapse',)
        }),
        ('Otros', {
            'fields': ('observaciones',)
        })
    )
    readonly_fields = ['numero', 'subtotal', 'igv', 'total', 'monto_detraccion']
    
    def numero_completo(self, obj):
        return f"{obj.serie_comprobante.serie}-{obj.numero:08d}"
    numero_completo.short_description = 'Número Completo'
    
    def estado_sunat_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'ACEPTADO': 'green',
            'RECHAZADO': 'red',
            'ANULADO': 'gray'
        }
        color = colors.get(obj.estado_sunat, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado_sunat
        )
    estado_sunat_badge.short_description = 'Estado SUNAT'


@admin.register(Boleta)
class BoletaAdmin(admin.ModelAdmin):
    """Admin para boletas"""
    list_display = [
        'numero_completo', 'fecha_emision', 'cliente', 'total',
        'moneda', 'estado_sunat_badge'
    ]
    list_filter = ['fecha_emision', 'estado_sunat', 'moneda']
    search_fields = [
        'numero', 'serie_comprobante__serie', 'cliente__razon_social',
        'cliente__numero_documento'
    ]
    date_hierarchy = 'fecha_emision'
    ordering = ['-fecha_emision', '-numero']
    inlines = [ItemBoletaInline]
    
    def numero_completo(self, obj):
        return f"{obj.serie_comprobante.serie}-{obj.numero:08d}"
    numero_completo.short_description = 'Número Completo'
    
    def estado_sunat_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'ACEPTADO': 'green',
            'RECHAZADO': 'red',
            'ANULADO': 'gray'
        }
        color = colors.get(obj.estado_sunat, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado_sunat
        )
    estado_sunat_badge.short_description = 'Estado SUNAT'


@admin.register(NotaCredito)
class NotaCreditoAdmin(admin.ModelAdmin):
    """Admin para notas de crédito"""
    list_display = [
        'numero_completo', 'fecha_emision', 'cliente', 'total',
        'codigo_motivo', 'documento_modificado', 'estado_sunat_badge'
    ]
    list_filter = ['fecha_emision', 'estado_sunat', 'codigo_motivo', 'tipo_documento_modificado']
    search_fields = [
        'numero', 'serie_comprobante__serie', 'cliente__razon_social',
        'numero_documento_modificado'
    ]
    date_hierarchy = 'fecha_emision'
    ordering = ['-fecha_emision', '-numero']
    inlines = [ItemNotaCreditoInline]
    
    def numero_completo(self, obj):
        return f"{obj.serie_comprobante.serie}-{obj.numero:08d}"
    numero_completo.short_description = 'Número Completo'
    
    def documento_modificado(self, obj):
        return f"{obj.tipo_documento_modificado}-{obj.numero_documento_modificado}"
    documento_modificado.short_description = 'Doc. Modificado'
    
    def estado_sunat_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'ACEPTADO': 'green',
            'RECHAZADO': 'red',
            'ANULADO': 'gray'
        }
        color = colors.get(obj.estado_sunat, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado_sunat
        )
    estado_sunat_badge.short_description = 'Estado SUNAT'


@admin.register(NotaDebito)
class NotaDebitoAdmin(admin.ModelAdmin):
    """Admin para notas de débito"""
    list_display = [
        'numero_completo', 'fecha_emision', 'cliente', 'total',
        'codigo_motivo', 'documento_modificado', 'estado_sunat_badge'
    ]
    list_filter = ['fecha_emision', 'estado_sunat', 'codigo_motivo', 'tipo_documento_modificado']
    search_fields = [
        'numero', 'serie_comprobante__serie', 'cliente__razon_social',
        'numero_documento_modificado'
    ]
    date_hierarchy = 'fecha_emision'
    ordering = ['-fecha_emision', '-numero']
    inlines = [ItemNotaDebitoInline]
    
    def numero_completo(self, obj):
        return f"{obj.serie_comprobante.serie}-{obj.numero:08d}"
    numero_completo.short_description = 'Número Completo'
    
    def documento_modificado(self, obj):
        return f"{obj.tipo_documento_modificado}-{obj.numero_documento_modificado}"
    documento_modificado.short_description = 'Doc. Modificado'
    
    def estado_sunat_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'ACEPTADO': 'green',
            'RECHAZADO': 'red',
            'ANULADO': 'gray'
        }
        color = colors.get(obj.estado_sunat, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado_sunat
        )
    estado_sunat_badge.short_description = 'Estado SUNAT'


@admin.register(GuiaRemision)
class GuiaRemisionAdmin(admin.ModelAdmin):
    """Admin para guías de remisión"""
    list_display = [
        'serie_numero', 'fecha_emision', 'fecha_inicio_traslado',
        'tipo_traslado', 'transportista_nombre', 'peso_bruto_total',
        'estado_sunat_badge'
    ]
    list_filter = [
        'fecha_emision', 'fecha_inicio_traslado', 'tipo_traslado',
        'modalidad_transporte', 'estado_sunat'
    ]
    search_fields = [
        'serie_numero', 'transportista_ruc', 'transportista_nombre',
        'vehiculo_placa', 'conductor_nombre'
    ]
    date_hierarchy = 'fecha_emision'
    ordering = ['-fecha_emision', '-fecha_inicio_traslado']
    inlines = [ItemGuiaRemisionInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('empresa', 'serie_numero', 'fecha_emision')
        }),
        ('Traslado', {
            'fields': (
                'tipo_traslado', 'modalidad_transporte', 'fecha_inicio_traslado',
                'peso_bruto_total'
            )
        }),
        ('Origen y Destino', {
            'fields': (
                'direccion_origen', 'ubigeo_origen',
                'direccion_destino', 'ubigeo_destino'
            )
        }),
        ('Transportista', {
            'fields': ('transportista_ruc', 'transportista_nombre')
        }),
        ('Vehículo y Conductor', {
            'fields': (
                'vehiculo_placa', 'conductor_licencia', 'conductor_nombre'
            )
        }),
        ('SUNAT', {
            'fields': ('estado_sunat', 'nubefact_id', 'hash_cpe'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        })
    )
    readonly_fields = ['peso_bruto_total']
    
    def estado_sunat_badge(self, obj):
        colors = {
            'PENDIENTE': 'orange',
            'ACEPTADO': 'green',
            'RECHAZADO': 'red',
            'ANULADO': 'gray'
        }
        color = colors.get(obj.estado_sunat, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado_sunat
        )
    estado_sunat_badge.short_description = 'Estado SUNAT'

