"""
FILTERS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Filtros para las APIs del módulo core
"""

import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Cliente, Producto, Empresa, CategoriaProducto


# =============================================================================
# FILTER BASE
# =============================================================================
class BaseFilter(filters.FilterSet):
    """
    Filter base con campos comunes
    """
    
    # Filtros de fechas
    creado_desde = filters.DateFilter(field_name='creado_en', lookup_expr='gte')
    creado_hasta = filters.DateFilter(field_name='creado_en', lookup_expr='lte')
    actualizado_desde = filters.DateFilter(field_name='actualizado_en', lookup_expr='gte')
    actualizado_hasta = filters.DateFilter(field_name='actualizado_en', lookup_expr='lte')
    
    # Filtro de estado
    activo = filters.BooleanFilter(field_name='activo')


# =============================================================================
# FILTER CLIENTE
# =============================================================================
class ClienteFilter(BaseFilter):
    """
    Filtros para el modelo Cliente
    """
    
    # Filtros de búsqueda
    busqueda = filters.CharFilter(method='filtrar_busqueda')
    
    # Filtros específicos
    tipo_documento = filters.ChoiceFilter(
        field_name='tipo_documento',
        choices=Cliente.TIPO_DOCUMENTO_CHOICES
    )
    
    tipo_cliente = filters.ChoiceFilter(
        field_name='tipo_cliente',
        choices=Cliente.TIPO_CLIENTE_CHOICES
    )
    
    # Filtros de ubicación
    distrito = filters.CharFilter(field_name='distrito', lookup_expr='icontains')
    provincia = filters.CharFilter(field_name='provincia', lookup_expr='icontains')
    departamento = filters.CharFilter(field_name='departamento', lookup_expr='icontains')
    
    # Filtros de crédito
    limite_credito_min = filters.NumberFilter(field_name='limite_credito', lookup_expr='gte')
    limite_credito_max = filters.NumberFilter(field_name='limite_credito', lookup_expr='lte')
    
    # Filtros de estado
    bloqueado = filters.BooleanFilter(field_name='bloqueado')
    
    # Filtros de días de crédito
    dias_credito_min = filters.NumberFilter(field_name='dias_credito', lookup_expr='gte')
    dias_credito_max = filters.NumberFilter(field_name='dias_credito', lookup_expr='lte')
    
    # Filtro de email
    tiene_email = filters.BooleanFilter(method='filtrar_tiene_email')
    
    class Meta:
        model = Cliente
        fields = [
            'tipo_documento', 'tipo_cliente', 'distrito', 'provincia', 
            'departamento', 'bloqueado', 'activo'
        ]
    
    def filtrar_busqueda(self, queryset, name, value):
        """
        Filtro de búsqueda general
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(razon_social__icontains=value) |
            Q(nombres__icontains=value) |
            Q(apellido_paterno__icontains=value) |
            Q(apellido_materno__icontains=value) |
            Q(numero_documento__icontains=value) |
            Q(email__icontains=value) |
            Q(telefono__icontains=value)
        )
    
    def filtrar_tiene_email(self, queryset, name, value):
        """
        Filtrar clientes que tienen o no email
        """
        if value:
            return queryset.exclude(Q(email='') | Q(email__isnull=True))
        else:
            return queryset.filter(Q(email='') | Q(email__isnull=True))


# =============================================================================
# FILTER PRODUCTO
# =============================================================================
class ProductoFilter(BaseFilter):
    """
    Filtros para el modelo Producto
    """
    
    # Filtros de búsqueda
    busqueda = filters.CharFilter(method='filtrar_busqueda')
    
    # Filtros específicos
    tipo_producto = filters.ChoiceFilter(
        field_name='tipo_producto',
        choices=Producto.TIPO_PRODUCTO_CHOICES
    )
    
    categoria = filters.ModelChoiceFilter(
        field_name='categoria',
        queryset=CategoriaProducto.objects.all()
    )
    
    categoria_nombre = filters.CharFilter(
        field_name='categoria__nombre',
        lookup_expr='icontains'
    )
    
    # Filtros de precios
    precio_min = filters.NumberFilter(field_name='precio_venta', lookup_expr='gte')
    precio_max = filters.NumberFilter(field_name='precio_venta', lookup_expr='lte')
    
    precio_compra_min = filters.NumberFilter(field_name='precio_compra', lookup_expr='gte')
    precio_compra_max = filters.NumberFilter(field_name='precio_compra', lookup_expr='lte')
    
    # Filtros de stock
    controla_stock = filters.BooleanFilter(field_name='controla_stock')
    stock_minimo_min = filters.NumberFilter(field_name='stock_minimo', lookup_expr='gte')
    stock_minimo_max = filters.NumberFilter(field_name='stock_minimo', lookup_expr='lte')
    
    # Filtros de estado de venta/compra
    activo_venta = filters.BooleanFilter(field_name='activo_venta')
    activo_compra = filters.BooleanFilter(field_name='activo_compra')
    
    # Filtros de IGV
    tipo_afectacion_igv = filters.ChoiceFilter(
        field_name='tipo_afectacion_igv',
        choices=Producto.TIPO_AFECTACION_IGV_CHOICES
    )
    
    incluye_igv = filters.BooleanFilter(field_name='incluye_igv')
    
    # Filtros de marca y modelo
    marca = filters.CharFilter(field_name='marca', lookup_expr='icontains')
    modelo = filters.CharFilter(field_name='modelo', lookup_expr='icontains')
    
    # Filtro de código SUNAT
    codigo_sunat = filters.CharFilter(field_name='codigo_sunat', lookup_expr='exact')
    
    # Filtro de unidad de medida
    unidad_medida = filters.CharFilter(field_name='unidad_medida', lookup_expr='exact')
    
    # Filtro de imagen
    tiene_imagen = filters.BooleanFilter(method='filtrar_tiene_imagen')
    
    class Meta:
        model = Producto
        fields = [
            'tipo_producto', 'categoria', 'controla_stock', 
            'activo_venta', 'activo_compra', 'incluye_igv', 'activo'
        ]
    
    def filtrar_busqueda(self, queryset, name, value):
        """
        Filtro de búsqueda general
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(codigo__icontains=value) |
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value) |
            Q(codigo_barras__icontains=value) |
            Q(marca__icontains=value) |
            Q(modelo__icontains=value) |
            Q(categoria__nombre__icontains=value)
        )
    
    def filtrar_tiene_imagen(self, queryset, name, value):
        """
        Filtrar productos que tienen o no imagen
        """
        if value:
            return queryset.exclude(Q(imagen='') | Q(imagen__isnull=True))
        else:
            return queryset.filter(Q(imagen='') | Q(imagen__isnull=True))


# =============================================================================
# FILTER CATEGORIA PRODUCTO
# =============================================================================
class CategoriaProductoFilter(BaseFilter):
    """
    Filtros para el modelo CategoriaProducto
    """
    
    # Filtros de búsqueda
    busqueda = filters.CharFilter(method='filtrar_busqueda')
    
    # Filtros de jerarquía
    categoria_padre = filters.ModelChoiceFilter(
        field_name='categoria_padre',
        queryset=CategoriaProducto.objects.all()
    )
    
    es_categoria_raiz = filters.BooleanFilter(method='filtrar_categoria_raiz')
    
    # Filtro de productos
    tiene_productos = filters.BooleanFilter(method='filtrar_tiene_productos')
    
    class Meta:
        model = CategoriaProducto
        fields = ['categoria_padre', 'activo']
    
    def filtrar_busqueda(self, queryset, name, value):
        """
        Filtro de búsqueda general
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(codigo__icontains=value) |
            Q(nombre__icontains=value) |
            Q(descripcion__icontains=value)
        )
    
    def filtrar_categoria_raiz(self, queryset, name, value):
        """
        Filtrar categorías raíz (sin padre)
        """
        if value:
            return queryset.filter(categoria_padre__isnull=True)
        else:
            return queryset.filter(categoria_padre__isnull=False)
    
    def filtrar_tiene_productos(self, queryset, name, value):
        """
        Filtrar categorías que tienen productos
        """
        if value:
            return queryset.filter(productos__isnull=False).distinct()
        else:
            return queryset.filter(productos__isnull=True)


# =============================================================================
# FILTER EMPRESA
# =============================================================================
class EmpresaFilter(BaseFilter):
    """
    Filtros para el modelo Empresa
    """
    
    # Filtros de búsqueda
    busqueda = filters.CharFilter(method='filtrar_busqueda')
    
    # Filtros específicos
    regimen_tributario = filters.ChoiceFilter(
        field_name='regimen_tributario',
        choices=Empresa.REGIMEN_TRIBUTARIO_CHOICES if hasattr(Empresa, 'REGIMEN_TRIBUTARIO_CHOICES') else []
    )
    
    plan_cuentas = filters.ChoiceFilter(
        field_name='plan_cuentas',
        choices=[('PCGE', 'PCGE'), ('PCGR', 'PCGR')]
    )
    
    moneda_base = filters.ChoiceFilter(
        field_name='moneda_base',
        choices=[('PEN', 'PEN'), ('USD', 'USD'), ('EUR', 'EUR')]
    )
    
    # Filtros de ubicación
    distrito = filters.CharFilter(field_name='distrito', lookup_expr='icontains')
    provincia = filters.CharFilter(field_name='provincia', lookup_expr='icontains')
    departamento = filters.CharFilter(field_name='departamento', lookup_expr='icontains')
    
    class Meta:
        model = Empresa
        fields = ['regimen_tributario', 'plan_cuentas', 'moneda_base', 'activo']
    
    def filtrar_busqueda(self, queryset, name, value):
        """
        Filtro de búsqueda general
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(ruc__icontains=value) |
            Q(razon_social__icontains=value) |
            Q(nombre_comercial__icontains=value) |
            Q(email__icontains=value)
        )


# =============================================================================
# FILTROS PERSONALIZADOS ADICIONALES
# =============================================================================
class RangoFechaFilter(filters.FilterSet):
    """
    Filter para rangos de fechas reutilizable
    """
    
    fecha_desde = filters.DateFilter(method='filtrar_fecha_desde')
    fecha_hasta = filters.DateFilter(method='filtrar_fecha_hasta')
    
    def filtrar_fecha_desde(self, queryset, name, value):
        """
        Filtrar desde fecha
        """
        campo_fecha = getattr(self.Meta, 'campo_fecha', 'creado_en')
        return queryset.filter(**{f'{campo_fecha}__gte': value})
    
    def filtrar_fecha_hasta(self, queryset, name, value):
        """
        Filtrar hasta fecha
        """
        campo_fecha = getattr(self.Meta, 'campo_fecha', 'creado_en')
        return queryset.filter(**{f'{campo_fecha}__lte': value})


class BusquedaGeneralFilter(filters.FilterSet):
    """
    Filter de búsqueda general reutilizable
    """
    
    q = filters.CharFilter(method='busqueda_general')
    
    def busqueda_general(self, queryset, name, value):
        """
        Búsqueda general en campos especificados
        """
        if not value:
            return queryset
        
        campos_busqueda = getattr(self.Meta, 'campos_busqueda', [])
        if not campos_busqueda:
            return queryset
        
        condiciones = Q()
        for campo in campos_busqueda:
            condiciones |= Q(**{f'{campo}__icontains': value})
        
        return queryset.filter(condiciones)


# =============================================================================
# FILTROS ESPECÍFICOS PARA REPORTES
# =============================================================================
class FiltroReporteVentas(filters.FilterSet):
    """
    Filtros específicos para reportes de ventas
    """
    
    fecha_desde = filters.DateFilter(field_name='fecha_emision', lookup_expr='gte')
    fecha_hasta = filters.DateFilter(field_name='fecha_emision', lookup_expr='lte')
    cliente = filters.ModelChoiceFilter(queryset=Cliente.objects.all())
    vendedor = filters.CharFilter(field_name='usuario_vendedor__nombres', lookup_expr='icontains')
    tipo_comprobante = filters.CharFilter(field_name='tipo_comprobante')
    estado = filters.CharFilter(field_name='estado')
    
    # Filtros de montos
    total_min = filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = filters.NumberFilter(field_name='total', lookup_expr='lte')


class FiltroReporteInventario(filters.FilterSet):
    """
    Filtros específicos para reportes de inventario
    """
    
    categoria = filters.ModelChoiceFilter(queryset=CategoriaProducto.objects.all())
    con_stock = filters.BooleanFilter(method='filtrar_con_stock')
    stock_bajo = filters.BooleanFilter(method='filtrar_stock_bajo')
    sin_movimientos = filters.BooleanFilter(method='filtrar_sin_movimientos')
    
    def filtrar_con_stock(self, queryset, name, value):
        """
        Filtrar productos con stock
        """
        # TODO: Implementar cuando se tenga StockProducto
        return queryset
    
    def filtrar_stock_bajo(self, queryset, name, value):
        """
        Filtrar productos con stock bajo
        """
        # TODO: Implementar cuando se tenga StockProducto
        return queryset
    
    def filtrar_sin_movimientos(self, queryset, name, value):
        """
        Filtrar productos sin movimientos recientes
        """
        # TODO: Implementar cuando se tenga MovimientoInventario
        return queryset