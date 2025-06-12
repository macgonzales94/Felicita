"""
VIEWS DE FACTURACIÓN - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

ViewSets para manejo completo de facturación electrónica con integración Nubefact
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Factura, Boleta, NotaCredito, NotaDebito, GuiaRemision,
    SerieComprobante, ItemFactura, ItemBoleta
)
from .serializers import (
    FacturaSerializer, BoletaSerializer, NotaCreditoSerializer,
    SerieComprobanteSerializer, ConsultaEstadoSerializer,
    AnularComprobanteSerializer
)
from .filters import FacturaFilter, BoletaFilter, NotaCreditoFilter
from aplicaciones.core.permissions import TienePermisoModulo
from aplicaciones.integraciones.services.nubefact import nubefact_service
from aplicaciones.inventario.services import actualizar_inventario_venta
from aplicaciones.contabilidad.services import generar_asiento_venta

logger = logging.getLogger('felicita.facturacion')


# =============================================================================
# MIXINS COMUNES
# =============================================================================
class ComprobanteViewSetMixin:
    """Mixin con funcionalidad común para comprobantes"""
    
    permission_classes = [IsAuthenticated, TienePermisoModulo]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['numero', 'cliente__razon_social', 'cliente__numero_documento']
    ordering_fields = ['fecha_emision', 'numero', 'total']
    ordering = ['-fecha_emision', '-numero']
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, TienePermisoModulo]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Crear comprobante con usuario actual"""
        serializer.save(usuario_creacion=self.request.user)
    
    @action(detail=True, methods=['post'])
    def enviar_sunat(self, request, pk=None):
        """Enviar comprobante a SUNAT vía Nubefact"""
        comprobante = self.get_object()
        
        if comprobante.estado_sunat == 'ACEPTADO':
            return Response(
                {'error': 'El comprobante ya fue aceptado por SUNAT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Preparar datos según tipo de comprobante
            if isinstance(comprobante, Factura):
                resultado = self._enviar_factura_nubefact(comprobante)
            elif isinstance(comprobante, Boleta):
                resultado = self._enviar_boleta_nubefact(comprobante)
            elif isinstance(comprobante, NotaCredito):
                resultado = self._enviar_nota_credito_nubefact(comprobante)
            else:
                return Response(
                    {'error': 'Tipo de comprobante no soportado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if resultado.get('success'):
                # Actualizar estado del comprobante
                comprobante.nubefact_id = resultado.get('invoice_id')
                comprobante.estado_sunat = resultado.get('estado_sunat', 'PENDIENTE')
                comprobante.hash_cpe = resultado.get('hash_documento')
                comprobante.fecha_envio_sunat = timezone.now()
                comprobante.save()
                
                # Actualizar inventario si es venta
                if isinstance(comprobante, (Factura, Boleta)):
                    self._actualizar_inventario_comprobante(comprobante)
                
                # Generar asiento contable
                self._generar_asiento_contable(comprobante)
                
                logger.info(f"Comprobante {comprobante.numero_completo} enviado exitosamente a SUNAT")
                
                return Response({
                    'success': True,
                    'message': 'Comprobante enviado exitosamente a SUNAT',
                    'nubefact_id': resultado.get('invoice_id'),
                    'estado_sunat': resultado.get('estado_sunat')
                })
            else:
                return Response(
                    {'error': 'Error al enviar a SUNAT', 'details': resultado},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error al enviar comprobante {pk} a SUNAT: {e}")
            return Response(
                {'error': f'Error interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def consultar_estado(self, request, pk=None):
        """Consultar estado del comprobante en SUNAT"""
        comprobante = self.get_object()
        
        if not comprobante.nubefact_id:
            return Response(
                {'error': 'El comprobante no ha sido enviado a SUNAT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resultado = nubefact_service.consultar_estado(comprobante.nubefact_id)
            
            # Actualizar estado local si ha cambiado
            if resultado.get('estado_sunat') != comprobante.estado_sunat:
                comprobante.estado_sunat = resultado.get('estado_sunat')
                comprobante.save()
            
            return Response({
                'nubefact_id': comprobante.nubefact_id,
                'estado_sunat': resultado.get('estado_sunat'),
                'codigo_respuesta': resultado.get('codigo_respuesta'),
                'mensaje_sunat': resultado.get('mensaje_sunat'),
                'fecha_consulta': resultado.get('fecha_consulta')
            })
            
        except Exception as e:
            logger.error(f"Error al consultar estado del comprobante {pk}: {e}")
            return Response(
                {'error': f'Error al consultar estado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anular comprobante"""
        comprobante = self.get_object()
        serializer = AnularComprobanteSerializer(data=request.data)
        
        if serializer.is_valid():
            if comprobante.estado_sunat == 'ANULADO':
                return Response(
                    {'error': 'El comprobante ya está anulado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Preparar comunicación de baja para SUNAT
                documentos_baja = [{
                    'tipo_comprobante': comprobante.get_tipo_comprobante_sunat(),
                    'serie': comprobante.serie,
                    'numero': comprobante.numero,
                    'motivo': serializer.validated_data['motivo'],
                    'codigo_motivo': serializer.validated_data['codigo_motivo']
                }]
                
                # Enviar comunicación de baja
                resultado = nubefact_service.comunicacion_baja(documentos_baja)
                
                if resultado.get('success'):
                    # Actualizar estado del comprobante
                    comprobante.estado_sunat = 'ANULADO'
                    comprobante.motivo_anulacion = serializer.validated_data['motivo']
                    comprobante.fecha_anulacion = timezone.now()
                    comprobante.usuario_anulacion = request.user
                    comprobante.ticket_baja = resultado.get('ticket')
                    comprobante.save()
                    
                    # Reversar inventario si es necesario
                    if isinstance(comprobante, (Factura, Boleta)):
                        self._reversar_inventario_comprobante(comprobante)
                    
                    # Reversar asiento contable
                    self._reversar_asiento_contable(comprobante)
                    
                    logger.info(f"Comprobante {comprobante.numero_completo} anulado exitosamente")
                    
                    return Response({
                        'success': True,
                        'message': 'Comprobante anulado exitosamente',
                        'ticket': resultado.get('ticket')
                    })
                else:
                    return Response(
                        {'error': 'Error al anular en SUNAT', 'details': resultado},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except Exception as e:
                logger.error(f"Error al anular comprobante {pk}: {e}")
                return Response(
                    {'error': f'Error interno: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def descargar_xml(self, request, pk=None):
        """Descargar XML del comprobante"""
        comprobante = self.get_object()
        
        if not comprobante.nubefact_id:
            return Response(
                {'error': 'El comprobante no ha sido enviado a SUNAT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            xml_content = nubefact_service.descargar_xml(comprobante.nubefact_id)
            
            if xml_content:
                return Response({
                    'xml_content': xml_content,
                    'filename': f"{comprobante.numero_completo}.xml"
                })
            else:
                return Response(
                    {'error': 'No se pudo obtener el XML'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error al descargar XML del comprobante {pk}: {e}")
            return Response(
                {'error': f'Error al descargar XML: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def descargar_pdf(self, request, pk=None):
        """Descargar PDF del comprobante"""
        comprobante = self.get_object()
        
        if not comprobante.nubefact_id:
            return Response(
                {'error': 'El comprobante no ha sido enviado a SUNAT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pdf_url = nubefact_service.descargar_pdf(comprobante.nubefact_id)
            
            if pdf_url:
                return Response({
                    'pdf_url': pdf_url,
                    'filename': f"{comprobante.numero_completo}.pdf"
                })
            else:
                return Response(
                    {'error': 'No se pudo obtener el PDF'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error al descargar PDF del comprobante {pk}: {e}")
            return Response(
                {'error': f'Error al descargar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # =============================================================================
    # MÉTODOS PRIVADOS
    # =============================================================================
    
    def _enviar_factura_nubefact(self, factura):
        """Enviar factura a Nubefact"""
        factura_data = self._preparar_datos_comprobante(factura)
        return nubefact_service.emitir_factura(factura_data)
    
    def _enviar_boleta_nubefact(self, boleta):
        """Enviar boleta a Nubefact"""
        boleta_data = self._preparar_datos_comprobante(boleta)
        return nubefact_service.emitir_boleta(boleta_data)
    
    def _enviar_nota_credito_nubefact(self, nota_credito):
        """Enviar nota de crédito a Nubefact"""
        nota_data = self._preparar_datos_comprobante(nota_credito)
        # Agregar campos específicos de nota de crédito
        nota_data.update({
            'codigo_motivo': nota_credito.codigo_motivo,
            'descripcion_motivo': nota_credito.descripcion_motivo,
            'tipo_documento_modificado': nota_credito.documento_modificado_tipo,
            'serie_documento_modificado': nota_credito.documento_modificado_serie,
            'numero_documento_modificado': nota_credito.documento_modificado_numero
        })
        return nubefact_service.emitir_nota_credito(nota_data)
    
    def _preparar_datos_comprobante(self, comprobante):
        """Preparar datos base del comprobante para Nubefact"""
        items = []
        for item in comprobante.get_items():
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
            'serie': comprobante.serie,
            'numero': comprobante.numero,
            'fecha_emision': comprobante.fecha_emision.strftime('%Y-%m-%d'),
            'fecha_vencimiento': comprobante.fecha_vencimiento.strftime('%Y-%m-%d') if comprobante.fecha_vencimiento else None,
            'cliente': {
                'tipo_documento': comprobante.cliente.tipo_documento,
                'numero_documento': comprobante.cliente.numero_documento,
                'razon_social': comprobante.cliente.razon_social,
                'direccion': comprobante.cliente.direccion,
                'email': comprobante.cliente.email or ''
            },
            'moneda': comprobante.moneda,
            'tipo_cambio': float(comprobante.tipo_cambio),
            'subtotal': float(comprobante.subtotal),
            'descuento_global': float(comprobante.descuento_global),
            'igv': float(comprobante.igv),
            'total': float(comprobante.total),
            'items': items
        }
    
    def _actualizar_inventario_comprobante(self, comprobante):
        """Actualizar inventario por venta"""
        try:
            for item in comprobante.get_items():
                actualizar_inventario_venta(
                    producto_id=item.producto.id,
                    cantidad_vendida=item.cantidad,
                    comprobante_referencia=comprobante.numero_completo
                )
            logger.info(f"Inventario actualizado para comprobante {comprobante.numero_completo}")
        except Exception as e:
            logger.error(f"Error al actualizar inventario: {e}")
    
    def _reversar_inventario_comprobante(self, comprobante):
        """Reversar inventario por anulación"""
        try:
            for item in comprobante.get_items():
                # Reversar movimiento de inventario
                actualizar_inventario_venta(
                    producto_id=item.producto.id,
                    cantidad_vendida=-item.cantidad,  # Cantidad negativa para reversión
                    comprobante_referencia=f"ANULACION-{comprobante.numero_completo}"
                )
            logger.info(f"Inventario reversado para comprobante {comprobante.numero_completo}")
        except Exception as e:
            logger.error(f"Error al reversar inventario: {e}")
    
    def _generar_asiento_contable(self, comprobante):
        """Generar asiento contable automático"""
        try:
            if isinstance(comprobante, (Factura, Boleta)):
                generar_asiento_venta(comprobante)
            elif isinstance(comprobante, NotaCredito):
                generar_asiento_venta(comprobante, es_nota_credito=True)
            logger.info(f"Asiento contable generado para comprobante {comprobante.numero_completo}")
        except Exception as e:
            logger.error(f"Error al generar asiento contable: {e}")
    
    def _reversar_asiento_contable(self, comprobante):
        """Reversar asiento contable por anulación"""
        try:
            # Lógica para reversar asiento contable
            # Se implementará en el service de contabilidad
            pass
        except Exception as e:
            logger.error(f"Error al reversar asiento contable: {e}")


# =============================================================================
# VIEWSETS PRINCIPALES
# =============================================================================
class FacturaViewSet(ComprobanteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet para facturas"""
    
    queryset = Factura.objects.select_related('cliente').prefetch_related('items__producto')
    serializer_class = FacturaSerializer
    filterset_class = FacturaFilter
    
    def get_queryset(self):
        """Filtrar facturas por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    @action(detail=False, methods=['get'])
    def resumen_diario(self, request):
        """Resumen de facturas del día"""
        from django.db.models import Sum, Count
        from datetime import date
        
        hoy = date.today()
        facturas_hoy = self.get_queryset().filter(fecha_emision=hoy)
        
        resumen = facturas_hoy.aggregate(
            total_facturas=Count('id'),
            total_monto=Sum('total'),
            total_aceptadas=Count('id', filter=models.Q(estado_sunat='ACEPTADO')),
            total_pendientes=Count('id', filter=models.Q(estado_sunat='PENDIENTE'))
        )
        
        return Response({
            'fecha': hoy,
            'resumen': resumen,
            'facturas_recientes': FacturaSerializer(
                facturas_hoy.order_by('-created_at')[:5], many=True
            ).data
        })
    
    @action(detail=False, methods=['get'])
    def por_cliente(self, request):
        """Facturas agrupadas por cliente"""
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response(
                {'error': 'Se requiere cliente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        facturas = self.get_queryset().filter(cliente_id=cliente_id).order_by('-fecha_emision')
        page = self.paginate_queryset(facturas)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(facturas, many=True)
        return Response(serializer.data)


class BoletaViewSet(ComprobanteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet para boletas de venta"""
    
    queryset = Boleta.objects.select_related('cliente').prefetch_related('items__producto')
    serializer_class = BoletaSerializer
    filterset_class = BoletaFilter
    
    def get_queryset(self):
        """Filtrar boletas por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    @action(detail=False, methods=['get'])
    def resumen_diario(self, request):
        """Resumen de boletas del día"""
        from django.db.models import Sum, Count
        from datetime import date
        
        hoy = date.today()
        boletas_hoy = self.get_queryset().filter(fecha_emision=hoy)
        
        resumen = boletas_hoy.aggregate(
            total_boletas=Count('id'),
            total_monto=Sum('total'),
            total_aceptadas=Count('id', filter=models.Q(estado_sunat='ACEPTADO')),
            total_pendientes=Count('id', filter=models.Q(estado_sunat='PENDIENTE'))
        )
        
        return Response({
            'fecha': hoy,
            'resumen': resumen,
            'boletas_recientes': BoletaSerializer(
                boletas_hoy.order_by('-created_at')[:5], many=True
            ).data
        })


class NotaCreditoViewSet(ComprobanteViewSetMixin, viewsets.ModelViewSet):
    """ViewSet para notas de crédito"""
    
    queryset = NotaCredito.objects.select_related('cliente').prefetch_related('items__producto')
    serializer_class = NotaCreditoSerializer
    filterset_class = NotaCreditoFilter
    
    def get_queryset(self):
        """Filtrar notas de crédito por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    @action(detail=False, methods=['post'])
    def desde_factura(self, request):
        """Crear nota de crédito desde una factura"""
        factura_id = request.data.get('factura_id')
        if not factura_id:
            return Response(
                {'error': 'Se requiere factura_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            factura = Factura.objects.get(id=factura_id)
            
            # Preparar datos de la nota de crédito basada en la factura
            nota_data = {
                'cliente': factura.cliente.id,
                'serie': request.data.get('serie', 'FC01'),
                'moneda': factura.moneda,
                'tipo_cambio': factura.tipo_cambio,
                'codigo_motivo': request.data.get('codigo_motivo', '01'),
                'descripcion_motivo': request.data.get('descripcion_motivo', 'Anulación de la operación'),
                'documento_modificado_tipo': '01',  # Factura
                'documento_modificado_serie': factura.serie,
                'documento_modificado_numero': factura.numero,
                'items': []
            }
            
            # Copiar items de la factura
            for item in factura.items.all():
                nota_data['items'].append({
                    'producto_id': item.producto.id,
                    'descripcion': item.descripcion,
                    'cantidad': item.cantidad,
                    'precio_unitario': item.precio_unitario,
                    'descuento': item.descuento
                })
            
            # Crear nota de crédito
            serializer = self.get_serializer(data=nota_data)
            if serializer.is_valid():
                nota_credito = serializer.save()
                return Response(
                    self.get_serializer(nota_credito).data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Factura.DoesNotExist:
            return Response(
                {'error': 'La factura no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error al crear nota de crédito desde factura: {e}")
            return Response(
                {'error': f'Error interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SerieComprobanteViewSet(viewsets.ModelViewSet):
    """ViewSet para series de comprobantes"""
    
    queryset = SerieComprobante.objects.all()
    serializer_class = SerieComprobanteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar series por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener series por tipo de comprobante"""
        tipo_comprobante = request.query_params.get('tipo')
        if not tipo_comprobante:
            return Response(
                {'error': 'Se requiere parámetro tipo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        series = self.get_queryset().filter(tipo_comprobante=tipo_comprobante)
        serializer = self.get_serializer(series, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reiniciar_numeracion(self, request, pk=None):
        """Reiniciar numeración de serie (solo administradores)"""
        serie = self.get_object()
        
        if not request.user.is_superuser:
            return Response(
                {'error': 'Solo administradores pueden reiniciar numeración'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        nuevo_numero = request.data.get('siguiente_numero', 1)
        
        try:
            serie.siguiente_numero = int(nuevo_numero)
            serie.save()
            
            logger.warning(f"Numeración reiniciada para serie {serie.serie} por usuario {request.user}")
            
            return Response({
                'success': True,
                'message': f'Numeración reiniciada a {nuevo_numero}',
                'siguiente_numero': serie.siguiente_numero
            })
            
        except ValueError:
            return Response(
                {'error': 'siguiente_numero debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )


# =============================================================================
# VIEWS AUXILIARES
# =============================================================================
class EstadisticasFacturacionView(viewsets.ViewSet):
    """View para estadísticas de facturación"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Estadísticas para dashboard"""
        from django.db.models import Sum, Count, Q
        from datetime import date, timedelta
        
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        semana_pasada = hoy - timedelta(weeks=1)
        mes_pasado = hoy - timedelta(days=30)
        
        # Estadísticas de facturas
        facturas_stats = Factura.objects.aggregate(
            total_hoy=Sum('total', filter=Q(fecha_emision=hoy)),
            cantidad_hoy=Count('id', filter=Q(fecha_emision=hoy)),
            total_ayer=Sum('total', filter=Q(fecha_emision=ayer)),
            total_semana=Sum('total', filter=Q(fecha_emision__gte=semana_pasada)),
            total_mes=Sum('total', filter=Q(fecha_emision__gte=mes_pasado)),
            aceptadas_sunat=Count('id', filter=Q(estado_sunat='ACEPTADO')),
            pendientes_sunat=Count('id', filter=Q(estado_sunat='PENDIENTE')),
            rechazadas_sunat=Count('id', filter=Q(estado_sunat='RECHAZADO'))
        )
        
        # Estadísticas de boletas
        boletas_stats = Boleta.objects.aggregate(
            total_hoy=Sum('total', filter=Q(fecha_emision=hoy)),
            cantidad_hoy=Count('id', filter=Q(fecha_emision=hoy)),
            total_semana=Sum('total', filter=Q(fecha_emision__gte=semana_pasada)),
            total_mes=Sum('total', filter=Q(fecha_emision__gte=mes_pasado))
        )
        
        return Response({
            'fecha_consulta': hoy,
            'facturas': facturas_stats,
            'boletas': boletas_stats,
            'totales': {
                'ingresos_hoy': (facturas_stats.get('total_hoy') or 0) + (boletas_stats.get('total_hoy') or 0),
                'comprobantes_hoy': (facturas_stats.get('cantidad_hoy') or 0) + (boletas_stats.get('cantidad_hoy') or 0),
                'ingresos_semana': (facturas_stats.get('total_semana') or 0) + (boletas_stats.get('total_semana') or 0),
                'ingresos_mes': (facturas_stats.get('total_mes') or 0) + (boletas_stats.get('total_mes') or 0)
            }
        })
    
    @action(detail=False, methods=['get'])
    def ventas_por_periodo(self, request):
        """Ventas agrupadas por período"""
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncDate
        
        periodo = request.query_params.get('periodo', 'dia')  # dia, semana, mes
        limite = int(request.query_params.get('limite', 30))
        
        if periodo == 'dia':
            truncate_func = TruncDate('fecha_emision')
        elif periodo == 'semana':
            truncate_func = TruncDate('fecha_emision')  # Se puede personalizar para semanas
        else:
            truncate_func = TruncDate('fecha_emision')
        
        # Combinar facturas y boletas
        ventas_facturas = Factura.objects.annotate(
            periodo=truncate_func
        ).values('periodo').annotate(
            total_factura=Sum('total'),
            cantidad_factura=Count('id')
        ).order_by('-periodo')[:limite]
        
        ventas_boletas = Boleta.objects.annotate(
            periodo=truncate_func
        ).values('periodo').annotate(
            total_boleta=Sum('total'),
            cantidad_boleta=Count('id')
        ).order_by('-periodo')[:limite]
        
        # Combinar resultados
        ventas_combinadas = {}
        
        for venta in ventas_facturas:
            fecha = venta['periodo']
            ventas_combinadas[fecha] = {
                'fecha': fecha,
                'total_facturas': venta['total_factura'] or 0,
                'cantidad_facturas': venta['cantidad_factura'] or 0,
                'total_boletas': 0,
                'cantidad_boletas': 0
            }
        
        for venta in ventas_boletas:
            fecha = venta['periodo']
            if fecha in ventas_combinadas:
                ventas_combinadas[fecha]['total_boletas'] = venta['total_boleta'] or 0
                ventas_combinadas[fecha]['cantidad_boletas'] = venta['cantidad_boleta'] or 0
            else:
                ventas_combinadas[fecha] = {
                    'fecha': fecha,
                    'total_facturas': 0,
                    'cantidad_facturas': 0,
                    'total_boletas': venta['total_boleta'] or 0,
                    'cantidad_boletas': venta['cantidad_boleta'] or 0
                }
        
        # Calcular totales
        for fecha, datos in ventas_combinadas.items():
            datos['total_general'] = datos['total_facturas'] + datos['total_boletas']
            datos['cantidad_general'] = datos['cantidad_facturas'] + datos['cantidad_boletas']
        
        # Convertir a lista y ordenar
        resultado = list(ventas_combinadas.values())
        resultado.sort(key=lambda x: x['fecha'], reverse=True)
        
        return Response({
            'periodo': periodo,
            'ventas': resultado
        })