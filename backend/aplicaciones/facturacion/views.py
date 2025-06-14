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
    SerieComprobanteSerializer, ConsultaEstadoSerializer, NotaDebitoSerializer, GuiaRemisionSerializer,
    AnularComprobanteSerializer
)
from .filters import FacturaFilter, BoletaFilter, NotaCreditoFilter, NotaDebitoFilter, GuiaRemisionFilter
from aplicaciones.core.permissions import TienePermisoModulo
from aplicaciones.integraciones.services.nubefact import nubefact_service
#from aplicaciones.inventario.services import actualizar_inventario_venta
#from aplicaciones.contabilidad.services import generar_asiento_venta

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
            self.permission_classes = [IsAuthenticated]
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
        


# =============================================================================
# VIEWSETS DE FACTURACIÓN FALTANTES
# =============================================================================

class NotaDebitoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de notas de débito"""
    
    queryset = NotaDebito.objects.select_related('cliente', 'serie_comprobante').prefetch_related('items')
    serializer_class = NotaDebitoSerializer
    permission_classes = [IsAuthenticated, TienePermisoModulo]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NotaDebitoFilter
    search_fields = ['numero', 'cliente__razon_social', 'cliente__numero_documento', 'numero_documento_modificado']
    ordering_fields = ['fecha_emision', 'numero', 'total']
    ordering = ['-fecha_emision', '-numero']
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, TienePermisoModulo]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtrar por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    def perform_create(self, serializer):
        """Crear nota de débito con usuario y empresa actuales"""
        serializer.save(
            usuario_creacion=self.request.user,
            empresa=getattr(self.request.user, 'empresa', None)
        )
    
    @action(detail=True, methods=['post'])
    def enviar_sunat(self, request, pk=None):
        """Enviar nota de débito a SUNAT via Nubefact"""
        nota_debito = self.get_object()
        
        try:
            # Preparar datos para Nubefact
            serializer = self.get_serializer(nota_debito)
            nota_data = serializer._preparar_datos_nubefact(nota_debito)
            
            # Enviar a Nubefact
            response = nubefact_service.emitir_nota_debito(nota_data)
            
            if response.get('success'):
                # Actualizar nota de débito con respuesta
                nota_debito.nubefact_id = response.get('invoice_id')
                nota_debito.estado_sunat = response.get('estado_sunat', 'PENDIENTE')
                nota_debito.hash_cpe = response.get('hash_documento')
                nota_debito.save()
                
                logger.info(f"Nota de débito {nota_debito.numero_completo} enviada a SUNAT")
                
                return Response({
                    'success': True,
                    'message': 'Nota de débito enviada exitosamente a SUNAT'
                })
            else:
                return Response({
                    'success': False,
                    'message': response.get('message', 'Error al enviar a SUNAT')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error al enviar nota de débito a SUNAT: {e}")
            return Response({
                'success': False,
                'message': f'Error al enviar a SUNAT: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def consultar_estado(self, request, pk=None):
        """Consultar estado de la nota de débito en SUNAT"""
        nota_debito = self.get_object()
        
        if not nota_debito.nubefact_id:
            return Response({
                'success': False,
                'message': 'La nota de débito no ha sido enviada a SUNAT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Consultar estado en Nubefact
            response = nubefact_service.consultar_estado(nota_debito.nubefact_id)
            
            if response.get('success'):
                # Actualizar estado local
                nota_debito.estado_sunat = response.get('estado_sunat', nota_debito.estado_sunat)
                nota_debito.save()
                
                return Response({
                    'success': True,
                    'estado_sunat': nota_debito.estado_sunat,
                    'mensaje_sunat': response.get('mensaje_sunat', ''),
                    'fecha_consulta': timezone.now()
                })
            else:
                return Response({
                    'success': False,
                    'message': response.get('message', 'Error al consultar estado')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error al consultar estado en SUNAT: {e}")
            return Response({
                'success': False,
                'message': f'Error al consultar estado: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anular nota de débito"""
        nota_debito = self.get_object()
        
        if nota_debito.estado_sunat == 'ANULADO':
            return Response({
                'success': False,
                'message': 'La nota de débito ya está anulada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Marcar como anulada
                nota_debito.estado_sunat = 'ANULADO'
                nota_debito.fecha_anulacion = timezone.now()
                nota_debito.usuario_anulacion = request.user
                nota_debito.motivo_anulacion = request.data.get('motivo', 'Anulación solicitada por usuario')
                nota_debito.save()
                
                # Generar asiento contable inverso
                generar_asiento_venta(nota_debito, es_nota_credito=True)
                
                logger.info(f"Nota de débito {nota_debito.numero_completo} anulada")
                
                return Response({
                    'success': True,
                    'message': 'Nota de débito anulada exitosamente'
                })
                
        except Exception as e:
            logger.error(f"Error al anular nota de débito: {e}")
            return Response({
                'success': False,
                'message': f'Error al anular: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de notas de débito"""
        queryset = self.get_queryset()
        
        # Estadísticas básicas
        total_notas = queryset.count()
        total_pendientes = queryset.filter(estado_sunat='PENDIENTE').count()
        total_aceptadas = queryset.filter(estado_sunat='ACEPTADO').count()
        total_rechazadas = queryset.filter(estado_sunat='RECHAZADO').count()
        total_anuladas = queryset.filter(estado_sunat='ANULADO').count()
        
        # Estadísticas de montos
        from django.db.models import Sum, Avg
        estadisticas_montos = queryset.aggregate(
            monto_total=Sum('total'),
            monto_promedio=Avg('total')
        )
        
        # Estadísticas por motivo
        estadisticas_motivos = {}
        motivos = queryset.values_list('codigo_motivo', flat=True).distinct()
        for motivo in motivos:
            count = queryset.filter(codigo_motivo=motivo).count()
            estadisticas_motivos[motivo] = count
        
        return Response({
            'totales': {
                'total_notas': total_notas,
                'pendientes': total_pendientes,
                'aceptadas': total_aceptadas,
                'rechazadas': total_rechazadas,
                'anuladas': total_anuladas
            },
            'montos': {
                'monto_total': float(estadisticas_montos['monto_total'] or 0),
                'monto_promedio': float(estadisticas_montos['monto_promedio'] or 0)
            },
            'por_motivo': estadisticas_motivos
        })


class GuiaRemisionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de guías de remisión"""
    
    queryset = GuiaRemision.objects.select_related('empresa').prefetch_related('items')
    serializer_class = GuiaRemisionSerializer
    permission_classes = [IsAuthenticated, TienePermisoModulo]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GuiaRemisionFilter
    search_fields = ['serie_numero', 'transportista_nombre', 'transportista_ruc', 'vehiculo_placa']
    ordering_fields = ['fecha_emision', 'fecha_inicio_traslado', 'peso_bruto_total']
    ordering = ['-fecha_emision', '-fecha_inicio_traslado']
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, TienePermisoModulo]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtrar por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    def perform_create(self, serializer):
        """Crear guía de remisión con usuario y empresa actuales"""
        serializer.save(
            usuario_creacion=self.request.user,
            empresa=getattr(self.request.user, 'empresa', None)
        )
    
    @action(detail=True, methods=['post'])
    def enviar_sunat(self, request, pk=None):
        """Enviar guía de remisión a SUNAT via Nubefact"""
        guia = self.get_object()
        
        try:
            # Preparar datos para Nubefact
            serializer = self.get_serializer(guia)
            guia_data = serializer._preparar_datos_nubefact(guia)
            
            # Enviar a Nubefact
            response = nubefact_service.emitir_guia_remision(guia_data)
            
            if response.get('success'):
                # Actualizar guía con respuesta
                guia.nubefact_id = response.get('invoice_id')
                guia.estado_sunat = response.get('estado_sunat', 'PENDIENTE')
                guia.hash_cpe = response.get('hash_documento')
                guia.save()
                
                logger.info(f"Guía de remisión {guia.serie_numero} enviada a SUNAT")
                
                return Response({
                    'success': True,
                    'message': 'Guía de remisión enviada exitosamente a SUNAT'
                })
            else:
                return Response({
                    'success': False,
                    'message': response.get('message', 'Error al enviar a SUNAT')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error al enviar guía de remisión a SUNAT: {e}")
            return Response({
                'success': False,
                'message': f'Error al enviar a SUNAT: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def consultar_estado(self, request, pk=None):
        """Consultar estado de la guía de remisión en SUNAT"""
        guia = self.get_object()
        
        if not guia.nubefact_id:
            return Response({
                'success': False,
                'message': 'La guía de remisión no ha sido enviada a SUNAT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Consultar estado en Nubefact
            response = nubefact_service.consultar_estado(guia.nubefact_id)
            
            if response.get('success'):
                # Actualizar estado local
                guia.estado_sunat = response.get('estado_sunat', guia.estado_sunat)
                guia.save()
                
                return Response({
                    'success': True,
                    'estado_sunat': guia.estado_sunat,
                    'mensaje_sunat': response.get('mensaje_sunat', ''),
                    'fecha_consulta': timezone.now()
                })
            else:
                return Response({
                    'success': False,
                    'message': response.get('message', 'Error al consultar estado')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error al consultar estado en SUNAT: {e}")
            return Response({
                'success': False,
                'message': f'Error al consultar estado: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def traslados_hoy(self, request):
        """Obtener traslados programados para hoy"""
        from datetime import date
        
        hoy = date.today()
        traslados = self.get_queryset().filter(fecha_inicio_traslado=hoy)
        
        serializer = self.get_serializer(traslados, many=True)
        
        return Response({
            'fecha': hoy,
            'total_traslados': traslados.count(),
            'traslados': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def por_transportista(self, request):
        """Obtener guías agrupadas por transportista"""
        transportistas = {}
        
        for guia in self.get_queryset().select_related():
            transportista = guia.transportista_ruc
            if transportista not in transportistas:
                transportistas[transportista] = {
                    'ruc': guia.transportista_ruc,
                    'nombre': guia.transportista_nombre,
                    'guias': [],
                    'total_peso': 0,
                    'total_guias': 0
                }
            
            transportistas[transportista]['guias'].append({
                'id': guia.id,
                'serie_numero': guia.serie_numero,
                'fecha_emision': guia.fecha_emision,
                'fecha_traslado': guia.fecha_inicio_traslado,
                'peso_bruto': float(guia.peso_bruto_total),
                'estado_sunat': guia.estado_sunat
            })
            transportistas[transportista]['total_peso'] += float(guia.peso_bruto_total)
            transportistas[transportista]['total_guias'] += 1
        
        return Response({
            'transportistas': list(transportistas.values()),
            'resumen': {
                'total_transportistas': len(transportistas),
                'total_guias': sum(t['total_guias'] for t in transportistas.values()),
                'peso_total': sum(t['total_peso'] for t in transportistas.values())
            }
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de guías de remisión"""
        queryset = self.get_queryset()
        
        # Estadísticas básicas
        total_guias = queryset.count()
        total_pendientes = queryset.filter(estado_sunat='PENDIENTE').count()
        total_aceptadas = queryset.filter(estado_sunat='ACEPTADO').count()
        total_rechazadas = queryset.filter(estado_sunat='RECHAZADO').count()
        
        # Estadísticas de peso
        from django.db.models import Sum, Avg
        estadisticas_peso = queryset.aggregate(
            peso_total=Sum('peso_bruto_total'),
            peso_promedio=Avg('peso_bruto_total')
        )
        
        # Estadísticas por tipo de traslado
        estadisticas_traslado = {}
        tipos = queryset.values_list('tipo_traslado', flat=True).distinct()
        for tipo in tipos:
            count = queryset.filter(tipo_traslado=tipo).count()
            estadisticas_traslado[tipo] = count
        
        # Estadísticas por modalidad de transporte
        estadisticas_modalidad = {}
        modalidades = queryset.values_list('modalidad_transporte', flat=True).distinct()
        for modalidad in modalidades:
            count = queryset.filter(modalidad_transporte=modalidad).count()
            estadisticas_modalidad[modalidad] = count
        
        return Response({
            'totales': {
                'total_guias': total_guias,
                'pendientes': total_pendientes,
                'aceptadas': total_aceptadas,
                'rechazadas': total_rechazadas
            },
            'peso': {
                'peso_total': float(estadisticas_peso['peso_total'] or 0),
                'peso_promedio': float(estadisticas_peso['peso_promedio'] or 0)
            },
            'por_tipo_traslado': estadisticas_traslado,
            'por_modalidad_transporte': estadisticas_modalidad
        })


# =============================================================================
# VIEWSETS DE CONTABILIDAD FALTANTES
# =============================================================================

from aplicaciones.contabilidad.models import BalanceComprobacion, PeriodoContable
from aplicaciones.contabilidad.serializers import BalanceComprobacionSerializer, PeriodoContableSerializer
from aplicaciones.contabilidad.filters import BalanceComprobacionFilter, PeriodoContableFilter


class BalanceComprobacionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de balances de comprobación"""
    
    queryset = BalanceComprobacion.objects.select_related('empresa', 'periodo', 'cuenta', 'usuario_generacion')
    serializer_class = BalanceComprobacionSerializer
    permission_classes = [IsAuthenticated, TienePermisoModulo]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BalanceComprobacionFilter
    search_fields = ['cuenta__codigo', 'cuenta__nombre', 'periodo__nombre']
    ordering_fields = ['fecha_desde', 'fecha_hasta', 'cuenta__codigo']
    ordering = ['cuenta__codigo', 'fecha_desde']
    
    def get_queryset(self):
        """Filtrar por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    def perform_create(self, serializer):
        """Crear balance con usuario y empresa actuales"""
        serializer.save(
            usuario_generacion=self.request.user,
            empresa=getattr(self.request.user, 'empresa', None)
        )
    
    @action(detail=False, methods=['post'])
    def generar_balance(self, request):
        """Generar balance de comprobación automáticamente"""
        from aplicaciones.contabilidad.services import ContabilidadService
        
        try:
            fecha_desde = request.data.get('fecha_desde')
            fecha_hasta = request.data.get('fecha_hasta')
            nivel_cuenta = request.data.get('nivel_cuenta', 2)
            
            if not fecha_desde or not fecha_hasta:
                return Response({
                    'success': False,
                    'message': 'Se requieren fecha_desde y fecha_hasta'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar balance usando el servicio
            service = ContabilidadService(empresa_id=getattr(request.user, 'empresa_id', None))
            balance_data = service.generar_balance_comprobacion(
                fecha_desde=datetime.strptime(fecha_desde, '%Y-%m-%d').date(),
                fecha_hasta=datetime.strptime(fecha_hasta, '%Y-%m-%d').date(),
                nivel_cuenta=nivel_cuenta
            )
            
            return Response({
                'success': True,
                'balance': balance_data
            })
            
        except Exception as e:
            logger.error(f"Error al generar balance: {e}")
            return Response({
                'success': False,
                'message': f'Error al generar balance: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def estado_resultados(self, request):
        """Generar estado de resultados"""
        from aplicaciones.contabilidad.services import ContabilidadService
        
        try:
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            if not fecha_desde or not fecha_hasta:
                return Response({
                    'success': False,
                    'message': 'Se requieren fecha_desde y fecha_hasta'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar estado de resultados
            service = ContabilidadService(empresa_id=getattr(request.user, 'empresa_id', None))
            estado_resultados = service.generar_estado_resultados(
                fecha_desde=datetime.strptime(fecha_desde, '%Y-%m-%d').date(),
                fecha_hasta=datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            )
            
            return Response({
                'success': True,
                'estado_resultados': estado_resultados
            })
            
        except Exception as e:
            logger.error(f"Error al generar estado de resultados: {e}")
            return Response({
                'success': False,
                'message': f'Error al generar estado de resultados: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PeriodoContableViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de períodos contables"""
    
    queryset = PeriodoContable.objects.select_related('empresa', 'usuario_cierre')
    serializer_class = PeriodoContableSerializer
    permission_classes = [IsAuthenticated, TienePermisoModulo]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PeriodoContableFilter
    search_fields = ['nombre', 'año']
    ordering_fields = ['año', 'mes', 'fecha_inicio']
    ordering = ['-año', '-mes']
    
    def get_queryset(self):
        """Filtrar por empresa del usuario"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset
    
    def perform_create(self, serializer):
        """Crear período con empresa actual"""
        serializer.save(
            empresa=getattr(self.request.user, 'empresa', None)
        )
    
    @action(detail=True, methods=['post'])
    def cerrar_periodo(self, request, pk=None):
        """Cerrar período contable"""
        periodo = self.get_object()
        
        try:
            observaciones = request.data.get('observaciones', '')
            periodo.cerrar_periodo(request.user, observaciones)
            
            logger.info(f"Período {periodo.nombre} cerrado por {request.user.username}")
            
            return Response({
                'success': True,
                'message': 'Período cerrado exitosamente'
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error al cerrar período: {e}")
            return Response({
                'success': False,
                'message': f'Error al cerrar período: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reabrir_periodo(self, request, pk=None):
        """Reabrir período contable"""
        periodo = self.get_object()
        
        try:
            periodo.reabrir_periodo(request.user)
            
            logger.info(f"Período {periodo.nombre} reabierto por {request.user.username}")
            
            return Response({
                'success': True,
                'message': 'Período reabierto exitosamente'
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error al reabrir período: {e}")
            return Response({
                'success': False,
                'message': f'Error al reabrir período: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def periodo_actual(self, request):
        """Obtener período contable actual"""
        from datetime import date
        
        hoy = date.today()
        periodo_actual = self.get_queryset().filter(
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
            estado='abierto'
        ).first()
        
        if periodo_actual:
            serializer = self.get_serializer(periodo_actual)
            return Response({
                'success': True,
                'periodo_actual': serializer.data
            })
        else:
            return Response({
                'success': False,
                'message': 'No hay período contable activo para la fecha actual'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Obtener resumen de períodos contables"""
        queryset = self.get_queryset()
        
        # Estadísticas básicas
        total_periodos = queryset.count()
        periodos_abiertos = queryset.filter(estado='abierto').count()
        periodos_cerrados = queryset.filter(estado='cerrado').count()
        periodos_auditoria = queryset.filter(estado='auditoria').count()
        periodos_bloqueados = queryset.filter(estado='bloqueado').count()
        
        # Períodos por año
        from django.db.models import Count
        por_año = queryset.values('año').annotate(
            count=Count('id')
        ).order_by('-año')
        
        return Response({
            'totales': {
                'total_periodos': total_periodos,
                'abiertos': periodos_abiertos,
                'cerrados': periodos_cerrados,
                'en_auditoria': periodos_auditoria,
                'bloqueados': periodos_bloqueados
            },
            'por_año': list(por_año)
        })