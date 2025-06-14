"""
FILTROS DE FACTURACIÓN - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Filtros personalizados para ViewSets de facturación
"""

import django_filters
from django.db import models
from datetime import date, timedelta

from .models import Factura, Boleta, NotaCredito, NotaDebito, GuiaRemision, SerieComprobante

from aplicaciones.core.models import Cliente



# =============================================================================
# FILTROS BASE
# =============================================================================
class ComprobanteBaseFilter(django_filters.FilterSet):
    """Filtro base para comprobantes"""
    
    # Filtros por fecha
    fecha_emision = django_filters.DateFilter(field_name='fecha_emision')
    fecha_desde = django_filters.DateFilter(field_name='fecha_emision', lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name='fecha_emision', lookup_expr='lte')
    
    # Filtros por rango de fechas predefinidos
    periodo = django_filters.ChoiceFilter(
        choices=[
            ('hoy', 'Hoy'),
            ('ayer', 'Ayer'),
            ('semana', 'Esta semana'),
            ('mes', 'Este mes'),
            ('trimestre', 'Este trimestre'),
            ('año', 'Este año')
        ],
        method='filtrar_por_periodo'
    )
    
    # Filtros por cliente
    cliente = django_filters.ModelChoiceFilter(queryset=Cliente.objects.filter(activo=True))
    cliente_documento = django_filters.CharFilter(field_name='cliente__numero_documento', lookup_expr='icontains')
    cliente_nombre = django_filters.CharFilter(field_name='cliente__razon_social', lookup_expr='icontains')
    
    # Filtros por serie y número
    serie = django_filters.CharFilter(field_name='serie', lookup_expr='iexact')
    numero = django_filters.NumberFilter(field_name='numero')
    numero_desde = django_filters.NumberFilter(field_name='numero', lookup_expr='gte')
    numero_hasta = django_filters.NumberFilter(field_name='numero', lookup_expr='lte')
    
    # Filtros por montos
    total = django_filters.NumberFilter(field_name='total')
    total_desde = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_hasta = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    
    # Filtros por estado SUNAT
    estado_sunat = django_filters.ChoiceFilter(
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('ACEPTADO', 'Aceptado'),
            ('RECHAZADO', 'Rechazado'),
            ('ANULADO', 'Anulado')
        ]
    )
    
    # Filtros por moneda
    moneda = django_filters.ChoiceFilter(
        choices=[
            ('PEN', 'Soles'),
            ('USD', 'Dólares'),
            ('EUR', 'Euros')
        ]
    )
    
    # Filtro por enviado a SUNAT
    enviado_sunat = django_filters.BooleanFilter(
        field_name='nubefact_id',
        lookup_expr='isnull',
        exclude=True,
        label='Enviado a SUNAT'
    )
    
    def filtrar_por_periodo(self, queryset, name, value):
        """Filtrar por períodos predefinidos"""
        hoy = date.today()
        
        if value == 'hoy':
            return queryset.filter(fecha_emision=hoy)
        elif value == 'ayer':
            ayer = hoy - timedelta(days=1)
            return queryset.filter(fecha_emision=ayer)
        elif value == 'semana':
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            return queryset.filter(fecha_emision__gte=inicio_semana)
        elif value == 'mes':
            inicio_mes = hoy.replace(day=1)
            return queryset.filter(fecha_emision__gte=inicio_mes)
        elif value == 'trimestre':
            mes_actual = hoy.month
            if mes_actual <= 3:
                inicio_trimestre = hoy.replace(month=1, day=1)
            elif mes_actual <= 6:
                inicio_trimestre = hoy.replace(month=4, day=1)
            elif mes_actual <= 9:
                inicio_trimestre = hoy.replace(month=7, day=1)
            else:
                inicio_trimestre = hoy.replace(month=10, day=1)
            return queryset.filter(fecha_emision__gte=inicio_trimestre)
        elif value == 'año':
            inicio_año = hoy.replace(month=1, day=1)
            return queryset.filter(fecha_emision__gte=inicio_año)
        
        return queryset


# =============================================================================
# FILTROS ESPECÍFICOS
# =============================================================================
class FacturaFilter(ComprobanteBaseFilter):
    """Filtro específico para facturas"""
    
    # Filtros específicos de facturas
    condicion_pago = django_filters.ChoiceFilter(
        choices=[
            ('CONTADO', 'Contado'),
            ('CREDITO_30', 'Crédito 30 días'),
            ('CREDITO_60', 'Crédito 60 días'),
            ('CREDITO_90', 'Crédito 90 días')
        ]
    )
    
    medio_pago = django_filters.ChoiceFilter(
        choices=[
            ('EFECTIVO', 'Efectivo'),
            ('TRANSFERENCIA', 'Transferencia'),
            ('TARJETA', 'Tarjeta'),
            ('CHEQUE', 'Cheque')
        ]
    )
    
    # Filtro por vencimiento
    fecha_vencimiento = django_filters.DateFilter(field_name='fecha_vencimiento')
    vencimiento_desde = django_filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='gte')
    vencimiento_hasta = django_filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='lte')
    
    # Filtros por estado de vencimiento
    vencidas = django_filters.BooleanFilter(
        method='filtrar_facturas_vencidas',
        label='Facturas vencidas'
    )
    
    por_vencer = django_filters.NumberFilter(
        method='filtrar_por_vencer',
        label='Por vencer en X días'
    )
    
    # Filtro por cliente con RUC (solo facturas)
    solo_ruc = django_filters.BooleanFilter(
        method='filtrar_solo_ruc',
        label='Solo clientes con RUC'
    )
    
    class Meta:
        model = Factura
        fields = [
            'fecha_emision', 'fecha_desde', 'fecha_hasta', 'periodo',
            'cliente', 'cliente_documento', 'cliente_nombre',
            'serie', 'numero', 'numero_desde', 'numero_hasta',
            'total', 'total_desde', 'total_hasta',
            'estado_sunat', 'moneda', 'enviado_sunat',
            'condicion_pago', 'medio_pago',
            'fecha_vencimiento', 'vencimiento_desde', 'vencimiento_hasta',
            'vencidas', 'por_vencer', 'solo_ruc'
        ]
    
    def filtrar_facturas_vencidas(self, queryset, name, value):
        """Filtrar facturas vencidas"""
        if value:
            hoy = date.today()
            return queryset.filter(
                fecha_vencimiento__lt=hoy,
                estado_sunat__in=['ACEPTADO', 'PENDIENTE']
            )
        return queryset
    
    def filtrar_por_vencer(self, queryset, name, value):
        """Filtrar facturas que vencen en X días"""
        if value:
            fecha_limite = date.today() + timedelta(days=int(value))
            return queryset.filter(
                fecha_vencimiento__lte=fecha_limite,
                fecha_vencimiento__gte=date.today(),
                estado_sunat__in=['ACEPTADO', 'PENDIENTE']
            )
        return queryset
    
    def filtrar_solo_ruc(self, queryset, name, value):
        """Filtrar solo clientes con RUC"""
        if value:
            return queryset.filter(cliente__tipo_documento='RUC')
        return queryset


class BoletaFilter(ComprobanteBaseFilter):
    """Filtro específico para boletas"""
    
    # Filtro por tipo de cliente (solo DNI para boletas)
    solo_dni = django_filters.BooleanFilter(
        method='filtrar_solo_dni',
        label='Solo clientes con DNI'
    )
    
    # Filtro por montos (boletas generalmente son montos menores)
    monto_menor = django_filters.NumberFilter(
        field_name='total',
        lookup_expr='lt',
        label='Monto menor a'
    )
    
    monto_mayor = django_filters.NumberFilter(
        field_name='total',
        lookup_expr='gt',
        label='Monto mayor a'
    )
    
    # Filtro por rango de IGV
    igv_desde = django_filters.NumberFilter(field_name='igv', lookup_expr='gte')
    igv_hasta = django_filters.NumberFilter(field_name='igv', lookup_expr='lte')
    
    class Meta:
        model = Boleta
        fields = [
            'fecha_emision', 'fecha_desde', 'fecha_hasta', 'periodo',
            'cliente', 'cliente_documento', 'cliente_nombre',
            'serie', 'numero', 'numero_desde', 'numero_hasta',
            'total', 'total_desde', 'total_hasta',
            'estado_sunat', 'moneda', 'enviado_sunat',
            'solo_dni', 'monto_menor', 'monto_mayor',
            'igv_desde', 'igv_hasta'
        ]
    
    def filtrar_solo_dni(self, queryset, name, value):
        """Filtrar solo clientes con DNI"""
        if value:
            return queryset.filter(cliente__tipo_documento='DNI')
        return queryset


class NotaCreditoFilter(ComprobanteBaseFilter):
    """Filtro específico para notas de crédito"""
    
    # Filtros específicos de notas de crédito
    codigo_motivo = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Anulación de la operación'),
            ('02', 'Anulación por error en el RUC'),
            ('03', 'Corrección por error en la descripción'),
            ('04', 'Descuento global'),
            ('05', 'Descuento por ítem'),
            ('06', 'Devolución total'),
            ('07', 'Devolución por ítem'),
            ('08', 'Bonificación'),
            ('09', 'Disminución en el valor'),
            ('10', 'Otros conceptos')
        ]
    )
    
    # Filtro por documento modificado
    documento_modificado_serie = django_filters.CharFilter(
        field_name='documento_modificado_serie',
        lookup_expr='iexact'
    )
    
    documento_modificado_numero = django_filters.NumberFilter(
        field_name='documento_modificado_numero'
    )
    
    documento_modificado_tipo = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Factura'),
            ('03', 'Boleta'),
            ('07', 'Nota de Crédito'),
            ('08', 'Nota de Débito')
        ]
    )
    
    # Filtro por descripción del motivo
    descripcion_motivo = django_filters.CharFilter(
        field_name='descripcion_motivo',
        lookup_expr='icontains'
    )
    
    # Filtro por notas de crédito automáticas vs manuales
    automatica = django_filters.BooleanFilter(
        method='filtrar_automaticas',
        label='Notas automáticas'
    )
    
    class Meta:
        model = NotaCredito
        fields = [
            'fecha_emision', 'fecha_desde', 'fecha_hasta', 'periodo',
            'cliente', 'cliente_documento', 'cliente_nombre',
            'serie', 'numero', 'numero_desde', 'numero_hasta',
            'total', 'total_desde', 'total_hasta',
            'estado_sunat', 'moneda', 'enviado_sunat',
            'codigo_motivo', 'documento_modificado_serie',
            'documento_modificado_numero', 'documento_modificado_tipo',
            'descripcion_motivo', 'automatica'
        ]
    
    def filtrar_automaticas(self, queryset, name, value):
        """Filtrar notas de crédito automáticas"""
        if value:
            # Las automáticas generalmente tienen códigos 01, 06, 07
            return queryset.filter(codigo_motivo__in=['01', '06', '07'])
        else:
            # Las manuales tienen otros códigos
            return queryset.exclude(codigo_motivo__in=['01', '06', '07'])


class SerieComprobanteFilter(django_filters.FilterSet):
    """Filtro para series de comprobantes"""
    
    tipo_comprobante = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Factura'),
            ('03', 'Boleta'),
            ('07', 'Nota de Crédito'),
            ('08', 'Nota de Débito'),
            ('09', 'Guía de Remisión')
        ]
    )
    
    serie = django_filters.CharFilter(lookup_expr='icontains')
    
    activa = django_filters.BooleanFilter(field_name='activa')
    
    # Filtro por rango de numeración
    numero_desde = django_filters.NumberFilter(field_name='siguiente_numero', lookup_expr='gte')
    numero_hasta = django_filters.NumberFilter(field_name='siguiente_numero', lookup_expr='lte')
    
    # Filtro por series que necesitan atención
    por_agotar = django_filters.BooleanFilter(
        method='filtrar_por_agotar',
        label='Series por agotar'
    )
    
    class Meta:
        model = SerieComprobante
        fields = [
            'tipo_comprobante', 'serie', 'activa',
            'numero_desde', 'numero_hasta', 'por_agotar'
        ]
    
    def filtrar_por_agotar(self, queryset, name, value):
        """Filtrar series que están por agotarse"""
        if value:
            # Series que han alcanzado el 90% de su capacidad (ej: 99000+)
            return queryset.filter(siguiente_numero__gte=90000)
        return queryset


# =============================================================================
# FILTROS AVANZADOS
# =============================================================================
class ComprobanteAvanzadoFilter(django_filters.FilterSet):
    """Filtro avanzado que combina múltiples modelos"""
    
    # Filtro por cualquier tipo de comprobante
    tipo_comprobante = django_filters.ChoiceFilter(
        choices=[
            ('factura', 'Facturas'),
            ('boleta', 'Boletas'),
            ('nota_credito', 'Notas de Crédito'),
            ('nota_debito', 'Notas de Débito')
        ],
        method='filtrar_por_tipo'
    )
    
    # Filtros generales
    fecha_desde = django_filters.DateFilter(method='filtrar_fecha_desde')
    fecha_hasta = django_filters.DateFilter(method='filtrar_fecha_hasta')
    
    cliente_busqueda = django_filters.CharFilter(method='filtrar_cliente_general')
    
    # Filtros por estado
    pendientes_sunat = django_filters.BooleanFilter(method='filtrar_pendientes_sunat')
    con_errores = django_filters.BooleanFilter(method='filtrar_con_errores')
    
    # Filtros por montos consolidados
    total_ventas_desde = django_filters.NumberFilter(method='filtrar_total_ventas_desde')
    total_ventas_hasta = django_filters.NumberFilter(method='filtrar_total_ventas_hasta')
    
    def filtrar_por_tipo(self, queryset, name, value):
        """Filtrar por tipo de comprobante específico"""
        # Este método se implementaría en una vista que maneje múltiples tipos
        return queryset
    
    def filtrar_fecha_desde(self, queryset, name, value):
        """Filtrar desde fecha en cualquier modelo"""
        return queryset.filter(fecha_emision__gte=value)
    
    def filtrar_fecha_hasta(self, queryset, name, value):
        """Filtrar hasta fecha en cualquier modelo"""
        return queryset.filter(fecha_emision__lte=value)
    
    def filtrar_cliente_general(self, queryset, name, value):
        """Buscar en nombre o documento del cliente"""
        return queryset.filter(
            models.Q(cliente__razon_social__icontains=value) |
            models.Q(cliente__numero_documento__icontains=value)
        )
    
    def filtrar_pendientes_sunat(self, queryset, name, value):
        """Filtrar comprobantes pendientes en SUNAT"""
        if value:
            return queryset.filter(
                models.Q(estado_sunat='PENDIENTE') |
                models.Q(nubefact_id__isnull=True)
            )
        return queryset
    
    def filtrar_con_errores(self, queryset, name, value):
        """Filtrar comprobantes con errores"""
        if value:
            return queryset.filter(estado_sunat='RECHAZADO')
        return queryset
    
    def filtrar_total_ventas_desde(self, queryset, name, value):
        """Filtrar por monto total desde"""
        return queryset.filter(total__gte=value)
    
    def filtrar_total_ventas_hasta(self, queryset, name, value):
        """Filtrar por monto total hasta"""
        return queryset.filter(total__lte=value)


# =============================================================================
# FILTROS DE REPORTES
# =============================================================================
class ReporteVentasFilter(django_filters.FilterSet):
    """Filtro específico para reportes de ventas"""
    
    # Agrupaciones para reportes
    agrupar_por = django_filters.ChoiceFilter(
        choices=[
            ('dia', 'Por día'),
            ('semana', 'Por semana'),
            ('mes', 'Por mes'),
            ('cliente', 'Por cliente'),
            ('producto', 'Por producto'),
            ('vendedor', 'Por vendedor')
        ],
        method='agrupar_resultados'
    )
    
    # Métricas a incluir
    incluir_igv = django_filters.BooleanFilter(
        method='incluir_igv_separado',
        label='Incluir IGV separado'
    )
    
    incluir_costos = django_filters.BooleanFilter(
        method='incluir_analisis_costos',
        label='Incluir análisis de costos'
    )
    
    # Filtros de rendimiento
    top_clientes = django_filters.NumberFilter(
        method='filtrar_top_clientes',
        label='Top N clientes'
    )
    
    top_productos = django_filters.NumberFilter(
        method='filtrar_top_productos',
        label='Top N productos'
    )
    
    def agrupar_resultados(self, queryset, name, value):
        """Aplicar agrupación según criterio"""
        # La lógica de agrupación se implementaría en la vista
        return queryset
    
    def incluir_igv_separado(self, queryset, name, value):
        """Incluir análisis de IGV separado"""
        return queryset
    
    def incluir_analisis_costos(self, queryset, name, value):
        """Incluir análisis de costos y márgenes"""
        return queryset
    
    def filtrar_top_clientes(self, queryset, name, value):
        """Filtrar top N clientes por ventas"""
        if value:
            # Implementar lógica para top clientes
            pass
        return queryset
    
    def filtrar_top_productos(self, queryset, name, value):
        """Filtrar top N productos por ventas"""
        if value:
            # Implementar lógica para top productos
            pass
        return queryset


# =============================================================================
# FILTROS PERSONALIZADOS ADICIONALES
# =============================================================================
class RangoFechasFilter(django_filters.Filter):
    """Filtro personalizado para rangos de fechas flexibles"""
    
    def filter(self, qs, value):
        if not value:
            return qs
        
        # Parsear valor como "2024-01-01,2024-12-31"
        try:
            fecha_inicio, fecha_fin = value.split(',')
            fecha_inicio = date.fromisoformat(fecha_inicio.strip())
            fecha_fin = date.fromisoformat(fecha_fin.strip())
            
            return qs.filter(
                fecha_emision__gte=fecha_inicio,
                fecha_emision__lte=fecha_fin
            )
        except (ValueError, AttributeError):
            return qs


class MultiSerieFilter(django_filters.Filter):
    """Filtro para múltiples series separadas por coma"""
    
    def filter(self, qs, value):
        if not value:
            return qs
        
        # Parsear valor como "F001,F002,B001"
        series = [serie.strip() for serie in value.split(',')]
        return qs.filter(serie__in=series)


class EstadoCompletoFilter(django_filters.Filter):
    """Filtro que combina estado SUNAT y estado de envío"""
    
    def filter(self, qs, value):
        if not value:
            return qs
        
        if value == 'no_enviado':
            return qs.filter(nubefact_id__isnull=True)
        elif value == 'enviado_pendiente':
            return qs.filter(
                nubefact_id__isnull=False,
                estado_sunat='PENDIENTE'
            )
        elif value == 'completado':
            return qs.filter(estado_sunat='ACEPTADO')
        elif value == 'con_problemas':
            return qs.filter(estado_sunat='RECHAZADO')
        
        return qs


# =============================================================================
# FILTROS DE FACTURACIÓN FALTANTES
# =============================================================================

class NotaDebitoFilter(ComprobanteBaseFilter):
    """Filtro específico para notas de débito"""
    
    # Filtros específicos de notas de débito
    codigo_motivo = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Intereses por mora'),
            ('02', 'Aumento en el valor'),
            ('03', 'Penalidades/otros conceptos'),
            ('10', 'Ajustes de operaciones de exportación'),
            ('11', 'Ajustes afectos al IVAP')
        ]
    )
    
    # Filtro por documento modificado
    documento_modificado_serie = django_filters.CharFilter(
        field_name='documento_modificado_serie',
        lookup_expr='iexact'
    )
    
    documento_modificado_numero = django_filters.NumberFilter(
        field_name='documento_modificado_numero'
    )
    
    documento_modificado_tipo = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Factura'),
            ('03', 'Boleta')
        ]
    )
    
    # Filtro por descripción del motivo
    descripcion_motivo = django_filters.CharFilter(
        field_name='descripcion_motivo',
        lookup_expr='icontains'
    )
    
    # Filtro por notas de débito automáticas vs manuales
    automatica = django_filters.BooleanFilter(
        method='filtrar_automaticas',
        label='Notas automáticas'
    )
    
    # Filtro por tipo de operación (intereses, penalidades, etc.)
    tipo_operacion = django_filters.ChoiceFilter(
        choices=[
            ('intereses', 'Intereses por mora'),
            ('penalidades', 'Penalidades'),
            ('ajustes', 'Ajustes'),
            ('otros', 'Otros conceptos')
        ],
        method='filtrar_por_tipo_operacion'
    )
    
    class Meta:
        model = NotaDebito
        fields = [
            'fecha_emision', 'fecha_desde', 'fecha_hasta', 'periodo',
            'cliente', 'cliente_documento', 'cliente_nombre',
            'serie', 'numero', 'numero_desde', 'numero_hasta',
            'total', 'total_desde', 'total_hasta',
            'estado_sunat', 'moneda', 'enviado_sunat',
            'codigo_motivo', 'documento_modificado_serie',
            'documento_modificado_numero', 'documento_modificado_tipo',
            'descripcion_motivo', 'automatica', 'tipo_operacion'
        ]
    
    def filtrar_automaticas(self, queryset, name, value):
        """Filtrar notas de débito automáticas"""
        if value:
            # Las automáticas generalmente son intereses por mora
            return queryset.filter(codigo_motivo='01')
        else:
            # Las manuales tienen otros códigos
            return queryset.exclude(codigo_motivo='01')
    
    def filtrar_por_tipo_operacion(self, queryset, name, value):
        """Filtrar por tipo de operación"""
        if value == 'intereses':
            return queryset.filter(codigo_motivo='01')
        elif value == 'penalidades':
            return queryset.filter(codigo_motivo='03')
        elif value == 'ajustes':
            return queryset.filter(codigo_motivo__in=['10', '11'])
        elif value == 'otros':
            return queryset.filter(codigo_motivo='02')
        return queryset


class GuiaRemisionFilter(django_filters.FilterSet):
    """Filtro específico para guías de remisión"""
    
    # Filtros por fecha
    fecha_emision = django_filters.DateFilter(field_name='fecha_emision')
    fecha_desde = django_filters.DateFilter(field_name='fecha_emision', lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name='fecha_emision', lookup_expr='lte')
    
    # Filtros por traslado
    fecha_traslado = django_filters.DateFilter(field_name='fecha_inicio_traslado')
    fecha_traslado_desde = django_filters.DateFilter(field_name='fecha_inicio_traslado', lookup_expr='gte')
    fecha_traslado_hasta = django_filters.DateFilter(field_name='fecha_inicio_traslado', lookup_expr='lte')
    
    # Filtros por tipo de traslado
    tipo_traslado = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Venta'),
            ('02', 'Compra'),
            ('04', 'Traslado entre establecimientos de la misma empresa'),
            ('08', 'Importación'),
            ('09', 'Exportación'),
            ('13', 'Otros'),
            ('14', 'Venta sujeta a confirmación del comprador'),
            ('18', 'Traslado emisor itinerante CP'),
            ('19', 'Traslado a zona primaria')
        ]
    )
    
    modalidad_transporte = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Transporte público'),
            ('02', 'Transporte privado')
        ]
    )
    
    # Filtros por transportista
    transportista_ruc = django_filters.CharFilter(
        field_name='transportista_ruc',
        lookup_expr='icontains'
    )
    
    transportista_nombre = django_filters.CharFilter(
        field_name='transportista_nombre',
        lookup_expr='icontains'
    )
    
    # Filtros por vehículo
    vehiculo_placa = django_filters.CharFilter(
        field_name='vehiculo_placa',
        lookup_expr='icontains'
    )
    
    # Filtros por conductor
    conductor_nombre = django_filters.CharFilter(
        field_name='conductor_nombre',
        lookup_expr='icontains'
    )
    
    conductor_licencia = django_filters.CharFilter(
        field_name='conductor_licencia',
        lookup_expr='icontains'
    )
    
    # Filtros por ubicación
    ubigeo_origen = django_filters.CharFilter(
        field_name='ubigeo_origen',
        lookup_expr='exact'
    )
    
    ubigeo_destino = django_filters.CharFilter(
        field_name='ubigeo_destino',
        lookup_expr='exact'
    )
    
    # Filtros por peso
    peso_desde = django_filters.NumberFilter(
        field_name='peso_bruto_total',
        lookup_expr='gte'
    )
    
    peso_hasta = django_filters.NumberFilter(
        field_name='peso_bruto_total',
        lookup_expr='lte'
    )
    
    # Filtros por estado SUNAT
    estado_sunat = django_filters.ChoiceFilter(
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('ACEPTADO', 'Aceptado'),
            ('RECHAZADO', 'Rechazado'),
            ('ANULADO', 'Anulado')
        ]
    )
    
    # Filtro por envío a SUNAT
    enviado_sunat = django_filters.BooleanFilter(
        field_name='nubefact_id',
        lookup_expr='isnull',
        exclude=True,
        label='Enviado a SUNAT'
    )
    
    # Filtros especiales
    traslados_hoy = django_filters.BooleanFilter(
        method='filtrar_traslados_hoy',
        label='Traslados de hoy'
    )
    
    traslados_pendientes = django_filters.BooleanFilter(
        method='filtrar_traslados_pendientes',
        label='Traslados pendientes'
    )
    
    por_transportista = django_filters.CharFilter(
        method='filtrar_por_transportista',
        label='Buscar por transportista'
    )
    
    class Meta:
        model = GuiaRemision
        fields = [
            'fecha_emision', 'fecha_desde', 'fecha_hasta',
            'fecha_traslado', 'fecha_traslado_desde', 'fecha_traslado_hasta',
            'tipo_traslado', 'modalidad_transporte',
            'transportista_ruc', 'transportista_nombre',
            'vehiculo_placa', 'conductor_nombre', 'conductor_licencia',
            'ubigeo_origen', 'ubigeo_destino',
            'peso_desde', 'peso_hasta',
            'estado_sunat', 'enviado_sunat',
            'traslados_hoy', 'traslados_pendientes', 'por_transportista'
        ]
    
    def filtrar_traslados_hoy(self, queryset, name, value):
        """Filtrar traslados programados para hoy"""
        if value:
            hoy = date.today()
            return queryset.filter(fecha_inicio_traslado=hoy)
        return queryset
    
    def filtrar_traslados_pendientes(self, queryset, name, value):
        """Filtrar traslados aún no realizados"""
        if value:
            hoy = date.today()
            return queryset.filter(
                fecha_inicio_traslado__gte=hoy,
                estado_sunat__in=['PENDIENTE', 'ACEPTADO']
            )
        return queryset
    
    def filtrar_por_transportista(self, queryset, name, value):
        """Filtrar por RUC o nombre del transportista"""
        return queryset.filter(
            models.Q(transportista_ruc__icontains=value) |
            models.Q(transportista_nombre__icontains=value)
        )


