# =============================================================================
# SERIALIZERS DE CONTABILIDAD FALTANTES
# =============================================================================
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import re
import logging

from aplicaciones.contabilidad.models import BalanceComprobacion, PeriodoContable


class BalanceComprobacionSerializer(serializers.ModelSerializer):
    """Serializer para balance de comprobación"""
    
    cuenta_data = serializers.SerializerMethodField()
    periodo_data = serializers.SerializerMethodField()
    usuario_data = serializers.SerializerMethodField()
    
    class Meta:
        model = BalanceComprobacion
        fields = [
            'id', 'empresa', 'periodo', 'periodo_data', 'cuenta', 'cuenta_data',
            'fecha_desde', 'fecha_hasta', 'saldo_inicial_debe', 'saldo_inicial_haber',
            'movimientos_debe', 'movimientos_haber', 'saldo_final_debe', 'saldo_final_haber',
            'fecha_generacion', 'usuario_generacion', 'usuario_data', 'es_balance_oficial',
            'observaciones', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'saldo_final_debe', 'saldo_final_haber', 'fecha_generacion',
            'created_at', 'updated_at'
        ]
    
    def get_cuenta_data(self, obj):
        """Obtener datos de la cuenta"""
        return {
            'id': obj.cuenta.id,
            'codigo': obj.cuenta.codigo,
            'nombre': obj.cuenta.nombre,
            'naturaleza': obj.cuenta.naturaleza,
            'tipo_cuenta': obj.cuenta.tipo_cuenta
        }
    
    def get_periodo_data(self, obj):
        """Obtener datos del período"""
        return {
            'id': obj.periodo.id,
            'nombre': obj.periodo.nombre,
            'año': obj.periodo.año,
            'mes': obj.periodo.mes
        }
    
    def get_usuario_data(self, obj):
        """Obtener datos del usuario"""
        return {
            'id': obj.usuario_generacion.id,
            'username': obj.usuario_generacion.username,
            'nombre_completo': obj.usuario_generacion.get_full_name()
        }


class PeriodoContableSerializer(serializers.ModelSerializer):
    """Serializer para períodos contables"""
    
    usuario_cierre_data = serializers.SerializerMethodField()
    
    class Meta:
        model = PeriodoContable
        fields = [
            'id', 'empresa', 'año', 'mes', 'nombre', 'fecha_inicio', 'fecha_fin',
            'estado', 'es_periodo_principal', 'fecha_cierre', 'usuario_cierre',
            'usuario_cierre_data', 'observaciones_cierre', 'permite_reapertura',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['fecha_cierre', 'usuario_cierre', 'created_at', 'updated_at']
    
    def get_usuario_cierre_data(self, obj):
        """Obtener datos del usuario que cerró"""
        if obj.usuario_cierre:
            return {
                'id': obj.usuario_cierre.id,
                'username': obj.usuario_cierre.username,
                'nombre_completo': obj.usuario_cierre.get_full_name()
            }
        return None
    
    def validate_fecha_fin(self, value):
        """Validar que fecha fin sea posterior a fecha inicio"""
        fecha_inicio = self.initial_data.get('fecha_inicio')
        if fecha_inicio and value <= fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
        return value
    
    def validate(self, data):
        """Validaciones adicionales del período"""
        # Validar que no se solapen períodos
        empresa = data.get('empresa')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if empresa and fecha_inicio and fecha_fin:
            periodos_existentes = PeriodoContable.objects.filter(
                empresa=empresa,
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio
            )
            
            # Excluir el período actual si estamos actualizando
            if self.instance:
                periodos_existentes = periodos_existentes.exclude(id=self.instance.id)
            
            if periodos_existentes.exists():
                raise serializers.ValidationError("Ya existe un período que se solapa con las fechas especificadas")
        
        return data   
    
