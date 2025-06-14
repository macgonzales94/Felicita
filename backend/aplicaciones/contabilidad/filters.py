"""
FILTROS DE CONTABILIDAD - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Filtros personalizados para ViewSets de contabilidad
"""

import django_filters
from django.db import models
from datetime import date, timedelta

from .models import BalanceComprobacion, PeriodoContable, MovimientoContable


class BalanceComprobacionFilter(django_filters.FilterSet):
    """Filtro específico para balances de comprobación"""
    
    # Filtros por período
    periodo_año = django_filters.NumberFilter(field_name='periodo__año')
    periodo_mes = django_filters.NumberFilter(field_name='periodo__mes')
    periodo_nombre = django_filters.CharFilter(field_name='periodo__nombre', lookup_expr='icontains')
    
    # Filtros por fecha
    fecha_generacion_desde = django_filters.DateFilter(field_name='fecha_generacion', lookup_expr='gte')
    fecha_generacion_hasta = django_filters.DateFilter(field_name='fecha_generacion', lookup_expr='lte')
    
    # Filtros por cuenta
    cuenta_codigo = django_filters.CharFilter(field_name='cuenta__codigo', lookup_expr='icontains')
    cuenta_nombre = django_filters.CharFilter(field_name='cuenta__nombre', lookup_expr='icontains')
    cuenta_tipo = django_filters.CharFilter(field_name='cuenta__tipo_cuenta')
    cuenta_naturaleza = django_filters.ChoiceFilter(
        field_name='cuenta__naturaleza',
        choices=[
            ('DEUDORA', 'Deudora'),
            ('ACREEDORA', 'Acreedora')
        ]
    )
    
    # Filtros por saldos
    saldo_inicial_desde = django_filters.NumberFilter(method='filtrar_saldo_inicial_desde')
    saldo_inicial_hasta = django_filters.NumberFilter(method='filtrar_saldo_inicial_hasta')
    saldo_final_desde = django_filters.NumberFilter(method='filtrar_saldo_final_desde')
    saldo_final_hasta = django_filters.NumberFilter(method='filtrar_saldo_final_hasta')
    
    # Filtros por movimientos
    movimientos_desde = django_filters.NumberFilter(method='filtrar_movimientos_desde')
    movimientos_hasta = django_filters.NumberFilter(method='filtrar_movimientos_hasta')
    con_movimientos = django_filters.BooleanFilter(method='filtrar_con_movimientos')
    sin_saldo = django_filters.BooleanFilter(method='filtrar_sin_saldo')
    
    # Filtro por tipo de balance
    es_balance_oficial = django_filters.BooleanFilter(field_name='es_balance_oficial')
    
    # Filtro por usuario que generó
    usuario_generacion = django_filters.CharFilter(
        field_name='usuario_generacion__username',
        lookup_expr='icontains'
    )
    
    class Meta:
        model = BalanceComprobacion
        fields = '__all__'  # Usar '__all__' es más seguro
    
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
    
    def filtrar_con_movimientos(self, queryset, name, value):
        """Filtrar balances que tienen movimientos"""
        if value:
            return queryset.filter(
                models.Q(movimientos_debe__gt=0) | 
                models.Q(movimientos_haber__gt=0)
            )
        else:
            return queryset.filter(
                movimientos_debe=0,
                movimientos_haber=0
            )
    
    def filtrar_sin_saldo(self, queryset, name, value):
        """Filtrar balances sin saldo final"""
        if value:
            return queryset.filter(
                saldo_final_debe=0,
                saldo_final_haber=0
            )
        else:
            return queryset.exclude(
                saldo_final_debe=0,
                saldo_final_haber=0
            )


class PeriodoContableFilter(django_filters.FilterSet):
    """Filtro específico para períodos contables"""
    
    # Filtros por año y mes
    año_desde = django_filters.NumberFilter(field_name='año', lookup_expr='gte')
    año_hasta = django_filters.NumberFilter(field_name='año', lookup_expr='lte')
    
    # Filtros por nombre
    nombre_buscar = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    
    # Filtros por fecha
    fecha_inicio_desde = django_filters.DateFilter(field_name='fecha_inicio', lookup_expr='gte')
    fecha_inicio_hasta = django_filters.DateFilter(field_name='fecha_inicio', lookup_expr='lte')
    fecha_fin_desde = django_filters.DateFilter(field_name='fecha_fin', lookup_expr='gte')
    fecha_fin_hasta = django_filters.DateFilter(field_name='fecha_fin', lookup_expr='lte')
    
    # Filtros por fechas de cierre
    fecha_cierre_desde = django_filters.DateFilter(field_name='fecha_cierre', lookup_expr='gte')
    fecha_cierre_hasta = django_filters.DateFilter(field_name='fecha_cierre', lookup_expr='lte')
    
    # Filtro por usuario de cierre
    cerrado_por = django_filters.CharFilter(
        field_name='usuario_cierre__username',
        lookup_expr='icontains'
    )
    
    # Filtros por rango de períodos
    periodo_actual = django_filters.BooleanFilter(method='filtrar_periodo_actual')
    periodos_abiertos = django_filters.BooleanFilter(method='filtrar_periodos_abiertos')
    periodos_vencidos = django_filters.BooleanFilter(method='filtrar_periodos_vencidos')
    
    class Meta:
        model = PeriodoContable
        fields = '__all__'  # Usar '__all__' es más seguro
    
    def filtrar_periodo_actual(self, queryset, name, value):
        """Filtrar el período actual según la fecha"""
        if value:
            hoy = date.today()
            return queryset.filter(
                fecha_inicio__lte=hoy,
                fecha_fin__gte=hoy
            )
        return queryset
    
    def filtrar_periodos_abiertos(self, queryset, name, value):
        """Filtrar períodos que están abiertos"""
        if value:
            return queryset.filter(estado='ABIERTO')
        else:
            return queryset.exclude(estado='ABIERTO')
    
    def filtrar_periodos_vencidos(self, queryset, name, value):
        """Filtrar períodos que ya han vencido pero siguen abiertos"""
        if value:
            hoy = date.today()
            return queryset.filter(
                estado='ABIERTO',
                fecha_fin__lt=hoy
            )
        return queryset


class MovimientoContableFilter(django_filters.FilterSet):
    """Filtro para movimientos contables"""
    
    # Filtros básicos
    fecha_desde = django_filters.DateFilter(field_name='fecha_movimiento', lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name='fecha_movimiento', lookup_expr='lte')
    
    class Meta:
        model = MovimientoContable
        fields = '__all__'