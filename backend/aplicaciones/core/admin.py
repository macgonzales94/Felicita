"""
ADMIN CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Configuración del admin de Django para el módulo core
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.contrib.admin import SimpleListFilter
from .models import (
    Empresa, Cliente, Proveedor, CategoriaProducto,
    Producto, ConfiguracionSistema
)


# =============================================================================
# CONFIGURACIÓN BASE DEL ADMIN
# =============================================================================
class BaseModelAdmin(admin.ModelAdmin):
    """
    Configuración base para todos los modelos del admin
    """
    
    # Campos de solo lectura comunes
    readonly_fields = ['id', 'creado_en', 'actualizado_en']
    
    # Campos para mostrar en listas
    list_display_base = ['activo', 'creado_en', 'actualizado_en']
    
    # Filtros comunes
    list_filter_base = ['activo', 'creado_en', 'actualizado_en']
    
    # Configuración de paginación
    list_per_page = 25
    list_max_show_all = 100
    
    def get_readonly_fields(self, request, obj=None):
        """Campos de solo lectura dinámicos"""
        fields = list(self.readonly_fields)
        if obj:  # Editando
            fields.extend(['creado_en', 'actualizado_en'])
        return fields
    
    def save_model(self, request, obj, form, change):
        """Guardar modelo con información del usuario"""
        super().save_model(request, obj, form, change)


# =============================================================================
# FILTROS PERSONALIZADOS
# =============================================================================
class TieneEmailFilter(SimpleListFilter):
    """Filtro para elementos con/sin email"""
    title = 'Tiene Email'
    parameter_name = 'tiene_email'
    
    def lookups(self, request, model_admin):
        return (
            ('si', 'Con Email'),
            ('no', 'Sin Email'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.exclude(email__isnull=True).exclude(email='')
        if self.value() == 'no':
            return queryset.filter(email__isnull=True) | queryset.filter(email='')
        return queryset


class TieneTelefonoFilter(SimpleListFilter):
    """Filtro para elementos con/sin teléfono"""
    title = 'Tiene Teléfono'
    parameter_name = 'tiene_telefono'
    
    def lookups(self, request, model_admin):
        return (
            ('si', 'Con Teléfono'),
            ('no', 'Sin Teléfono'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.exclude(telefono__isnull=True).exclude(telefono='')
        if self.value() == 'no':
            return queryset.filter(telefono__isnull=True) | queryset.filter(telefono='')
        return queryset


# =============================================================================
# ADMIN EMPRESA
# =============================================================================
@admin.register(Empresa)
class EmpresaAdmin(BaseModelAdmin):
    """
    Configuración del admin para Empresa
    """
    
    list_display = [
        'ruc', 'razon_social', 'nombre_comercial', 'email',
        'regimen_tributario', 'moneda_base', 'activo'
    ]
    
    list_filter = [
        'regimen_tributario', 'moneda_base', 'plan_cuentas'
    ] + BaseModelAdmin.list_filter_base
    
    search_fields = [
        'ruc', 'razon_social', 'nombre_comercial', 'email'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'ruc', 'razon_social', 'nombre_comercial', 'logo'
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion', 'ubigeo', 'distrito', 'provincia', 'departamento'
            )
        }),
        ('Contacto', {
            'fields': (
                'telefono', 'email', 'pagina_web'
            )
        }),
        ('Configuración Contable', {
            'fields': (
                'plan_cuentas', 'moneda_base', 'regimen_tributario'
            )
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request)


# =============================================================================
# ADMIN CLIENTE
# =============================================================================
@admin.register(Cliente)
class ClienteAdmin(BaseModelAdmin):
    """
    Configuración del admin para Cliente
    """
    
    list_display = [
        'numero_documento', 'get_nombre_completo', 'tipo_cliente',
        'email', 'telefono', 'limite_credito', 'bloqueado', 'activo'
    ]
    
    list_filter = [
        'tipo_documento', 'tipo_cliente', 'bloqueado',
        TieneEmailFilter, TieneTelefonoFilter,
        'distrito', 'provincia'
    ] + BaseModelAdmin.list_filter_base
    
    search_fields = [
        'numero_documento', 'razon_social', 'nombres',
        'apellido_paterno', 'apellido_materno', 'email'
    ]
    
    list_editable = ['bloqueado']
    
    fieldsets = (
        ('Identificación', {
            'fields': (
                'tipo_documento', 'numero_documento', 'tipo_cliente'
            )
        }),
        ('Datos Personales/Empresariales', {
            'fields': (
                'razon_social', 'nombres', 'apellido_paterno', 'apellido_materno'
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion', 'ubigeo', 'distrito', 'provincia', 'departamento'
            )
        }),
        ('Contacto', {
            'fields': (
                'telefono', 'email'
            )
        }),
        ('Configuración Comercial', {
            'fields': (
                'limite_credito', 'dias_credito', 'descuento_maximo'
            )
        }),
        ('Estado', {
            'fields': (
                'bloqueado', 'fecha_bloqueo', 'motivo_bloqueo', 'activo'
            )
        }),
        ('Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def get_nombre_completo(self, obj):
        """Mostrar nombre completo"""
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request)
    
    actions = ['bloquear_clientes', 'desbloquear_clientes']
    
    def bloquear_clientes(self, request, queryset):
        """Acción para bloquear clientes"""
        updated = queryset.update(bloqueado=True)
        self.message_user(request, f'{updated} clientes bloqueados.')
    bloquear_clientes.short_description = 'Bloquear clientes seleccionados'
    
    def desbloquear_clientes(self, request, queryset):
        """Acción para desbloquear clientes"""
        updated = queryset.update(bloqueado=False, motivo_bloqueo='')
        self.message_user(request, f'{updated} clientes desbloqueados.')
    desbloquear_clientes.short_description = 'Desbloquear clientes seleccionados'


# =============================================================================
# ADMIN PROVEEDOR
# =============================================================================
@admin.register(Proveedor)
class ProveedorAdmin(BaseModelAdmin):
    """
    Configuración del admin para Proveedor
    """
    
    list_display = [
        'ruc', 'razon_social', 'nombre_comercial',
        'contacto_principal', 'telefono', 'email',
        'dias_pago', 'activo_comercial', 'activo'
    ]
    
    list_filter = [
        'activo_comercial', TieneEmailFilter, TieneTelefonoFilter
    ] + BaseModelAdmin.list_filter_base
    
    search_fields = [
        'ruc', 'razon_social', 'nombre_comercial', 'contacto_principal'
    ]
    
    list_editable = ['activo_comercial']
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'ruc', 'razon_social', 'nombre_comercial'
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion', 'ubigeo'
            )
        }),
        ('Contacto', {
            'fields': (
                'telefono', 'email', 'contacto_principal'
            )
        }),
        ('Configuración Comercial', {
            'fields': (
                'dias_pago', 'descuento_obtenido'
            )
        }),
        ('Estado', {
            'fields': (
                'activo_comercial', 'activo'
            )
        }),
        ('Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )


# =============================================================================
# ADMIN CATEGORÍA PRODUCTO
# =============================================================================
@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(BaseModelAdmin):
    """
    Configuración del admin para CategoriaProducto
    """
    
    list_display = [
        'codigo', 'nombre', 'categoria_padre',
        'get_cantidad_productos', 'activo'
    ]
    
    list_filter = [
        'categoria_padre'
    ] + BaseModelAdmin.list_filter_base
    
    search_fields = ['codigo', 'nombre', 'descripcion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo', 'nombre', 'descripcion'
            )
        }),
        ('Jerarquía', {
            'fields': (
                'categoria_padre',
            )
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def get_cantidad_productos(self, obj):
        """Mostrar cantidad de productos"""
        return obj.productos.count()
    get_cantidad_productos.short_description = 'Productos'
    
    def get_queryset(self, request):
        """Optimizar consultas con anotaciones"""
        return super().get_queryset(request).annotate(
            num_productos=Count('productos')
        )


# =============================================================================
# ADMIN PRODUCTO
# =============================================================================
@admin.register(Producto)
class ProductoAdmin(BaseModelAdmin):
    """
    Configuración del admin para Producto
    """
    
    list_display = [
        'codigo', 'nombre', 'categoria', 'tipo_producto',
        'precio_venta', 'get_precio_con_igv', 'controla_stock',
        'activo_venta', 'activo_compra', 'activo'
    ]
    
    list_filter = [
        'tipo_producto', 'categoria', 'controla_stock',
        'activo_venta', 'activo_compra', 'tipo_afectacion_igv',
        'incluye_igv', 'marca'
    ] + BaseModelAdmin.list_filter_base
    
    search_fields = [
        'codigo', 'nombre', 'descripcion', 'codigo_barras',
        'marca', 'modelo'
    ]
    
    list_editable = ['activo_venta', 'activo_compra']
    
    fieldsets = (
        ('Identificación', {
            'fields': (
                'codigo', 'codigo_barras', 'codigo_sunat'
            )
        }),
        ('Descripción', {
            'fields': (
                'nombre', 'descripcion', 'tipo_producto', 'categoria'
            )
        }),
        ('Unidades y Medidas', {
            'fields': (
                'unidad_medida', 'peso'
            )
        }),
        ('Precios', {
            'fields': (
                'precio_compra', 'precio_venta', 'precio_venta_minimo'
            )
        }),
        ('Configuración Tributaria', {
            'fields': (
                'tipo_afectacion_igv', 'incluye_igv'
            )
        }),
        ('Control de Stock', {
            'fields': (
                'controla_stock', 'stock_minimo'
            )
        }),
        ('Información Adicional', {
            'fields': (
                'marca', 'modelo', 'imagen'
            )
        }),
        ('Estados', {
            'fields': (
                'activo_venta', 'activo_compra', 'activo'
            )
        }),
        ('Auditoría', {
            'fields': ('id', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        })
    )
    
    def get_precio_con_igv(self, obj):
        """Mostrar precio con IGV"""
        precio = obj.get_precio_con_igv()
        return f"S/ {precio:.2f}"
    get_precio_con_igv.short_description = 'Precio con IGV'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related('categoria')
    
    actions = ['activar_venta', 'desactivar_venta', 'duplicar_productos']
    
    def activar_venta(self, request, queryset):
        """Activar productos para venta"""
        updated = queryset.update(activo_venta=True)
        self.message_user(request, f'{updated} productos activados para venta.')
    activar_venta.short_description = 'Activar para venta'
    
    def desactivar_venta(self, request, queryset):
        """Desactivar productos para venta"""
        updated = queryset.update(activo_venta=False)
        self.message_user(request, f'{updated} productos desactivados para venta.')
    desactivar_venta.short_description = 'Desactivar para venta'
    
    def duplicar_productos(self, request, queryset):
        """Duplicar productos seleccionados"""
        count = 0
        for producto in queryset:
            # Crear copia
            producto.pk = None
            producto.codigo = f"{producto.codigo}_COPIA"
            producto.save()
            count += 1
        
        self.message_user(request, f'{count} productos duplicados.')
    duplicar_productos.short_description = 'Duplicar productos'


# =============================================================================
# ADMIN CONFIGURACIÓN SISTEMA
# =============================================================================
@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para ConfiguracionSistema
    """
    
    list_display = [
        'clave', 'valor', 'tipo_dato', 'descripcion', 'actualizado_en'
    ]
    
    list_filter = ['tipo_dato', 'actualizado_en']
    
    search_fields = ['clave', 'descripcion']
    
    list_editable = ['valor']
    
    fieldsets = (
        ('Configuración', {
            'fields': (
                'clave', 'valor', 'tipo_dato'
            )
        }),
        ('Información', {
            'fields': (
                'descripcion',
            )
        }),
        ('Auditoría', {
            'fields': ('actualizado_en',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['actualizado_en']
    
    def has_delete_permission(self, request, obj=None):
        """Prevenir eliminación de configuraciones críticas"""
        if obj and obj.clave in ['IGV_PORCENTAJE', 'MONEDA_BASE', 'METODO_INVENTARIO']:
            return False
        return super().has_delete_permission(request, obj)


# =============================================================================
# CONFIGURACIÓN ADICIONAL DEL ADMIN
# =============================================================================

# Personalizar el sitio admin
admin.site.site_header = 'FELICITA - Administración'
admin.site.site_title = 'FELICITA Admin'
admin.site.index_title = 'Panel de Administración'


# =============================================================================
# INLINE ADMINS
# =============================================================================
class ProductoInline(admin.TabularInline):
    """
    Inline para productos en categorías
    """
    model = Producto
    extra = 0
    fields = ['codigo', 'nombre', 'precio_venta', 'activo_venta']
    readonly_fields = ['codigo']
    show_change_link = True


# Agregar inline a CategoriaProductoAdmin
CategoriaProductoAdmin.inlines = [ProductoInline]


# =============================================================================
# CONFIGURACIONES ADICIONALES
# =============================================================================

# Registrar acciones globales del admin
def hacer_activo(modeladmin, request, queryset):
    """Acción global para activar elementos"""
    updated = queryset.update(activo=True)
    modeladmin.message_user(request, f'{updated} elementos activados.')
hacer_activo.short_description = 'Activar elementos seleccionados'

def hacer_inactivo(modeladmin, request, queryset):
    """Acción global para desactivar elementos"""
    updated = queryset.update(activo=False)
    modeladmin.message_user(request, f'{updated} elementos desactivados.')
hacer_inactivo.short_description = 'Desactivar elementos seleccionados'

# Agregar acciones a todos los admins base
BaseModelAdmin.actions = [hacer_activo, hacer_inactivo]