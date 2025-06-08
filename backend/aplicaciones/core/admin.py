"""
ADMIN CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Configuración del Django Admin para modelos core
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.contrib.admin import SimpleListFilter
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from datetime import datetime, timedelta

from .models import (
    Empresa, Sucursal, Cliente, Proveedor, Producto, Categoria,
    UnidadMedida, Moneda, TipoCambio, ConfiguracionSistema
)


# =============================================================================
# CONFIGURACIÓN BASE DEL ADMIN
# =============================================================================
admin.site.site_header = "FELICITA - Sistema de Facturación Electrónica"
admin.site.site_title = "FELICITA Admin"
admin.site.index_title = "Panel de Administración"


# =============================================================================
# FILTROS PERSONALIZADOS
# =============================================================================
class FechaCreacionFilter(SimpleListFilter):
    """
    Filtro personalizado para fecha de creación
    """
    title = 'Fecha de Creación'
    parameter_name = 'fecha_creacion'

    def lookups(self, request, model_admin):
        return (
            ('hoy', 'Hoy'),
            ('ayer', 'Ayer'),
            ('semana', 'Esta semana'),
            ('mes', 'Este mes'),
            ('año', 'Este año'),
        )

    def queryset(self, request, queryset):
        hoy = datetime.now().date()
        
        if self.value() == 'hoy':
            return queryset.filter(creado_en__date=hoy)
        elif self.value() == 'ayer':
            ayer = hoy - timedelta(days=1)
            return queryset.filter(creado_en__date=ayer)
        elif self.value() == 'semana':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            return queryset.filter(creado_en__date__gte=inicio_semana)
        elif self.value() == 'mes':
            inicio_mes = hoy.replace(day=1)
            return queryset.filter(creado_en__date__gte=inicio_mes)
        elif self.value() == 'año':
            inicio_año = hoy.replace(month=1, day=1)
            return queryset.filter(creado_en__date__gte=inicio_año)
        
        return queryset


class EstadoActivoFilter(SimpleListFilter):
    """
    Filtro para estado activo/inactivo
    """
    title = 'Estado'
    parameter_name = 'estado_activo'

    def lookups(self, request, model_admin):
        return (
            ('activo', 'Activos'),
            ('inactivo', 'Inactivos'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'activo':
            return queryset.filter(activo=True)
        elif self.value() == 'inactivo':
            return queryset.filter(activo=False)
        return queryset


# =============================================================================
# RECURSOS PARA IMPORT/EXPORT
# =============================================================================
class EmpresaResource(resources.ModelResource):
    """
    Recurso para importar/exportar empresas
    """
    class Meta:
        model = Empresa
        fields = (
            'ruc', 'razon_social', 'nombre_comercial', 'direccion',
            'distrito', 'provincia', 'departamento', 'telefono', 'email'
        )


class ClienteResource(resources.ModelResource):
    """
    Recurso para importar/exportar clientes
    """
    class Meta:
        model = Cliente
        fields = (
            'tipo_documento', 'numero_documento', 'nombres', 'apellido_paterno',
            'apellido_materno', 'razon_social', 'email', 'telefono'
        )


class ProductoResource(resources.ModelResource):
    """
    Recurso para importar/exportar productos
    """
    class Meta:
        model = Producto
        fields = (
            'codigo', 'nombre', 'descripcion', 'categoria__nombre',
            'unidad_medida__codigo', 'precio_venta', 'precio_compra',
            'stock_actual', 'stock_minimo'
        )


# =============================================================================
# INLINES PERSONALIZADOS
# =============================================================================
class SucursalInline(admin.TabularInline):
    """
    Inline para sucursales en empresa
    """
    model = Sucursal
    extra = 0
    fields = ('codigo', 'nombre', 'direccion', 'telefono', 'es_principal', 'activo')
    readonly_fields = ('creado_en', 'actualizado_en')


class SubcategoriaInline(admin.TabularInline):
    """
    Inline para subcategorías
    """
    model = Categoria
    fk_name = 'categoria_padre'
    extra = 0
    fields = ('codigo', 'nombre', 'descripcion', 'activo')


# =============================================================================
# ADMIN DE EMPRESA
# =============================================================================
@admin.register(Empresa)
class EmpresaAdmin(ImportExportModelAdmin):
    """
    Admin para modelo Empresa
    """
    resource_class = EmpresaResource
    list_display = [
        'ruc', 'razon_social_corta', 'nombre_comercial', 'telefono',
        'email', 'estado_badge', 'regimen_tributario', 'sucursales_count',
        'fecha_creacion'
    ]
    list_filter = [
        'estado', 'regimen_tributario', 'departamento', 'provincia',
        FechaCreacionFilter, EstadoActivoFilter
    ]
    search_fields = ['ruc', 'razon_social', 'nombre_comercial', 'email']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    inlines = [SucursalInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'ruc', 'razon_social', 'nombre_comercial', 'estado',
                'regimen_tributario'
            )
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'pagina_web')
        }),
        ('Ubicación', {
            'fields': (
                'direccion', 'distrito', 'provincia', 'departamento', 'ubigeo'
            )
        }),
        ('Configuración', {
            'fields': ('activo', 'configuracion_facturacion')
        }),
        ('Metadatos', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def razon_social_corta(self, obj):
        """Mostrar razón social abreviada"""
        if len(obj.razon_social) > 50:
            return f"{obj.razon_social[:50]}..."
        return obj.razon_social
    razon_social_corta.short_description = "Razón Social"
    
    def estado_badge(self, obj):
        """Mostrar estado con badge colorido"""
        colors = {
            'ACTIVO': 'green',
            'INACTIVO': 'red',
            'SUSPENDIDO': 'orange'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado
        )
    estado_badge.short_description = "Estado"
    
    def sucursales_count(self, obj):
        """Contar sucursales"""
        return obj.sucursales.count()
    sucursales_count.short_description = "Sucursales"
    
    def fecha_creacion(self, obj):
        """Formatear fecha de creación"""
        return obj.creado_en.strftime('%d/%m/%Y')
    fecha_creacion.short_description = "Creado"


# =============================================================================
# ADMIN DE SUCURSAL
# =============================================================================
@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    """
    Admin para modelo Sucursal
    """
    list_display = [
        'codigo', 'nombre', 'empresa_link', 'telefono', 'es_principal_badge',
        'estado_badge', 'fecha_creacion'
    ]
    list_filter = ['es_principal', 'provincia', 'departamento', EstadoActivoFilter]
    search_fields = ['codigo', 'nombre', 'empresa__razon_social', 'direccion']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('empresa', 'codigo', 'nombre', 'es_principal')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'distrito', 'provincia', 'departamento', 'ubigeo')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def empresa_link(self, obj):
        """Enlace a la empresa"""
        url = reverse('admin:core_empresa_change', args=[obj.empresa.id])
        return format_html('<a href="{}">{}</a>', url, obj.empresa.razon_social)
    empresa_link.short_description = "Empresa"
    
    def es_principal_badge(self, obj):
        """Badge para sucursal principal"""
        if obj.es_principal:
            return format_html('<span style="color: blue; font-weight: bold;">Principal</span>')
        return "No"
    es_principal_badge.short_description = "Principal"
    
    def estado_badge(self, obj):
        """Badge de estado"""
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        return format_html('<span style="color: red;">Inactivo</span>')
    estado_badge.short_description = "Estado"
    
    def fecha_creacion(self, obj):
        return obj.creado_en.strftime('%d/%m/%Y')
    fecha_creacion.short_description = "Creado"


# =============================================================================
# ADMIN DE CLIENTE
# =============================================================================
@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    """
    Admin para modelo Cliente
    """
    resource_class = ClienteResource
    list_display = [
        'numero_documento', 'nombre_completo', 'tipo_documento',
        'email', 'telefono', 'es_empresa_badge', 'estado_badge'
    ]
    list_filter = [
        'tipo_documento', 'es_empresa', 'provincia', 'departamento',
        EstadoActivoFilter, FechaCreacionFilter
    ]
    search_fields = [
        'numero_documento', 'nombres', 'apellido_paterno', 'apellido_materno',
        'razon_social', 'email', 'telefono'
    ]
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('tipo_documento', 'numero_documento')
        }),
        ('Datos Personales', {
            'fields': (
                'nombres', 'apellido_paterno', 'apellido_materno',
                'fecha_nacimiento', 'genero'
            )
        }),
        ('Datos Empresariales', {
            'fields': ('es_empresa', 'razon_social', 'nombre_comercial')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'distrito', 'provincia', 'departamento', 'ubigeo')
        }),
        ('Estado', {
            'fields': ('activo', 'observaciones')
        }),
        ('Metadatos', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def nombre_completo(self, obj):
        """Nombre completo del cliente"""
        if obj.es_empresa:
            return obj.razon_social or obj.nombre_comercial
        return f"{obj.nombres} {obj.apellido_paterno} {obj.apellido_materno}".strip()
    nombre_completo.short_description = "Nombre/Razón Social"
    
    def es_empresa_badge(self, obj):
        """Badge para indicar si es empresa"""
        if obj.es_empresa:
            return format_html('<span style="color: blue;">Empresa</span>')
        return "Persona"
    es_empresa_badge.short_description = "Tipo"
    
    def estado_badge(self, obj):
        """Badge de estado"""
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        return format_html('<span style="color: red;">Inactivo</span>')
    estado_badge.short_description = "Estado"


# =============================================================================
# ADMIN DE PROVEEDOR
# =============================================================================
@admin.register(Proveedor)
class ProveedorAdmin(ImportExportModelAdmin):
    """
    Admin para modelo Proveedor
    """
    list_display = [
        'numero_documento', 'razon_social', 'nombre_comercial',
        'categoria', 'telefono', 'email', 'dias_credito', 'estado_badge'
    ]
    list_filter = [
        'tipo_documento', 'categoria', 'provincia', 'departamento',
        EstadoActivoFilter, FechaCreacionFilter
    ]
    search_fields = [
        'numero_documento', 'razon_social', 'nombre_comercial', 'email'
    ]
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('tipo_documento', 'numero_documento')
        }),
        ('Información Comercial', {
            'fields': ('razon_social', 'nombre_comercial', 'categoria')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'contacto_principal')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'distrito', 'provincia', 'departamento', 'ubigeo')
        }),
        ('Condiciones Comerciales', {
            'fields': ('dias_credito', 'limite_credito', 'moneda_preferida')
        }),
        ('Estado', {
            'fields': ('activo', 'observaciones')
        }),
        ('Metadatos', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def estado_badge(self, obj):
        """Badge de estado"""
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        return format_html('<span style="color: red;">Inactivo</span>')
    estado_badge.short_description = "Estado"


# =============================================================================
# ADMIN DE PRODUCTO
# =============================================================================
@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    """
    Admin para modelo Producto
    """
    resource_class = ProductoResource
    list_display = [
        'codigo', 'nombre_corto', 'categoria', 'unidad_medida',
        'precio_venta_formatted', 'stock_actual_badge', 'tipo_producto',
        'igv_badge', 'estado_badge'
    ]
    list_filter = [
        'categoria', 'unidad_medida', 'tipo_producto', 'afecto_igv',
        EstadoActivoFilter, FechaCreacionFilter
    ]
    search_fields = ['codigo', 'nombre', 'descripcion', 'codigo_barra']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'categoria')
        }),
        ('Clasificación', {
            'fields': ('tipo_producto', 'unidad_medida', 'codigo_barra')
        }),
        ('Precios', {
            'fields': ('precio_venta', 'precio_compra', 'afecto_igv')
        }),
        ('Inventario', {
            'fields': ('stock_actual', 'stock_minimo', 'stock_maximo')
        }),
        ('Estado', {
            'fields': ('activo', 'observaciones')
        }),
        ('Metadatos', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def nombre_corto(self, obj):
        """Nombre abreviado"""
        if len(obj.nombre) > 40:
            return f"{obj.nombre[:40]}..."
        return obj.nombre
    nombre_corto.short_description = "Nombre"
    
    def precio_venta_formatted(self, obj):
        """Precio formateado"""
        return f"S/ {obj.precio_venta:.2f}"
    precio_venta_formatted.short_description = "Precio Venta"
    
    def stock_actual_badge(self, obj):
        """Badge de stock con colores"""
        if obj.stock_actual == 0:
            color = "red"
            text = "Sin Stock"
        elif obj.stock_actual <= obj.stock_minimo:
            color = "orange"
            text = f"{obj.stock_actual} (Bajo)"
        else:
            color = "green"
            text = str(obj.stock_actual)
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    stock_actual_badge.short_description = "Stock"
    
    def igv_badge(self, obj):
        """Badge para IGV"""
        if obj.afecto_igv:
            return format_html('<span style="color: blue;">Con IGV</span>')
        return "Sin IGV"
    igv_badge.short_description = "IGV"
    
    def estado_badge(self, obj):
        """Badge de estado"""
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        return format_html('<span style="color: red;">Inactivo</span>')
    estado_badge.short_description = "Estado"


# =============================================================================
# ADMIN DE CATEGORÍA
# =============================================================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Admin para modelo Categoría
    """
    list_display = [
        'codigo', 'nombre', 'categoria_padre', 'productos_count',
        'subcategorias_count', 'estado_badge'
    ]
    list_filter = ['categoria_padre', EstadoActivoFilter]
    search_fields = ['codigo', 'nombre', 'descripcion']
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    inlines = [SubcategoriaInline]
    
    def productos_count(self, obj):
        """Contar productos de la categoría"""
        return obj.productos.count()
    productos_count.short_description = "Productos"
    
    def subcategorias_count(self, obj):
        """Contar subcategorías"""
        return obj.subcategorias.count()
    subcategorias_count.short_description = "Subcategorías"
    
    def estado_badge(self, obj):
        """Badge de estado"""
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        return format_html('<span style="color: red;">Inactivo</span>')
    estado_badge.short_description = "Estado"


# =============================================================================
# ADMIN DE CONFIGURACIÓN
# =============================================================================
@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    """
    Admin para Unidad de Medida
    """
    list_display = ['codigo', 'nombre', 'descripcion', 'estado_badge']
    list_filter = [EstadoActivoFilter]
    search_fields = ['codigo', 'nombre']
    
    def estado_badge(self, obj):
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        return format_html('<span style="color: red;">Inactivo</span>')
    estado_badge.short_description = "Estado"


@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    """
    Admin para Moneda
    """
    list_display = ['codigo', 'nombre', 'simbolo', 'estado_badge']
    list_filter = [EstadoActivoFilter]
    search_fields = ['codigo', 'nombre']
    
    def estado_badge(self, obj):
        if obj.activo:
            return format_html('<span style="color: green;">Activo</span>')
        return format_html('<span style="color: red;">Inactivo</span>')
    estado_badge.short_description = "Estado"


@admin.register(TipoCambio)
class TipoCambioAdmin(admin.ModelAdmin):
    """
    Admin para Tipo de Cambio
    """
    list_display = [
        'fecha', 'moneda_origen', 'moneda_destino',
        'valor_compra', 'valor_venta', 'fuente'
    ]
    list_filter = ['moneda_origen', 'moneda_destino', 'fuente']
    date_hierarchy = 'fecha'
    ordering = ['-fecha']


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """
    Admin para Configuración del Sistema
    """
    list_display = ['clave', 'descripcion', 'tipo_dato', 'categoria', 'valor_preview']
    list_filter = ['tipo_dato', 'categoria']
    search_fields = ['clave', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def valor_preview(self, obj):
        """Preview del valor"""
        if len(str(obj.valor)) > 50:
            return f"{str(obj.valor)[:50]}..."
        return obj.valor
    valor_preview.short_description = "Valor"