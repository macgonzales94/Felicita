"""
FELICITA - Admin Core
Sistema de Facturación Electrónica para Perú

Configuración del Django Admin para entidades base
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Empresa, Sucursal, Cliente, Configuracion,
    TipoComprobante, SerieComprobante
)

# ===========================================
# ADMIN BASE
# ===========================================

class BaseModelAdmin(admin.ModelAdmin):
    """Admin base con funcionalidades comunes"""
    
    list_per_page = 25
    date_hierarchy = 'fecha_creacion'
    
    def get_readonly_fields(self, request, obj=None):
        """Campos solo lectura"""
        readonly = list(super().get_readonly_fields(request, obj))
        readonly.extend(['fecha_creacion', 'fecha_actualizacion'])
        return readonly
    
    def estado_activo(self, obj):
        """Mostrar estado activo con color"""
        if obj.activo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
            )
    estado_activo.short_description = 'Estado'

# ===========================================
# EMPRESA ADMIN
# ===========================================

@admin.register(Empresa)
class EmpresaAdmin(BaseModelAdmin):
    """Admin para Empresa"""
    
    list_display = [
        'ruc', 'razon_social', 'nombre_comercial', 
        'telefono', 'email', 'estado_activo', 'fecha_creacion'
    ]
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['ruc', 'razon_social', 'nombre_comercial', 'email']
    ordering = ['razon_social']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('ruc', 'razon_social', 'nombre_comercial')
        }),
        ('Datos de Contacto', {
            'fields': ('direccion_fiscal', 'ubigeo', 'telefono', 'email')
        }),
        ('Representante Legal', {
            'fields': ('representante_legal',),
            'classes': ('collapse',)
        }),
        ('Configuración SUNAT', {
            'fields': ('usuario_sol', 'clave_sol'),
            'classes': ('collapse',)
        }),
        ('Certificado Digital', {
            'fields': ('certificado_digital', 'clave_certificado'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('metadatos',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar formulario"""
        form = super().get_form(request, obj, **kwargs)
        
        # Ayuda para campos específicos
        if 'ruc' in form.base_fields:
            form.base_fields['ruc'].help_text = 'RUC de 11 dígitos con dígito verificador válido'
        
        return form

# ===========================================
# SUCURSAL ADMIN
# ===========================================

class SucursalInline(admin.TabularInline):
    """Inline para Sucursales en Empresa"""
    model = Sucursal
    extra = 0
    fields = ['codigo', 'nombre', 'direccion', 'telefono', 'es_principal', 'activo']

@admin.register(Sucursal)
class SucursalAdmin(BaseModelAdmin):
    """Admin para Sucursal"""
    
    list_display = [
        'empresa_ruc', 'codigo', 'nombre', 'telefono', 
        'es_principal_display', 'estado_activo', 'fecha_creacion'
    ]
    list_filter = ['empresa', 'es_principal', 'activo', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'direccion', 'empresa__razon_social']
    ordering = ['empresa', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'codigo', 'nombre', 'es_principal')
        }),
        ('Datos de Contacto', {
            'fields': ('direccion', 'ubigeo', 'telefono', 'email')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    def empresa_ruc(self, obj):
        """Mostrar RUC de la empresa"""
        return f"{obj.empresa.ruc} - {obj.empresa.razon_social}"
    empresa_ruc.short_description = 'Empresa'
    
    def es_principal_display(self, obj):
        """Mostrar si es principal con color"""
        if obj.es_principal:
            return format_html(
                '<span style="color: blue; font-weight: bold;">★ Principal</span>'
            )
        return '-'
    es_principal_display.short_description = 'Principal'

# ===========================================
# CLIENTE ADMIN
# ===========================================

@admin.register(Cliente)
class ClienteAdmin(BaseModelAdmin):
    """Admin para Cliente"""
    
    list_display = [
        'numero_documento', 'razon_social', 'tipo_documento_display',
        'email', 'telefono', 'limite_credito', 'estado_activo', 'fecha_creacion'
    ]
    list_filter = [
        'empresa', 'tipo_documento', 'activo', 'fecha_creacion'
    ]
    search_fields = [
        'numero_documento', 'razon_social', 'nombre_comercial', 
        'email', 'empresa__razon_social'
    ]
    ordering = ['razon_social']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'tipo_documento', 'numero_documento', 'razon_social', 'nombre_comercial')
        }),
        ('Datos de Contacto', {
            'fields': ('direccion', 'ubigeo', 'telefono', 'email', 'contacto_principal')
        }),
        ('Información Comercial', {
            'fields': ('limite_credito', 'dias_credito'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('metadatos',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    def tipo_documento_display(self, obj):
        """Mostrar tipo de documento con icono"""
        iconos = {
            'dni': '🆔',
            'ruc': '🏢',
            'pasaporte': '📔',
            'carnet_extranjeria': '🛂'
        }
        icono = iconos.get(obj.tipo_documento, '📄')
        return f"{icono} {obj.get_tipo_documento_display()}"
    tipo_documento_display.short_description = 'Tipo Documento'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related('empresa')

# ===========================================
# CONFIGURACIÓN ADMIN
# ===========================================

class ConfiguracionInline(admin.StackedInline):
    """Inline para Configuración en Empresa"""
    model = Configuracion
    extra = 0
    fieldsets = (
        ('Configuración Fiscal', {
            'fields': ('igv_porcentaje', 'moneda_defecto')
        }),
        ('Configuración Facturación', {
            'fields': ('numeracion_automatica', 'envio_automatico_sunat', 'envio_email_cliente')
        }),
        ('Configuración Inventario', {
            'fields': ('metodo_valuacion', 'control_stock')
        }),
        ('Configuración Reportes', {
            'fields': ('formato_fecha',)
        }),
        ('Parámetros Adicionales', {
            'fields': ('parametros',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Configuracion)
class ConfiguracionAdmin(BaseModelAdmin):
    """Admin para Configuración"""
    
    list_display = [
        'empresa_ruc', 'igv_porcentaje', 'moneda_defecto',
        'numeracion_automatica', 'control_stock', 'estado_activo'
    ]
    list_filter = ['moneda_defecto', 'metodo_valuacion', 'activo']
    search_fields = ['empresa__razon_social', 'empresa__ruc']
    ordering = ['empresa']
    
    fieldsets = (
        ('Empresa', {
            'fields': ('empresa',)
        }),
        ('Configuración Fiscal', {
            'fields': ('igv_porcentaje', 'moneda_defecto')
        }),
        ('Configuración Facturación', {
            'fields': ('numeracion_automatica', 'envio_automatico_sunat', 'envio_email_cliente')
        }),
        ('Configuración Inventario', {
            'fields': ('metodo_valuacion', 'control_stock')
        }),
        ('Configuración Reportes', {
            'fields': ('formato_fecha',)
        }),
        ('Parámetros Adicionales', {
            'fields': ('parametros',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    def empresa_ruc(self, obj):
        """Mostrar RUC de la empresa"""
        return f"{obj.empresa.ruc} - {obj.empresa.razon_social}"
    empresa_ruc.short_description = 'Empresa'

# ===========================================
# TIPO COMPROBANTE ADMIN
# ===========================================

@admin.register(TipoComprobante)
class TipoComprobanteAdmin(BaseModelAdmin):
    """Admin para Tipo de Comprobante"""
    
    list_display = [
        'codigo', 'nombre', 'requiere_serie', 'formato_serie',
        'total_series_display', 'estado_activo', 'fecha_creacion'
    ]
    list_filter = ['requiere_serie', 'activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Configuración Serie', {
            'fields': ('requiere_serie', 'formato_serie')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    def total_series_display(self, obj):
        """Mostrar total de series con enlace"""
        total = obj.seriecomprobante_set.filter(activo=True).count()
        if total > 0:
            url = reverse('admin:core_seriecomprobante_changelist') + f'?tipo_comprobante__id__exact={obj.id}'
            return format_html('<a href="{}">{} series</a>', url, total)
        return '0 series'
    total_series_display.short_description = 'Series Activas'

# ===========================================
# SERIE COMPROBANTE ADMIN
# ===========================================

class SerieComprobanteInline(admin.TabularInline):
    """Inline para Series en Empresa"""
    model = SerieComprobante
    extra = 0
    fields = ['tipo_comprobante', 'serie', 'numero_actual', 'sucursal', 'activo']

@admin.register(SerieComprobante)
class SerieComprobanteAdmin(BaseModelAdmin):
    """Admin para Serie de Comprobante"""
    
    list_display = [
        'empresa_ruc', 'tipo_codigo', 'serie', 'numero_actual',
        'siguiente_numero_display', 'sucursal_nombre', 'estado_activo', 'fecha_creacion'
    ]
    list_filter = [
        'empresa', 'tipo_comprobante', 'sucursal', 'activo', 'fecha_creacion'
    ]
    search_fields = [
        'serie', 'empresa__razon_social', 'tipo_comprobante__nombre'
    ]
    ordering = ['empresa', 'tipo_comprobante__codigo', 'serie']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'tipo_comprobante', 'serie')
        }),
        ('Numeración', {
            'fields': ('numero_actual',)
        }),
        ('Configuración Adicional', {
            'fields': ('sucursal',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    def empresa_ruc(self, obj):
        """Mostrar RUC de la empresa"""
        return f"{obj.empresa.ruc}"
    empresa_ruc.short_description = 'RUC'
    
    def tipo_codigo(self, obj):
        """Mostrar código del tipo"""
        return f"{obj.tipo_comprobante.codigo} - {obj.tipo_comprobante.nombre}"
    tipo_codigo.short_description = 'Tipo'
    
    def siguiente_numero_display(self, obj):
        """Mostrar siguiente número"""
        siguiente = obj.numero_actual + 1
        return format_html(
            '<span style="color: blue; font-weight: bold;">{:08d}</span>',
            siguiente
        )
    siguiente_numero_display.short_description = 'Siguiente #'
    
    def sucursal_nombre(self, obj):
        """Mostrar nombre de sucursal"""
        return obj.sucursal.nombre if obj.sucursal else '-'
    sucursal_nombre.short_description = 'Sucursal'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'empresa', 'tipo_comprobante', 'sucursal'
        )

# ===========================================
# PERSONALIZACIÓN ADMIN SITE
# ===========================================

# Agregar inlines a EmpresaAdmin
EmpresaAdmin.inlines = [SucursalInline, ConfiguracionInline, SerieComprobanteInline]

# Personalizar títulos del admin
admin.site.site_header = "FELICITA - Administración"
admin.site.site_title = "FELICITA Admin"
admin.site.index_title = "Panel de Administración del Sistema"

# ===========================================
# ACCIONES PERSONALIZADAS
# ===========================================

def activar_registros(modeladmin, request, queryset):
    """Acción para activar múltiples registros"""
    updated = queryset.update(activo=True)
    modeladmin.message_user(
        request,
        f"{updated} registro(s) activado(s) correctamente."
    )
activar_registros.short_description = "Activar registros seleccionados"

def desactivar_registros(modeladmin, request, queryset):
    """Acción para desactivar múltiples registros"""
    updated = queryset.update(activo=False)
    modeladmin.message_user(
        request,
        f"{updated} registro(s) desactivado(s) correctamente."
    )
desactivar_registros.short_description = "Desactivar registros seleccionados"

# Agregar acciones a todos los admins
for admin_class in [EmpresaAdmin, SucursalAdmin, ClienteAdmin, 
                   ConfiguracionAdmin, TipoComprobanteAdmin, SerieComprobanteAdmin]:
    admin_class.actions = [activar_registros, desactivar_registros]