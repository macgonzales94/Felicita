"""
SERIALIZERS DE FACTURACIÓN - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Serializers para validación y transformación de datos de facturación
con validaciones específicas SUNAT
"""

from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import re
import logging

from .models import (
    Factura, Boleta, NotaCredito, NotaDebito, GuiaRemision,
    ItemFactura, ItemBoleta, ItemNotaCredito, SerieComprobante
)
from aplicaciones.core.models import Cliente
from aplicaciones.inventario.models import Producto
from aplicaciones.core.utils import validar_ruc, validar_dni
from aplicaciones.integraciones.services.nubefact import nubefact_service

logger = logging.getLogger('felicita.facturacion')


# =============================================================================
# SERIALIZERS BASE
# =============================================================================
class ItemComprobanteBaseSerializer(serializers.Serializer):
    """Serializer base para items de comprobantes"""
    
    producto_id = serializers.IntegerField()
    descripcion = serializers.CharField(max_length=500)
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=4)
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=4)
    descuento = serializers.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    # Campos calculados automáticamente
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    igv = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    def validate_cantidad(self, value):
        """Validar cantidad positiva"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero")
        return value
    
    def validate_precio_unitario(self, value):
        """Validar precio unitario positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio unitario debe ser mayor a cero")
        return value
    
    def validate_producto_id(self, value):
        """Validar que el producto existe"""
        try:
            producto = Producto.objects.get(id=value)
            if not producto.activo:
                raise serializers.ValidationError("El producto no está activo")
            return value
        except Producto.DoesNotExist:
            raise serializers.ValidationError("El producto no existe")


class ComprobanteBaseSerializer(serializers.ModelSerializer):
    """Serializer base para comprobantes"""
    
    # Campos relacionales
    cliente_data = serializers.SerializerMethodField()
    items = ItemComprobanteBaseSerializer(many=True, write_only=True)
    items_detalle = serializers.SerializerMethodField()
    
    # Campos calculados
    numero_completo = serializers.SerializerMethodField()
    estado_sunat_display = serializers.SerializerMethodField()
    
    class Meta:
        fields = [
            'id', 'serie', 'numero', 'numero_completo', 'fecha_emision', 'fecha_vencimiento',
            'cliente', 'cliente_data', 'moneda', 'tipo_cambio',
            'subtotal', 'descuento_global', 'igv', 'total',
            'estado_sunat', 'estado_sunat_display', 'observaciones',
            'items', 'items_detalle', 'created_at', 'updated_at'
        ]
        read_only_fields = ['numero', 'subtotal', 'igv', 'total', 'created_at', 'updated_at']
    
    def get_cliente_data(self, obj):
        """Obtener datos completos del cliente"""
        if obj.cliente:
            return {
                'id': obj.cliente.id,
                'tipo_documento': obj.cliente.tipo_documento,
                'numero_documento': obj.cliente.numero_documento,
                'razon_social': obj.cliente.razon_social,
                'direccion': obj.cliente.direccion,
                'email': obj.cliente.email,
                'telefono': obj.cliente.telefono
            }
        return None
    
    def get_numero_completo(self, obj):
        """Obtener número completo del comprobante"""
        return f"{obj.serie}-{obj.numero:08d}"
    
    def get_estado_sunat_display(self, obj):
        """Obtener estado SUNAT legible"""
        estados = {
            'PENDIENTE': 'Pendiente',
            'ACEPTADO': 'Aceptado',
            'RECHAZADO': 'Rechazado',
            'ANULADO': 'Anulado'
        }
        return estados.get(obj.estado_sunat, obj.estado_sunat)
    
    def get_items_detalle(self, obj):
        """Obtener items del comprobante"""
        items = []
        for item in obj.get_items():
            items.append({
                'id': item.id,
                'producto': {
                    'id': item.producto.id,
                    'codigo': item.producto.codigo_producto,
                    'descripcion': item.producto.descripcion
                },
                'descripcion': item.descripcion,
                'cantidad': item.cantidad,
                'precio_unitario': item.precio_unitario,
                'descuento': item.descuento,
                'subtotal': item.subtotal,
                'igv': item.igv,
                'total': item.total
            })
        return items
    
    def validate_cliente(self, value):
        """Validar cliente activo"""
        if not value.activo:
            raise serializers.ValidationError("El cliente no está activo")
        return value
    
    def validate_fecha_emision(self, value):
        """Validar fecha de emisión"""
        from datetime import date
        
        hoy = date.today()
        if value > hoy:
            raise serializers.ValidationError("La fecha de emisión no puede ser futura")
        
        # No permitir fechas muy antiguas (más de 30 días)
        diferencia = (hoy - value).days
        if diferencia > 30:
            raise serializers.ValidationError("La fecha de emisión no puede ser mayor a 30 días")
        
        return value
    
    def validate_moneda(self, value):
        """Validar moneda permitida"""
        monedas_permitidas = ['PEN', 'USD', 'EUR']
        if value not in monedas_permitidas:
            raise serializers.ValidationError(f"Moneda no permitida. Use: {', '.join(monedas_permitidas)}")
        return value
    
    def validate_items(self, value):
        """Validar items del comprobante"""
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un item")
        
        if len(value) > 200:  # Límite SUNAT
            raise serializers.ValidationError("Máximo 200 items por comprobante")
        
        return value
    
    def validate(self, data):
        """Validaciones generales del comprobante"""
        # Validar que el cliente sea apropiado para el tipo de comprobante
        cliente = data.get('cliente')
        tipo_comprobante = self.Meta.model._meta.verbose_name.lower()
        
        if tipo_comprobante == 'factura' and cliente.tipo_documento != 'RUC':
            raise serializers.ValidationError("Las facturas requieren cliente con RUC")
        
        # Validar items y calcular totales
        items = data.get('items', [])
        if items:
            self._validar_y_calcular_totales(data, items)
        
        return data
    
    def _validar_y_calcular_totales(self, data, items):
        """Validar y calcular totales del comprobante"""
        subtotal_calculado = Decimal('0.00')
        igv_calculado = Decimal('0.00')
        
        for item in items:
            cantidad = Decimal(str(item['cantidad']))
            precio_unitario = Decimal(str(item['precio_unitario']))
            descuento = Decimal(str(item.get('descuento', 0)))
            
            # Calcular subtotal del item
            subtotal_item = cantidad * precio_unitario - descuento
            igv_item = subtotal_item * Decimal(str(settings.SUNAT_CONFIG['igv_tasa']))
            
            subtotal_calculado += subtotal_item
            igv_calculado += igv_item
        
        # Aplicar descuento global
        descuento_global = Decimal(str(data.get('descuento_global', 0)))
        subtotal_calculado -= descuento_global
        
        # Recalcular IGV después del descuento global
        igv_calculado = subtotal_calculado * Decimal(str(settings.SUNAT_CONFIG['igv_tasa']))
        total_calculado = subtotal_calculado + igv_calculado
        
        # Actualizar datos calculados
        data['subtotal'] = subtotal_calculado.quantize(Decimal('0.01'))
        data['igv'] = igv_calculado.quantize(Decimal('0.01'))
        data['total'] = total_calculado.quantize(Decimal('0.01'))
        
        logger.debug(f"Totales calculados - Subtotal: {data['subtotal']}, IGV: {data['igv']}, Total: {data['total']}")


# =============================================================================
# SERIALIZERS ESPECÍFICOS DE ITEMS
# =============================================================================
class ItemFacturaSerializer(ItemComprobanteBaseSerializer):
    """Serializer para items de facturas"""
    
    class Meta:
        model = ItemFactura
        fields = '__all__'


class ItemBoletaSerializer(ItemComprobanteBaseSerializer):
    """Serializer para items de boletas"""
    
    class Meta:
        model = ItemBoleta
        fields = '__all__'


class ItemNotaCreditoSerializer(ItemComprobanteBaseSerializer):
    """Serializer para items de notas de crédito"""
    
    class Meta:
        model = ItemNotaCredito
        fields = '__all__'


# =============================================================================
# SERIALIZERS PRINCIPALES
# =============================================================================
class FacturaSerializer(ComprobanteBaseSerializer):
    """Serializer para facturas"""
    
    condicion_pago = serializers.CharField(max_length=50, default='CONTADO')
    medio_pago = serializers.CharField(max_length=50, default='EFECTIVO')
    
    class Meta(ComprobanteBaseSerializer.Meta):
        model = Factura
        fields = ComprobanteBaseSerializer.Meta.fields + ['condicion_pago', 'medio_pago']
    
    def validate_condicion_pago(self, value):
        """Validar condición de pago"""
        condiciones_validas = ['CONTADO', 'CREDITO_30', 'CREDITO_60', 'CREDITO_90']
        if value not in condiciones_validas:
            raise serializers.ValidationError(f"Condición de pago inválida. Use: {', '.join(condiciones_validas)}")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear factura con items y envío automático a Nubefact"""
        items_data = validated_data.pop('items')
        
        logger.info(f"Creando factura para cliente {validated_data['cliente']}")
        
        # Obtener siguiente número de serie
        serie_obj = self._obtener_siguiente_numero(validated_data['serie'])
        validated_data['numero'] = serie_obj.siguiente_numero
        
        # Crear factura
        factura = Factura.objects.create(**validated_data)
        
        # Crear items
        for item_data in items_data:
            self._crear_item_factura(factura, item_data)
        
        # Actualizar numeración
        serie_obj.siguiente_numero += 1
        serie_obj.save()
        
        # Enviar automáticamente a Nubefact
        if getattr(settings, 'NUBEFACT_AUTO_SEND', True):
            self._enviar_a_nubefact(factura)
        
        logger.info(f"Factura {factura.numero_completo} creada exitosamente")
        
        return factura
    
    def _obtener_siguiente_numero(self, serie):
        """Obtener el siguiente número de la serie"""
        serie_obj, created = SerieComprobante.objects.get_or_create(
            serie=serie,
            tipo_comprobante='01',  # Factura
            defaults={'siguiente_numero': 1}
        )
        return serie_obj
    
    def _crear_item_factura(self, factura, item_data):
        """Crear item de factura con cálculos automáticos"""
        producto = Producto.objects.get(id=item_data['producto_id'])
        
        cantidad = Decimal(str(item_data['cantidad']))
        precio_unitario = Decimal(str(item_data['precio_unitario']))
        descuento = Decimal(str(item_data.get('descuento', 0)))
        
        # Calcular valores
        subtotal = cantidad * precio_unitario - descuento
        igv = subtotal * Decimal(str(settings.SUNAT_CONFIG['igv_tasa']))
        total = subtotal + igv
        
        ItemFactura.objects.create(
            factura=factura,
            producto=producto,
            descripcion=item_data['descripcion'],
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            descuento=descuento,
            subtotal=subtotal.quantize(Decimal('0.01')),
            igv=igv.quantize(Decimal('0.01')),
            total=total.quantize(Decimal('0.01'))
        )
    
    def _enviar_a_nubefact(self, factura):
        """Enviar factura a Nubefact automáticamente"""
        try:
            # Preparar datos para Nubefact
            factura_data = self._preparar_datos_nubefact(factura)
            
            # Enviar a Nubefact
            response = nubefact_service.emitir_factura(factura_data)
            
            if response.get('success'):
                # Actualizar factura con respuesta de Nubefact
                factura.nubefact_id = response.get('invoice_id')
                factura.estado_sunat = response.get('estado_sunat', 'PENDIENTE')
                factura.hash_cpe = response.get('hash_documento')
                factura.save()
                
                logger.info(f"Factura {factura.numero_completo} enviada a Nubefact exitosamente")
            else:
                logger.error(f"Error al enviar factura {factura.numero_completo} a Nubefact")
                
        except Exception as e:
            logger.error(f"Error crítico al enviar factura a Nubefact: {e}")
            # No interrumpir la creación de la factura
    
    def _preparar_datos_nubefact(self, factura):
        """Preparar datos de factura para Nubefact"""
        items = []
        for item in factura.items.all():
            items.append({
                'producto': {'codigo': item.producto.codigo_producto},
                'descripcion': item.descripcion,
                'cantidad': float(item.cantidad),
                'precio_unitario': float(item.precio_unitario),
                'descuento': float(item.descuento),
                'subtotal': float(item.subtotal),
                'igv': float(item.igv),
                'total': float(item.total),
                'unidad_medida': 'NIU',
                'tipo_afectacion_igv': 1
            })
        
        return {
            'serie': factura.serie,
            'numero': factura.numero,
            'fecha_emision': factura.fecha_emision.strftime('%Y-%m-%d'),
            'fecha_vencimiento': factura.fecha_vencimiento.strftime('%Y-%m-%d') if factura.fecha_vencimiento else None,
            'cliente': {
                'tipo_documento': factura.cliente.tipo_documento,
                'numero_documento': factura.cliente.numero_documento,
                'razon_social': factura.cliente.razon_social,
                'direccion': factura.cliente.direccion,
                'email': factura.cliente.email or ''
            },
            'moneda': factura.moneda,
            'tipo_cambio': float(factura.tipo_cambio),
            'subtotal': float(factura.subtotal),
            'descuento_global': float(factura.descuento_global),
            'igv': float(factura.igv),
            'total': float(factura.total),
            'condicion_pago': factura.condicion_pago,
            'medio_pago': factura.medio_pago,
            'items': items
        }


class BoletaSerializer(ComprobanteBaseSerializer):
    """Serializer para boletas de venta"""
    
    class Meta(ComprobanteBaseSerializer.Meta):
        model = Boleta
    
    def validate_cliente(self, value):
        """Validar cliente para boleta"""
        # Las boletas pueden ser para clientes con DNI o consumidor final
        if value.tipo_documento not in ['DNI', 'CE', 'PASSPORT']:
            raise serializers.ValidationError("Las boletas requieren cliente con DNI, CE o Pasaporte")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear boleta con lógica similar a factura"""
        items_data = validated_data.pop('items')
        
        logger.info(f"Creando boleta para cliente {validated_data['cliente']}")
        
        # Obtener siguiente número de serie
        serie_obj = self._obtener_siguiente_numero(validated_data['serie'])
        validated_data['numero'] = serie_obj.siguiente_numero
        
        # Crear boleta
        boleta = Boleta.objects.create(**validated_data)
        
        # Crear items
        for item_data in items_data:
            self._crear_item_boleta(boleta, item_data)
        
        # Actualizar numeración
        serie_obj.siguiente_numero += 1
        serie_obj.save()
        
        # Enviar automáticamente a Nubefact
        if getattr(settings, 'NUBEFACT_AUTO_SEND', True):
            self._enviar_a_nubefact(boleta)
        
        logger.info(f"Boleta {boleta.numero_completo} creada exitosamente")
        
        return boleta
    
    def _obtener_siguiente_numero(self, serie):
        """Obtener el siguiente número de la serie para boletas"""
        serie_obj, created = SerieComprobante.objects.get_or_create(
            serie=serie,
            tipo_comprobante='03',  # Boleta
            defaults={'siguiente_numero': 1}
        )
        return serie_obj
    
    def _crear_item_boleta(self, boleta, item_data):
        """Crear item de boleta"""
        producto = Producto.objects.get(id=item_data['producto_id'])
        
        cantidad = Decimal(str(item_data['cantidad']))
        precio_unitario = Decimal(str(item_data['precio_unitario']))
        descuento = Decimal(str(item_data.get('descuento', 0)))
        
        # Calcular valores
        subtotal = cantidad * precio_unitario - descuento
        igv = subtotal * Decimal(str(settings.SUNAT_CONFIG['igv_tasa']))
        total = subtotal + igv
        
        ItemBoleta.objects.create(
            boleta=boleta,
            producto=producto,
            descripcion=item_data['descripcion'],
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            descuento=descuento,
            subtotal=subtotal.quantize(Decimal('0.01')),
            igv=igv.quantize(Decimal('0.01')),
            total=total.quantize(Decimal('0.01'))
        )
    
    def _enviar_a_nubefact(self, boleta):
        """Enviar boleta a Nubefact"""
        try:
            # Preparar datos similares a factura pero para boleta
            boleta_data = self._preparar_datos_nubefact_boleta(boleta)
            
            # Enviar a Nubefact
            response = nubefact_service.emitir_boleta(boleta_data)
            
            if response.get('success'):
                boleta.nubefact_id = response.get('invoice_id')
                boleta.estado_sunat = response.get('estado_sunat', 'PENDIENTE')
                boleta.hash_cpe = response.get('hash_documento')
                boleta.save()
                
                logger.info(f"Boleta {boleta.numero_completo} enviada a Nubefact exitosamente")
                
        except Exception as e:
            logger.error(f"Error al enviar boleta a Nubefact: {e}")
    
    def _preparar_datos_nubefact_boleta(self, boleta):
        """Preparar datos de boleta para Nubefact"""
        # Similar a factura pero con tipo de comprobante 03
        datos = self._preparar_datos_base_nubefact(boleta)
        return datos


class NotaCreditoSerializer(ComprobanteBaseSerializer):
    """Serializer para notas de crédito"""
    
    # Campos específicos de nota de crédito
    codigo_motivo = serializers.CharField(max_length=2)
    descripcion_motivo = serializers.CharField(max_length=250)
    documento_modificado_tipo = serializers.CharField(max_length=2)
    documento_modificado_serie = serializers.CharField(max_length=4)
    documento_modificado_numero = serializers.IntegerField()
    
    class Meta(ComprobanteBaseSerializer.Meta):
        model = NotaCredito
        fields = ComprobanteBaseSerializer.Meta.fields + [
            'codigo_motivo', 'descripcion_motivo', 'documento_modificado_tipo',
            'documento_modificado_serie', 'documento_modificado_numero'
        ]
    
    def validate_codigo_motivo(self, value):
        """Validar código de motivo según SUNAT"""
        motivos_validos = [
            '01',  # Anulación de la operación
            '02',  # Anulación por error en el RUC
            '03',  # Corrección por error en la descripción
            '04',  # Descuento global
            '05',  # Descuento por ítem
            '06',  # Devolución total
            '07',  # Devolución por ítem
            '08',  # Bonificación
            '09',  # Disminución en el valor
            '10'   # Otros conceptos
        ]
        if value not in motivos_validos:
            raise serializers.ValidationError(f"Código de motivo inválido. Use: {', '.join(motivos_validos)}")
        return value
    
    def validate_documento_modificado_tipo(self, value):
        """Validar tipo de documento que se modifica"""
        tipos_validos = ['01', '03', '07', '08']  # Factura, Boleta, Nota Crédito, Nota Débito
        if value not in tipos_validos:
            raise serializers.ValidationError("Tipo de documento modificado inválido")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear nota de crédito"""
        items_data = validated_data.pop('items')
        
        logger.info(f"Creando nota de crédito para cliente {validated_data['cliente']}")
        
        # Obtener siguiente número de serie
        serie_obj = self._obtener_siguiente_numero(validated_data['serie'])
        validated_data['numero'] = serie_obj.siguiente_numero
        
        # Crear nota de crédito
        nota_credito = NotaCredito.objects.create(**validated_data)
        
        # Crear items
        for item_data in items_data:
            self._crear_item_nota_credito(nota_credito, item_data)
        
        # Actualizar numeración
        serie_obj.siguiente_numero += 1
        serie_obj.save()
        
        # Enviar automáticamente a Nubefact
        if getattr(settings, 'NUBEFACT_AUTO_SEND', True):
            self._enviar_a_nubefact(nota_credito)
        
        logger.info(f"Nota de crédito {nota_credito.numero_completo} creada exitosamente")
        
        return nota_credito
    
    def _obtener_siguiente_numero(self, serie):
        """Obtener el siguiente número de la serie para notas de crédito"""
        serie_obj, created = SerieComprobante.objects.get_or_create(
            serie=serie,
            tipo_comprobante='07',  # Nota de crédito
            defaults={'siguiente_numero': 1}
        )
        return serie_obj
    
    def _crear_item_nota_credito(self, nota_credito, item_data):
        """Crear item de nota de crédito"""
        producto = Producto.objects.get(id=item_data['producto_id'])
        
        cantidad = Decimal(str(item_data['cantidad']))
        precio_unitario = Decimal(str(item_data['precio_unitario']))
        descuento = Decimal(str(item_data.get('descuento', 0)))
        
        # Calcular valores
        subtotal = cantidad * precio_unitario - descuento
        igv = subtotal * Decimal(str(settings.SUNAT_CONFIG['igv_tasa']))
        total = subtotal + igv
        
        ItemNotaCredito.objects.create(
            nota_credito=nota_credito,
            producto=producto,
            descripcion=item_data['descripcion'],
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            descuento=descuento,
            subtotal=subtotal.quantize(Decimal('0.01')),
            igv=igv.quantize(Decimal('0.01')),
            total=total.quantize(Decimal('0.01'))
        )
    
    def _enviar_a_nubefact(self, nota_credito):
        """Enviar nota de crédito a Nubefact"""
        try:
            # Preparar datos para Nubefact
            nota_data = self._preparar_datos_nubefact_nota_credito(nota_credito)
            
            # Enviar a Nubefact
            response = nubefact_service.emitir_nota_credito(nota_data)
            
            if response.get('success'):
                nota_credito.nubefact_id = response.get('invoice_id')
                nota_credito.estado_sunat = response.get('estado_sunat', 'PENDIENTE')
                nota_credito.hash_cpe = response.get('hash_documento')
                nota_credito.save()
                
                logger.info(f"Nota de crédito {nota_credito.numero_completo} enviada a Nubefact exitosamente")
                
        except Exception as e:
            logger.error(f"Error al enviar nota de crédito a Nubefact: {e}")
    
    def _preparar_datos_nubefact_nota_credito(self, nota_credito):
        """Preparar datos de nota de crédito para Nubefact"""
        datos_base = self._preparar_datos_base_nubefact(nota_credito)
        
        # Agregar campos específicos de nota de crédito
        datos_base.update({
            'codigo_motivo': nota_credito.codigo_motivo,
            'descripcion_motivo': nota_credito.descripcion_motivo,
            'tipo_documento_modificado': nota_credito.documento_modificado_tipo,
            'serie_documento_modificado': nota_credito.documento_modificado_serie,
            'numero_documento_modificado': nota_credito.documento_modificado_numero
        })
        
        return datos_base


# =============================================================================
# SERIALIZERS AUXILIARES
# =============================================================================
class SerieComprobanteSerializer(serializers.ModelSerializer):
    """Serializer para series de comprobantes"""
    
    class Meta:
        model = SerieComprobante
        fields = '__all__'
        read_only_fields = ['siguiente_numero']


class ConsultaEstadoSerializer(serializers.Serializer):
    """Serializer para consultar estado en SUNAT"""
    
    comprobante_id = serializers.IntegerField()
    
    def validate_comprobante_id(self, value):
        """Validar que el comprobante existe"""
        # Esta validación se puede personalizar según el tipo de comprobante
        return value


class AnularComprobanteSerializer(serializers.Serializer):
    """Serializer para anular comprobantes"""
    
    comprobante_id = serializers.IntegerField()
    motivo = serializers.CharField(max_length=250)
    codigo_motivo = serializers.CharField(max_length=2, default='01')
    
    def validate_codigo_motivo(self, value):
        """Validar código de motivo de anulación"""
        codigos_validos = ['01', '02', '03']
        if value not in codigos_validos:
            raise serializers.ValidationError("Código de motivo inválido para anulación")
        return value