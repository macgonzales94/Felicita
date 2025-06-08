"""
FILTERS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Filtros personalizados para APIs Django REST Framework
"""

import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q, F
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
    fecha_rango = filters.DateFromToRangeFilter(field_name='creado_en')
    
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
    regimen_tributario = filters.ChoiceFilter(choices=[
        ('GENERAL', 'Régimen General'),
        ('ESPECIAL', 'Régimen Especial de Renta'),
        ('MYPE', 'Régimen MYPE Tributario'),
        ('RUS', 'Nuevo RUS')
    ])
    
    # Filtros por ubicación
    departamento = filters.CharFilter(field_name='departamento', lookup_expr='icontains')
    provincia = filters.CharFilter(field_name='provincia', lookup_expr='icontains')
    distrito = filters.CharFilter(field_name='distrito', lookup_expr='icontains')
    
    class Meta:
        model = Empresa
        fields = [
            'ruc', 'razon_social', 'nombre_comercial',
            'regimen_tributario', 'departamento', 'provincia', 'distrito',
            'activo'
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
    
    class Meta:
        model = Sucursal
        fields = [
            'empresa', 'codigo', 'nombre', 'es_principal', 'activo'
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
        ('DNI', 'DNI - Documento Nacional de Identidad'),
        ('RUC', 'RUC - Registro Único de Contribuyente'),
        ('CE', 'CE - Carnet de Extranjería'),
        ('PASSPORT', 'Pasaporte'),
        ('OTROS', 'Otros documentos')
    ])
    numero_documento = filters.CharFilter(lookup_expr='icontains')
    razon_social = filters.CharFilter(lookup_expr='icontains')
    nombres = filters.CharFilter(lookup_expr='icontains')
    apellido_paterno = filters.CharFilter(lookup_expr='icontains')
    apellido_materno = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    telefono = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por tipo - CORREGIDO: usar tipo_cliente en lugar de es_empresa
    tipo_cliente = filters.ChoiceFilter(choices=[
        ('PERSONA_NATURAL', 'Persona Natural'),
        ('PERSONA_JURIDICA', 'Persona Jurídica'),
        ('NO_DOMICILIADO', 'No Domiciliado')
    ])
    
    # Filtros por ubicación
    departamento = filters.CharFilter(lookup_expr='icontains')
    provincia = filters.CharFilter(lookup_expr='icontains')
    distrito = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por estado
    bloqueado = filters.BooleanFilter()
    
    # Filtros por fecha
    fecha_registro_desde = filters.DateFilter(field_name='creado_en', lookup_expr='date__gte')
    fecha_registro_hasta = filters.DateFilter(field_name='creado_en', lookup_expr='date__lte')
    
    class Meta:
        model = Cliente
        fields = [
            'tipo_documento', 'numero_documento', 'razon_social', 'nombres', 
            'apellido_paterno', 'apellido_materno', 'email', 'telefono', 
            'tipo_cliente', 'departamento', 'provincia', 'distrito', 
            'activo', 'bloqueado'
        ]
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en clientes
        """
        if value:
            return queryset.filter(
                Q(numero_documento__icontains=value) |
                Q(razon_social__icontains=value) |
                Q(nombres__icontains=value) |
                Q(apellido_paterno__icontains=value) |
                Q(apellido_materno__icontains=value) |
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
    ruc = filters.CharFilter(lookup_expr='icontains')
    razon_social = filters.CharFilter(lookup_expr='icontains')
    nombre_comercial = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    telefono = filters.CharFilter(lookup_expr='icontains')
    contacto_principal = filters.CharFilter(lookup_expr='icontains')
    
    # Filtros por condiciones comerciales - CORREGIDO: usar dias_pago en lugar de dias_credito
    dias_pago_min = filters.NumberFilter(field_name='dias_pago', lookup_expr='gte')
    dias_pago_max = filters.NumberFilter(field_name='dias_pago', lookup_expr='lte')
    
    # Filtros por estado
    activo_comercial = filters.BooleanFilter()
    
    class Meta:
        model = Proveedor
        fields = [
            'ruc', 'razon_social', 'nombre_comercial', 'email', 'telefono',
            'contacto_principal', 'activo', 'activo_comercial'
        ]
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en proveedores
        """
        if value:
            return queryset.filter(
                Q(ruc__icontains=value) |
                Q(razon_social__icontains=value) |
                Q(nombre_comercial__icontains=value) |
                Q(email__icontains=value) |
                Q(telefono__icontains=value) |
                Q(contacto_principal__icontains=value)
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
    codigo_barras = filters.CharFilter(lookup_expr='icontains')
    codigo_sunat = filters.CharFilter(lookup_expr='icontains')
    nombre = filters.CharFilter(lookup_expr='icontains')
    descripcion = filters.CharFilter(lookup_expr='icontains')
    categoria = filters.ModelChoiceFilter(queryset=Categoria.objects.all())
    
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
    
    # Filtros por stock - CORREGIDO: ahora que agregamos stock_actual al modelo
    stock_actual_min = filters.NumberFilter(field_name='stock_actual', lookup_expr='gte')
    stock_actual_max = filters.NumberFilter(field_name='stock_actual', lookup_expr='lte')
    con_stock = filters.BooleanFilter(method='filtrar_con_stock')
    sin_stock = filters.BooleanFilter(method='filtrar_sin_stock')
    stock_bajo = filters.BooleanFilter(method='filtrar_stock_bajo')
    
    # Filtros por configuración tributaria - CORREGIDO: usar tipo_afectacion_igv
    tipo_afectacion_igv = filters.ChoiceFilter(choices=[
        ('10', 'Gravado - Operación Onerosa'),
        ('11', 'Gravado - Retiro por premio'),
        ('12', 'Gravado - Retiro por donación'),
        ('13', 'Gravado - Retiro'),
        ('14', 'Gravado - Retiro por publicidad'),
        ('15', 'Gravado - Bonificaciones'),
        ('16', 'Gravado - Retiro por entrega a trabajadores'),
        ('17', 'Gravado - IVAP'),
        ('20', 'Exonerado - Operación Onerosa'),
        ('21', 'Exonerado - Transferencia Gratuita'),
        ('30', 'Inafecto - Operación Onerosa'),
        ('31', 'Inafecto - Retiro por Bonificación'),
        ('32', 'Inafecto - Retiro'),
        ('33', 'Inafecto - Retiro por Muestras Médicas'),
        ('34', 'Inafecto - Retiro por Convenio Colectivo'),
        ('35', 'Inafecto - Retiro por premio'),
        ('36', 'Inafecto - Retiro por publicidad'),
        ('40', 'Exportación de Bienes o Servicios'),
    ])
    incluye_igv = filters.BooleanFilter()
    
    # Filtros por inventario
    controla_stock = filters.BooleanFilter()
    stock_minimo_min = filters.NumberFilter(field_name='stock_minimo', lookup_expr='gte')
    stock_minimo_max = filters.NumberFilter(field_name='stock_minimo', lookup_expr='lte')
    stock_maximo_min = filters.NumberFilter(field_name='stock_maximo', lookup_expr='gte')
    stock_maximo_max = filters.NumberFilter(field_name='stock_maximo', lookup_expr='lte')
    
    # Filtros por estado
    activo_venta = filters.BooleanFilter()
    activo_compra = filters.BooleanFilter()
    
    # Filtros por información adicional
    marca = filters.CharFilter(lookup_expr='icontains')
    modelo = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Producto
        fields = [
            'codigo', 'codigo_barras', 'codigo_sunat', 'nombre', 'descripcion',
            'categoria', 'tipo_producto', 'unidad_medida', 'tipo_afectacion_igv',
            'incluye_igv', 'controla_stock', 'stock_actual', 'stock_minimo', 'stock_maximo',
            'activo', 'activo_venta', 'activo_compra', 'marca', 'modelo'
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
            return queryset.filter(stock_actual__lt=F('stock_minimo'))
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
                Q(codigo_barras__icontains=value) |
                Q(codigo_sunat__icontains=value) |
                Q(marca__icontains=value) |
                Q(modelo__icontains=value)
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
# FILTROS DE UNIDAD DE MEDIDA
# =============================================================================
class UnidadMedidaFilter(BaseFilterSet):
    """
    Filtros para modelo UnidadMedida
    """
    codigo = filters.CharFilter(lookup_expr='icontains')
    nombre = filters.CharFilter(lookup_expr='icontains')
    descripcion = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = UnidadMedida
        fields = ['codigo', 'nombre', 'descripcion', 'activo']
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en unidades de medida
        """
        if value:
            return queryset.filter(
                Q(codigo__icontains=value) |
                Q(nombre__icontains=value) |
                Q(descripcion__icontains=value)
            )
        return queryset


# =============================================================================
# FILTROS DE MONEDA
# =============================================================================
class MonedaFilter(BaseFilterSet):
    """
    Filtros para modelo Moneda
    """
    codigo = filters.CharFilter(lookup_expr='icontains')
    nombre = filters.CharFilter(lookup_expr='icontains')
    simbolo = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Moneda
        fields = ['codigo', 'nombre', 'simbolo', 'activo']
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en monedas
        """
        if value:
            return queryset.filter(
                Q(codigo__icontains=value) |
                Q(nombre__icontains=value) |
                Q(simbolo__icontains=value)
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
    
    # Filtro por fuente
    fuente = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = TipoCambio
        fields = ['moneda_origen', 'moneda_destino', 'fecha', 'fuente']
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en tipos de cambio
        """
        if value:
            return queryset.filter(
                Q(moneda_origen__codigo__icontains=value) |
                Q(moneda_destino__codigo__icontains=value) |
                Q(moneda_origen__nombre__icontains=value) |
                Q(moneda_destino__nombre__icontains=value) |
                Q(fuente__icontains=value)
            )
        return queryset


class ConfiguracionSistemaFilter(BaseFilterSet):
    """
    Filtros para modelo ConfiguracionSistema
    """
    clave = filters.CharFilter(lookup_expr='icontains')
    descripcion = filters.CharFilter(lookup_expr='icontains')
    tipo_dato = filters.ChoiceFilter(choices=[
        ('string', 'Texto'),
        ('integer', 'Número Entero'),
        ('decimal', 'Número Decimal'),
        ('boolean', 'Verdadero/Falso'),
        ('json', 'JSON')
    ])
    
    class Meta:
        model = ConfiguracionSistema
        fields = ['clave', 'descripcion', 'tipo_dato']
    
    def buscar_general(self, queryset, name, value):
        """
        Búsqueda general en configuraciones
        """
        if value:
            return queryset.filter(
                Q(clave__icontains=value) |
                Q(descripcion__icontains=value) |
                Q(valor__icontains=value)
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
    
    def filtrar_semana_pasada(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            inicio_semana_actual = hoy - timedelta(days=hoy.weekday())
            inicio_semana_pasada = inicio_semana_actual - timedelta(days=7)
            fin_semana_pasada = inicio_semana_actual - timedelta(days=1)
            return queryset.filter(
                creado_en__date__gte=inicio_semana_pasada,
                creado_en__date__lte=fin_semana_pasada
            )
        return queryset
    
    def filtrar_este_mes(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            inicio_mes = hoy.replace(day=1)
            return queryset.filter(creado_en__date__gte=inicio_mes)
        return queryset
    
    def filtrar_mes_pasado(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            inicio_mes_actual = hoy.replace(day=1)
            if inicio_mes_actual.month == 1:
                inicio_mes_pasado = inicio_mes_actual.replace(year=inicio_mes_actual.year-1, month=12)
            else:
                inicio_mes_pasado = inicio_mes_actual.replace(month=inicio_mes_actual.month-1)
            fin_mes_pasado = inicio_mes_actual - timedelta(days=1)
            return queryset.filter(
                creado_en__date__gte=inicio_mes_pasado,
                creado_en__date__lte=fin_mes_pasado
            )
        return queryset
    
    def filtrar_este_año(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            inicio_año = hoy.replace(month=1, day=1)
            return queryset.filter(creado_en__date__gte=inicio_año)
        return queryset
    
    def filtrar_año_pasado(self, queryset, name, value):
        if value:
            hoy = timezone.now().date()
            inicio_año_pasado = date(hoy.year - 1, 1, 1)
            fin_año_pasado = date(hoy.year - 1, 12, 31)
            return queryset.filter(
                creado_en__date__gte=inicio_año_pasado,
                creado_en__date__lte=fin_año_pasado
            )
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