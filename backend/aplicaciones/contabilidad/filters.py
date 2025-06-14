
import django_filters
from django.db import models
from datetime import date, timedelta

# =============================================================================
# FILTROS DE CONTABILIDAD FALTANTES
# =============================================================================

class BalanceComprobacionFilter(django_filters.FilterSet):
    """Filtro para balances de comprobación"""
    
    # Filtros por período
    año = django_filters.NumberFilter(field_name='periodo__año')
    mes = django_filters.NumberFilter(field_name='periodo__mes')
    periodo_nombre = django_filters.CharFilter(field_name='periodo__nombre', lookup_expr='icontains')
    
    # Filtros por cuenta
    codigo_cuenta = django_filters.CharFilter(field_name='cuenta__codigo', lookup_expr='istartswith')
    nombre_cuenta = django_filters.CharFilter(field_name='cuenta__nombre', lookup_expr='icontains')
    tipo_cuenta = django_filters.ChoiceFilter(
        field_name='cuenta__tipo_cuenta',
        choices=[
            ('activo', 'Activo'),
            ('pasivo', 'Pasivo'),
            ('patrimonio', 'Patrimonio'),
            ('ingreso', 'Ingreso'),
            ('gasto', 'Gasto'),
            ('costo', 'Costo'),
            ('resultado', 'Resultado'),
            ('orden', 'Cuentas de Orden')
        ]
    )
    
    naturaleza_cuenta = django_filters.ChoiceFilter(
        field_name='cuenta__naturaleza',
        choices=[
            ('deudora', 'Deudora'),
            ('acreedora', 'Acreedora')
        ]
    )
    
    # Filtros por fechas
    fecha_desde = django_filters.DateFilter(field_name='fecha_desde')
    fecha_hasta = django_filters.DateFilter(field_name='fecha_hasta')
    fecha_generacion_desde = django_filters.DateFilter(field_name='fecha_generacion', lookup_expr='gte')
    fecha_generacion_hasta = django_filters.DateFilter(field_name='fecha_generacion', lookup_expr='lte')
    
    # Filtros por montos
    saldo_inicial_desde = django_filters.NumberFilter(method='filtrar_saldo_inicial_desde')
    saldo_inicial_hasta = django_filters.NumberFilter(method='filtrar_saldo_inicial_hasta')
    saldo_final_desde = django_filters.NumberFilter(method='filtrar_saldo_final_desde')
    saldo_final_hasta = django_filters.NumberFilter(method='filtrar_saldo_final_hasta')
    
    movimientos_desde = django_filters.NumberFilter(method='filtrar_movimientos_desde')
    movimientos_hasta = django_filters.NumberFilter(method='filtrar_movimientos_hasta')
    
    # Filtros especiales
    solo_con_movimientos = django_filters.BooleanFilter(method='filtrar_solo_con_movimientos')
    solo_con_saldo = django_filters.BooleanFilter(method='filtrar_solo_con_saldo')
    balances_oficiales = django_filters.BooleanFilter(field_name='es_balance_oficial')
    
    # Filtro por usuario
    usuario_generacion = django_filters.CharFilter(field_name='usuario_generacion__username', lookup_expr='icontains')
    
    class Meta:
        model = BalanceComprobacion
        fields = [
            'año', 'mes', 'periodo_nombre',
            'codigo_cuenta', 'nombre_cuenta', 'tipo_cuenta', 'naturaleza_cuenta',
            'fecha_desde', 'fecha_hasta', 'fecha_generacion_desde', 'fecha_generacion_hasta',
            'saldo_inicial_desde', 'saldo_inicial_hasta',
            'saldo_final_desde', 'saldo_final_hasta',
            'movimientos_desde', 'movimientos_hasta',
            'solo_con_movimientos', 'solo_con_saldo', 'balances_oficiales',
            'usuario_generacion'
        ]
    
    def filtrar_saldo_inicial_desde(self, queryset, name, value):
        """Filtrar por saldo inicial mínimo"""
        return queryset.filter(
            models.Q(saldo_inicial_debe__gte=value) |
            models.Q(saldo_inicial_haber__gte=value)
        )
    
    def filtrar_saldo_inicial_hasta(self, queryset, name, value):
        """Filtrar por saldo inicial máximo"""
        return queryset.filter(
            models.Q(saldo_inicial_debe__lte=value) |
            models.Q(saldo_inicial_haber__lte=value)
        )
    
    def filtrar_saldo_final_desde(self, queryset, name, value):
        """Filtrar por saldo final mínimo"""
        return queryset.filter(
            models.Q(saldo_final_debe__gte=value) |
            models.Q(saldo_final_haber__gte=value)
        )
    
    def filtrar_saldo_final_hasta(self, queryset, name, value):
        """Filtrar por saldo final máximo"""
        return queryset.filter(
            models.Q(saldo_final_debe__lte=value) |
            models.Q(saldo_final_haber__lte=value)
        )
    
    def filtrar_movimientos_desde(self, queryset, name, value):
        """Filtrar por movimientos mínimos"""
        return queryset.filter(
            models.Q(movimientos_debe__gte=value) |
            models.Q(movimientos_haber__gte=value)
        )
    
    def filtrar_movimientos_hasta(self, queryset, name, value):
        """Filtrar por movimientos máximos"""
        return queryset.filter(
            models.Q(movimientos_debe__lte=value) |
            models.Q(movimientos_haber__lte=value)
        )
    
    def filtrar_solo_con_movimientos(self, queryset, name, value):
        """Filtrar solo cuentas con movimientos"""
        if value:
            return queryset.filter(
                models.Q(movimientos_debe__gt=0) |
                models.Q(movimientos_haber__gt=0)
            )
        return queryset
    
    def filtrar_solo_con_saldo(self, queryset, name, value):
        """Filtrar solo cuentas con saldo"""
        if value:
            return queryset.filter(
                models.Q(saldo_final_debe__gt=0) |
                models.Q(saldo_final_haber__gt=0)
            )
        return queryset


class PeriodoContableFilter(django_filters.FilterSet):
    """Filtro para períodos contables"""
    
    # Filtros básicos
    año = django_filters.NumberFilter(field_name='año')
    año_desde = django_filters.NumberFilter(field_name='año', lookup_expr='gte')
    año_hasta = django_filters.NumberFilter(field_name='año', lookup_expr='lte')
    
    mes = django_filters.NumberFilter(field_name='mes')
    
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    
    # Filtros por estado
    estado = django_filters.ChoiceFilter(
        choices=[
            ('abierto', 'Abierto'),
            ('cerrado', 'Cerrado'),
            ('auditoria', 'En Auditoría'),
            ('bloqueado', 'Bloqueado')
        ]
    )
    
    # Filtros por fechas
    fecha_inicio_desde = django_filters.DateFilter(field_name='fecha_inicio', lookup_expr='gte')
    fecha_inicio_hasta = django_filters.DateFilter(field_name='fecha_inicio', lookup_expr='lte')
    fecha_fin_desde = django_filters.DateFilter(field_name='fecha_fin', lookup_expr='gte')
    fecha_fin_hasta = django_filters.DateFilter(field_name='fecha_fin', lookup_expr='lte')
    
    # Filtros especiales
    periodo_principal = django_filters.BooleanFilter(field_name='es_periodo_principal')
    permite_reapertura = django_filters.BooleanFilter(field_name='permite_reapertura')
    
    # Filtros por cierre
    cerrado_por = django_filters.CharFilter(field_name='usuario_cierre__username', lookup_expr='icontains')
    fecha_cierre_desde = django_filters.DateFilter(field_name='fecha_cierre', lookup_expr='gte')
    fecha_cierre_hasta = django_filters.DateFilter(field_name='fecha_cierre', lookup_expr='lte')
    
    # Filtros por rango de períodos
    periodo_actual = django_filters.BooleanFilter(method='filtrar_periodo_actual')
    periodos_abiertos = django_filters.BooleanFilter(method='filtrar_periodos_abiertos')
    periodos_cerrados = django_filters.BooleanFilter(method='filtrar_periodos_cerrados')
    
    class Meta:
        model = PeriodoContable
        fields = [
            'año', 'año_desde', 'año_hasta', 'mes', 'nombre', 'estado',
            'fecha_inicio_desde', 'fecha_inicio_hasta',
            'fecha_fin_desde', 'fecha_fin_hasta',
            'periodo_principal', 'permite_reapertura',
            'cerrado_por', 'fecha_cierre_desde', 'fecha_cierre_hasta',
            'periodo_actual', 'periodos_abiertos', 'periodos_cerrados'
        ]
    
    def filtrar_periodo_actual(self, queryset, name, value):
        """Filtrar período actual"""
        if value:
            hoy = date.today()
            return queryset.filter(
                fecha_inicio__lte=hoy,
                fecha_fin__gte=hoy,
                estado='abierto'
            )
        return queryset
    
    def filtrar_periodos_abiertos(self, queryset, name, value):
        """Filtrar períodos abiertos"""
        if value:
            return queryset.filter(estado='abierto')
        return queryset
    
    def filtrar_periodos_cerrados(self, queryset, name, value):
        """Filtrar períodos cerrados"""
        if value:
            return queryset.filter(estado='cerrado')
        return queryset


# =============================================================================
# FILTROS AVANZADOS Y PERSONALIZADOS
# =============================================================================

class MovimientoContableFilter(django_filters.FilterSet):
    
    """Filtro avanzado para análisis de movimientos contables"""
    
    # Filtros por período
    año = django_filters.NumberFilter(field_name='asiento__periodo__año')
    mes = django_filters.NumberFilter(method='filtrar_por_mes')
    trimestre = django_filters.NumberFilter(method='filtrar_por_trimestre')
    
    # Filtros por cuenta
    elemento = django_filters.CharFilter(method='filtrar_por_elemento')
    rubro = django_filters.CharFilter(method='filtrar_por_rubro')
    cuenta = django_filters.CharFilter(method='filtrar_por_cuenta')
    
    # Filtros por tipo de asiento
    tipo_asiento = django_filters.ChoiceFilter(
        field_name='asiento__tipo_asiento',
        choices=[
            ('VENTA', 'Venta'),
            ('COMPRA', 'Compra'),
            ('PAGO', 'Pago'),
            ('COBRO', 'Cobro'),
            ('AJUSTE', 'Ajuste'),
            ('CIERRE', 'Cierre')
        ]
    )
    
    # Filtros por documento
    documento_tipo = django_filters.CharFilter(field_name='tipo_documento')
    documento_numero = django_filters.CharFilter(field_name='numero_documento', lookup_expr='icontains')
    
    # Filtros por montos
    monto_desde = django_filters.NumberFilter(method='filtrar_monto_desde')
    monto_hasta = django_filters.NumberFilter(method='filtrar_monto_hasta')
    
    def filtrar_por_mes(self, queryset, name, value):
        """Filtrar por mes específico"""
        return queryset.filter(asiento__fecha_asiento__month=value)
    
    def filtrar_por_trimestre(self, queryset, name, value):
        """Filtrar por trimestre"""
        if value == 1:
            return queryset.filter(asiento__fecha_asiento__month__in=[1, 2, 3])
        elif value == 2:
            return queryset.filter(asiento__fecha_asiento__month__in=[4, 5, 6])
        elif value == 3:
            return queryset.filter(asiento__fecha_asiento__month__in=[7, 8, 9])
        elif value == 4:
            return queryset.filter(asiento__fecha_asiento__month__in=[10, 11, 12])
        return queryset
    
    def filtrar_por_elemento(self, queryset, name, value):
        """Filtrar por elemento (primer dígito)"""
        return queryset.filter(cuenta__codigo__startswith=value)
    
    def filtrar_por_rubro(self, queryset, name, value):
        """Filtrar por rubro (dos primeros dígitos)"""
        return queryset.filter(cuenta__codigo__startswith=value)
    
    def filtrar_por_cuenta(self, queryset, name, value):
        """Filtrar por cuenta (tres primeros dígitos)"""
        return queryset.filter(cuenta__codigo__startswith=value)
    
    def filtrar_monto_desde(self, queryset, name, value):
        """Filtrar por monto mínimo"""
        return queryset.filter(
            models.Q(debe__gte=value) | models.Q(haber__gte=value)
        )
    
    def filtrar_monto_hasta(self, queryset, name, value):
        """Filtrar por monto máximo"""
        return queryset.filter(
            models.Q(debe__lte=value) | models.Q(haber__lte=value)
        )

    """Filtro específico para notas de débito"""
    
    # Filtros específicos de notas de débito
    codigo_motivo = django_filters.ChoiceFilter(
        choices=[
            ('01', 'Intereses por mora'),
            ('02', 'Aumento en el valor'),
            ('03', 'Penalidades/otros conceptos'),
            ('10', 'Ajustes de operaciones de exportación'),
            ('11', 'Ajustes afectos al IVAP'),
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
    
    # Filtro por tipo de operación
    por_interes = django_filters.BooleanFilter(
        method='filtrar_por_interes',
        label='Solo intereses por mora'
    )
    
    por_penalidad = django_filters.BooleanFilter(
        method='filtrar_por_penalidad',
        label='Solo penalidades'
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
            'descripcion_motivo', 'por_interes', 'por_penalidad'
        ]
    
    def filtrar_por_interes(self, queryset, name, value):
        """Filtrar solo notas de débito por intereses"""
        if value:
            return queryset.filter(codigo_motivo='01')
        return queryset
    
    def filtrar_por_penalidad(self, queryset, name, value):
        """Filtrar solo notas de débito por penalidades"""
        if value:
            return queryset.filter(codigo_motivo='03')
        return queryset