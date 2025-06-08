"""
FILTERS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Filtros personalizados para APIs Django REST Framework
"""

import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from datetime import datetime, date, timedelta
from django.utils import timezone

from .models import (
    Empresa, Sucursal, Cliente, Proveedor, Producto, Categoria,
    UnidadMedida, Moneda, TipoCambio, ConfiguracionSistema
)


# =============================================================================
# FILTROS BASE
# =============================================================================
class BaseFilterSet(filters.FilterSet):
    """
    FilterSet base con funcionalidades comunes
    """
    # Filtros de fecha comunes
    fecha_desde = filters.DateFilter(method='filtrar_fecha_desde')
    fecha_hasta = filters.DateFilter(method='filtrar_fecha_hasta')
    fecha_rango = filters.DateFromToRangeFilter()
    
    # Filtros de búsqueda
    buscar = filters.CharFilter(method='buscar_general')
    
    # Filtros de estado
    activo = filters.BooleanFilter()
    
    def filtrar_fecha_desde(self, queryset, name, value):
        """
        Filtrar registros desde una fecha específica
        """
        if value:
            return queryset.filter(creado_en__date__gte=value)
        return queryset
    
    def filtrar_fecha_hasta(self, queryset, name, value):
        """
        Filtrar registros hasta una fecha específica
        """
        if value:
            return queryset.filter(creado_en__date__lte=value)
        return queryset
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general - implementar en cada filtro específico
        """
        return queryset


# =============================================================================
# FILTROS DE EMPRESA
# =============================================================================
class EmpresaFilter(BaseFilterSet):
    """
    Filtros para modelo Empresa
    """
    ruc = filters.CharFilter(lookup_expr='icontains')
    razon_social = filters.CharFilter(lookup_expr='icontains')
    nombre_comercial = filters.CharFilter(lookup_expr='icontains')
    estado = filters.ChoiceFilter(choices=[
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido')
    ])
    regimen_tributario = filters.ChoiceFilter(choices=[
        ('GENERAL', 'Régimen General'),
        ('ESPECIAL', 'Régimen Especial'),
        ('MYPE', 'Régimen MYPE'),
        ('RUS', 'Régimen Único Simplificado')
    ])
    
    # Filtros por ubicación
    departamento = filters.CharFilter(field_name='departamento', lookup_expr='icontains')
    provincia = filters.CharFilter(field_name='provincia', lookup_expr='icontains')
    distrito = filters.CharFilter(field_name='distrito', lookup_expr='icontains')
    
    class Meta:
        model = Empresa
        fields = [
            'ruc', 'razon_social', 'nombre_comercial', 'estado',
            'regimen_tributario', 'departamento', 'provincia', 'distrito'
        ]
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en empresas
        """
        if value:
            return queryset.filter(
                Q(ruc__icontains=value) |
                Q(razon_social__icontains=value) |
                Q(nombre_comercial__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS DE SUCURSAL
# =============================================================================
class SucursalFilter(BaseFilterSet):
    """
    Filtros para modelo Sucursal
    """
    empresa = filters.ModelChoiceFilter(queryset=Empresa.objects.all())
    codigo = filters.CharFilter(lookup_expr='icontains')
    nombre = filters.CharFilter(lookup_expr='icontains')
    es_principal = filters.BooleanFilter()
    
    # Filtros por ubicación
    departamento = filters.CharFilter(lookup_expr='icontains')
    provincia = filters.CharFilter(lookup_expr='icontains')
    distrito = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Sucursal
        fields = [
            'empresa', 'codigo', 'nombre', 'es_principal',
            'departamento', 'provincia', 'distrito', 'activo'
        ]
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en sucursales
        """
        if value:
            return queryset.filter(
                Q(codigo__icontains=value) |
                Q(nombre__icontains=value) |
                Q(direccion__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS DE CLIENTE
# =============================================================================
class ClienteFilter(BaseFilterSet):
    """
    Filtros para modelo Cliente
    """
    tipo_documento = filters.ChoiceFilter(choices=[
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CARNET_EXTRANJERIA', 'Carnet de Extranjería'),
        ('PASAPORTE', 'Pasaporte')
    ])
    numero_documento = filters.CharFilter(lookup_expr='icontains')
    nombres = filters.CharFilter(lookup_expr='icontains')
    apellido_paterno = filters.CharFilter(lookup_expr='icontains')
    apellido_materno = filters.CharFilter(lookup_expr='icontains')
    razon_social = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    telefono = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por tipo
    es_empresa = filters.BooleanFilter()
    
    # Filtros por ubicación
    departamento = filters.CharFilter(lookup_expr='icontains')
    provincia = filters.CharFilter(lookup_expr='icontains')
    distrito = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por fecha
    fecha_registro_desde = filters.DateFilter(field_name='creado_en', lookup_expr='date__gte')
    fecha_registro_hasta = filters.DateFilter(field_name='creado_en', lookup_expr='date__lte')
    
    class Meta:
        model = Cliente
        fields = [
            'tipo_documento', 'numero_documento', 'nombres', 'apellido_paterno',
            'apellido_materno', 'razon_social', 'email', 'telefono', 'es_empresa',
            'departamento', 'provincia', 'distrito', 'activo'
        ]
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en clientes
        """
        if value:
            return queryset.filter(
                Q(numero_documento__icontains=value) |
                Q(nombres__icontains=value) |
                Q(apellido_paterno__icontains=value) |
                Q(apellido_materno__icontains=value) |
                Q(razon_social__icontains=value) |
                Q(email__icontains=value) |
                Q(telefono__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS DE PROVEEDOR
# =============================================================================
class ProveedorFilter(BaseFilterSet):
    """
    Filtros para modelo Proveedor
    """
    tipo_documento = filters.ChoiceFilter(choices=[
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CARNET_EXTRANJERIA', 'Carnet de Extranjería'),
        ('PASAPORTE', 'Pasaporte')
    ])
    numero_documento = filters.CharFilter(lookup_expr='icontains')
    razon_social = filters.CharFilter(lookup_expr='icontains')
    nombre_comercial = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    telefono = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por categoría
    categoria = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por ubicación
    departamento = filters.CharFilter(lookup_expr='icontains')
    provincia = filters.CharFilter(lookup_expr='icontains')
    distrito = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por condiciones comerciales
    dias_credito_min = filters.NumberFilter(field_name='dias_credito', lookup_expr='gte')
    dias_credito_max = filters.NumberFilter(field_name='dias_credito', lookup_expr='lte')
    
    class Meta:
        model = Proveedor
        fields = [
            'tipo_documento', 'numero_documento', 'razon_social', 'nombre_comercial',
            'email', 'telefono', 'categoria', 'departamento', 'provincia',
            'distrito', 'activo'
        ]
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en proveedores
        """
        if value:
            return queryset.filter(
                Q(numero_documento__icontains=value) |
                Q(razon_social__icontains=value) |
                Q(nombre_comercial__icontains=value) |
                Q(email__icontains=value) |
                Q(telefono__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS DE PRODUCTO
# =============================================================================
class ProductoFilter(BaseFilterSet):
    """
    Filtros para modelo Producto
    """
    codigo = filters.CharFilter(lookup_expr='icontains')
    nombre = filters.CharFilter(lookup_expr='icontains')
    descripcion = filters.CharFilter(lookup_expr='icontains')
    categoria = filters.ModelChoiceFilter(queryset=Categoria.objects.all())
    unidad_medida = filters.ModelChoiceFilter(queryset=UnidadMedida.objects.all())
    
    # Filtros por tipo
    tipo_producto = filters.ChoiceFilter(choices=[
        ('BIEN', 'Bien'),
        ('SERVICIO', 'Servicio')
    ])
    
    # Filtros por precios
    precio_venta_min = filters.NumberFilter(field_name='precio_venta', lookup_expr='gte')
    precio_venta_max = filters.NumberFilter(field_name='precio_venta', lookup_expr='lte')
    precio_compra_min = filters.NumberFilter(field_name='precio_compra', lookup_expr='gte')
    precio_compra_max = filters.NumberFilter(field_name='precio_compra', lookup_expr='lte')
    
    # Filtros por stock
    stock_min = filters.NumberFilter(field_name='stock_actual', lookup_expr='gte')
    stock_max = filters.NumberFilter(field_name='stock_actual', lookup_expr='lte')
    con_stock = filters.BooleanFilter(method='filtrar_con_stock')
    sin_stock = filters.BooleanFilter(method='filtrar_sin_stock')
    stock_bajo = filters.BooleanFilter(method='filtrar_stock_bajo')
    
    # Filtros por estado
    con_igv = filters.BooleanFilter(field_name='afecto_igv')
    
    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'descripcion', 'categoria', 'unidad_medida',
            'tipo_producto', 'afecto_igv', 'activo'
        ]
    
    def filtrar_con_stock(self, queryset, name, value):
        """
        Filtrar productos con stock
        """
        if value:
            return queryset.filter(stock_actual__gt=0)
        return queryset
    
    def filtrar_sin_stock(self, queryset, name, value):
        """
        Filtrar productos sin stock
        """
        if value:
            return queryset.filter(stock_actual=0)
        return queryset
    
    def filtrar_stock_bajo(self, queryset, name, value):
        """
        Filtrar productos con stock bajo (menor al mínimo)
        """
        if value:
            return queryset.filter(stock_actual__lt=models.F('stock_minimo'))
        return queryset
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en productos
        """
        if value:
            return queryset.filter(
                Q(codigo__icontains=value) |
                Q(nombre__icontains=value) |
                Q(descripcion__icontains=value) |
                Q(codigo_barra__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS DE CATEGORÍA
# =============================================================================
class CategoriaFilter(BaseFilterSet):
    """
    Filtros para modelo Categoría
    """
    codigo = filters.CharFilter(lookup_expr='icontains')
    nombre = filters.CharFilter(lookup_expr='icontains')
    descripcion = filters.CharFilter(lookup_expr='icontains')
    categoria_padre = filters.ModelChoiceFilter(queryset=Categoria.objects.all())
    
    # Filtros especiales
    es_categoria_raiz = filters.BooleanFilter(method='filtrar_categoria_raiz')
    tiene_subcategorias = filters.BooleanFilter(method='filtrar_con_subcategorias')
    
    class Meta:
        model = Categoria
        fields = ['codigo', 'nombre', 'descripcion', 'categoria_padre', 'activo']
    
    def filtrar_categoria_raiz(self, queryset, name, value):
        """
        Filtrar categorías raíz (sin padre)
        """
        if value:
            return queryset.filter(categoria_padre__isnull=True)
        return queryset
    
    def filtrar_con_subcategorias(self, queryset, name, value):
        """
        Filtrar categorías que tienen subcategorías
        """
        if value:
            return queryset.filter(subcategorias__isnull=False).distinct()
        return queryset
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en categorías
        """
        if value:
            return queryset.filter(
                Q(codigo__icontains=value) |
                Q(nombre__icontains=value) |
                Q(descripcion__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS DE CONFIGURACIÓN
# =============================================================================
class TipoCambioFilter(BaseFilterSet):
    """
    Filtros para modelo TipoCambio
    """
    moneda_origen = filters.ModelChoiceFilter(queryset=Moneda.objects.all())
    moneda_destino = filters.ModelChoiceFilter(queryset=Moneda.objects.all())
    
    # Filtros por fecha
    fecha = filters.DateFilter()
    fecha_desde = filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_hasta = filters.DateFilter(field_name='fecha', lookup_expr='lte')
    
    # Filtros por valor
    valor_compra_min = filters.NumberFilter(field_name='valor_compra', lookup_expr='gte')
    valor_compra_max = filters.NumberFilter(field_name='valor_compra', lookup_expr='lte')
    valor_venta_min = filters.NumberFilter(field_name='valor_venta', lookup_expr='gte')
    valor_venta_max = filters.NumberFilter(field_name='valor_venta', lookup_expr='lte')
    
    class Meta:
        model = TipoCambio
        fields = ['moneda_origen', 'moneda_destino', 'fecha']
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en tipos de cambio
        """
        if value:
            return queryset.filter(
                Q(moneda_origen__codigo__icontains=value) |
                Q(moneda_destino__codigo__icontains=value) |
                Q(moneda_origen__nombre__icontains=value) |
                Q(moneda_destino__nombre__icontains=value)
            )
        return queryset


class ConfiguracionSistemaFilter(BaseFilterSet):
    """
    Filtros para modelo ConfiguracionSistema
    """
    clave = filters.CharFilter(lookup_expr='icontains')
    descripcion = filters.CharFilter(lookup_expr='icontains')
    tipo_dato = filters.ChoiceFilter(choices=[
        ('STRING', 'Texto'),
        ('INTEGER', 'Entero'),
        ('DECIMAL', 'Decimal'),
        ('BOOLEAN', 'Booleano'),
        ('DATE', 'Fecha'),
        ('JSON', 'JSON')
    ])
    categoria = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = ConfiguracionSistema
        fields = ['clave', 'descripcion', 'tipo_dato', 'categoria']
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en configuraciones
        """
        if value:
            return queryset.filter(
                Q(clave__icontains=value) |
                Q(descripcion__icontains=value) |
                Q(categoria__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS ESPECIALIZADOS
# =============================================================================
class FiltroFechaAvanzado(filters.FilterSet):
    """
    Filtro especializado para rangos de fechas avanzados
    """
    # Filtros predefinidos
    hoy = filters.BooleanFilter(method='filtrar_hoy')
    ayer = filters.BooleanFilter(method='filtrar_ayer')
    esta_semana = filters.BooleanFilter(method='filtrar_esta_semana')
    semana_pasada = filters.BooleanFilter(method='filtrar_semana_pasada')
    este_mes = filters.BooleanFilter(method='filtrar_este_mes')
    mes_pasado = filters.BooleanFilter(method='filtrar_mes_pasado')
    este_año = filters.BooleanFilter(method='filtrar_este_año')
    año_pasado = filters.BooleanFilter(method='filtrar_año_pasado')
    ultimos_7_dias = filters.BooleanFilter(method='filtrar_ultimos_7_dias')
    ultimos_30_dias = filters.BooleanFilter(method='filtrar_ultimos_30_dias')
    ultimos_90_dias = filters.BooleanFilter(method='filtrar_ultimos_90_dias')
    
    def filtrar_hoy(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            return queryset.filter(creado_en__date=hoy)
        return queryset
    
    def filtrar_ayer(self, queryset, name, value):
        if value:
            ayer = timezone.now().date() - timedelta(days=1)
            return queryset.filter(creado_en__date=ayer)
        return queryset
    
    def filtrar_esta_semana(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            return queryset.filter(creado_en__date__gte=inicio_semana)
        return queryset
    
    def filtrar_este_mes(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            inicio_mes = hoy.replace(day=1)
            return queryset.filter(creado_en__date__gte=inicio_mes)
        return queryset
    
    def filtrar_ultimos_7_dias(self, queryset, name, value):
        if value:
            fecha_limite = timezone.now().date() - timedelta(days=7)
            return queryset.filter(creado_en__date__gte=fecha_limite)
        return queryset
    
    def filtrar_ultimos_30_dias(self, queryset, name, value):
        if value:
            fecha_limite = timezone.now().date() - timedelta(days=30)
            return queryset.filter(creado_en__date__gte=fecha_limite)
        return queryset
    
    def filtrar_ultimos_90_dias(self, queryset, name, value):
        if value:
            fecha_limite = timezone.now().date() - timedelta(days=90)
            return queryset.filter(creado_en__date__gte=fecha_limite)
        return queryset


# =============================================================================
# MIXINS PARA FILTROS COMUNES
# =============================================================================
class EmpresaFilterMixin:
    """
    Mixin para filtrar por empresa del usuario autenticado
    """
    
    def filter_queryset(self, queryset):
        """
        Filtrar por empresa del usuario autenticado
        """
        queryset = super().filter_queryset(queryset)
        
        if hasattr(self.request, 'user') and hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        
        return queryset


class ActivoFilterMixin:
    """
    Mixin para filtros de registros activos/inactivos
    """
    mostrar_inactivos = filters.BooleanFilter(method='filtrar_mostrar_inactivos')
    solo_activos = filters.BooleanFilter(method='filtrar_solo_activos')
    
    def filtrar_mostrar_inactivos(self, queryset, name, value):
        """
        Incluir registros inactivos en los resultados
        """
        if not value:
            return queryset.filter(activo=True)
        return queryset
    
    def filtrar_solo_activos(self, queryset, name, value):
        """
        Mostrar solo registros activos
        """
        if value:
            return queryset.filter(activo=True)
        return queryset