"""
FELICITA - Views Core
Sistema de Facturación Electrónica para Perú

ViewSets y vistas para las entidades base del sistema
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import (
    Empresa, Sucursal, Cliente, Configuracion,
    TipoComprobante, SerieComprobante
)
from .serializers import (
    EmpresaSerializer, EmpresaListSerializer,
    SucursalSerializer,
    ClienteSerializer, ClienteListSerializer, ClienteSimpleSerializer,
    ConfiguracionSerializer,
    TipoComprobanteSerializer, TipoComprobanteSimpleSerializer,
    SerieComprobanteSerializer, SerieComprobanteSimpleSerializer,
    ValidarDocumentoSerializer, EstadisticasEmpresaSerializer,
    ImportarClientesSerializer, ExportarClientesSerializer
)
from aplicaciones.integraciones.services.apis_peru import ApisPeru
import logging
import pandas as pd
from io import BytesIO

logger = logging.getLogger('felicita.core')

# ===========================================
# VIEWSET BASE
# ===========================================

class BaseViewSet(viewsets.ModelViewSet):
    """ViewSet base con funcionalidades comunes"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        """Filtrar por empresa del usuario"""
        queryset = super().get_queryset()
        
        # Filtrar por empresa del usuario si tiene empresa asignada
        if hasattr(self.request.user, 'empresa') and self.request.user.empresa:
            if hasattr(queryset.model, 'empresa'):
                queryset = queryset.filter(empresa=self.request.user.empresa)
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar empresa automáticamente al crear"""
        # Si el modelo tiene campo empresa y el usuario tiene empresa
        if (hasattr(serializer.Meta.model, 'empresa') and 
            hasattr(self.request.user, 'empresa') and 
            self.request.user.empresa):
            serializer.save(empresa=self.request.user.empresa)
        else:
            serializer.save()
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """Activar/desactivar registro"""
        obj = self.get_object()
        obj.activo = not obj.activo
        obj.save(update_fields=['activo'])
        
        status_text = 'activado' if obj.activo else 'desactivado'
        return Response({
            'message': f'{obj.__class__.__name__} {status_text} correctamente',
            'activo': obj.activo
        })

# ===========================================
# EMPRESA VIEWSET
# ===========================================

class EmpresaViewSet(viewsets.ModelViewSet):
    """ViewSet para Empresa"""
    
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['ruc', 'razon_social', 'nombre_comercial']
    ordering_fields = ['razon_social', 'fecha_creacion']
    ordering = ['razon_social']
    
    def get_serializer_class(self):
        """Usar serializer simplificado para lista"""
        if self.action == 'list':
            return EmpresaListSerializer
        return self.serializer_class
    
    def get_queryset(self):
        """Filtrar empresas según usuario"""
        queryset = super().get_queryset()
        
        # Superusuario ve todas las empresas
        if self.request.user.is_superuser:
            return queryset
        
        # Usuario con empresa ve solo su empresa
        if hasattr(self.request.user, 'empresa') and self.request.user.empresa:
            return queryset.filter(id=self.request.user.empresa.id)
        
        # Usuario sin empresa no ve ninguna
        return queryset.none()
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtener estadísticas de la empresa"""
        empresa = self.get_object()
        
        stats = {
            'total_clientes': empresa.clientes.count(),
            'total_sucursales': empresa.sucursales.count(),
            'total_series': empresa.series.count(),
            'clientes_activos': empresa.clientes.filter(activo=True).count(),
            'clientes_con_credito': empresa.clientes.filter(
                limite_credito__gt=0, activo=True
            ).count(),
            'configuracion_completa': empresa.esta_configurada_para_facturacion(),
        }
        
        serializer = EstadisticasEmpresaSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def configurar_series(self, request, pk=None):
        """Configurar series iniciales para la empresa"""
        empresa = self.get_object()
        
        try:
            # Crear series para tipos principales si no existen
            tipos_principales = ['01', '03', '07', '08']
            series_creadas = []
            
            for codigo_tipo in tipos_principales:
                try:
                    tipo = TipoComprobante.objects.get(codigo=codigo_tipo, activo=True)
                    
                    # Verificar si ya existe serie para este tipo
                    if not empresa.series.filter(tipo_comprobante=tipo, activo=True).exists():
                        serie_inicial = {
                            '01': 'F001',
                            '03': 'B001', 
                            '07': 'FC01',
                            '08': 'FD01',
                        }.get(codigo_tipo, 'X001')
                        
                        serie = SerieComprobante.objects.create(
                            empresa=empresa,
                            tipo_comprobante=tipo,
                            serie=serie_inicial
                        )
                        series_creadas.append(serie)
                        
                except TipoComprobante.DoesNotExist:
                    continue
            
            return Response({
                'message': f'Se crearon {len(series_creadas)} series',
                'series_creadas': [
                    f"{s.tipo_comprobante.nombre} - {s.serie}" 
                    for s in series_creadas
                ]
            })
            
        except Exception as e:
            logger.error(f"Error configurando series para empresa {pk}: {e}")
            return Response(
                {'error': 'Error al configurar series'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ===========================================
# SUCURSAL VIEWSET
# ===========================================

class SucursalViewSet(BaseViewSet):
    """ViewSet para Sucursal"""
    
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    filterset_fields = ['empresa', 'es_principal', 'activo']
    search_fields = ['codigo', 'nombre', 'direccion']
    ordering_fields = ['nombre', 'fecha_creacion']
    ordering = ['nombre']
    
    @action(detail=True, methods=['post'])
    def establecer_principal(self, request, pk=None):
        """Establecer como sucursal principal"""
        sucursal = self.get_object()
        
        try:
            # Desactivar otras sucursales principales de la misma empresa
            Sucursal.objects.filter(
                empresa=sucursal.empresa,
                es_principal=True,
                activo=True
            ).update(es_principal=False)
            
            # Establecer como principal
            sucursal.es_principal = True
            sucursal.save(update_fields=['es_principal'])
            
            return Response({
                'message': f'Sucursal {sucursal.nombre} establecida como principal'
            })
            
        except Exception as e:
            logger.error(f"Error estableciendo sucursal principal {pk}: {e}")
            return Response(
                {'error': 'Error al establecer sucursal principal'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ===========================================
# CLIENTE VIEWSET
# ===========================================

class ClienteViewSet(BaseViewSet):
    """ViewSet para Cliente"""
    
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filterset_fields = ['empresa', 'tipo_documento', 'activo']
    search_fields = ['numero_documento', 'razon_social', 'nombre_comercial', 'email']
    ordering_fields = ['razon_social', 'fecha_creacion']
    ordering = ['razon_social']
    
    def get_serializer_class(self):
        """Usar serializer apropiado según acción"""
        if self.action == 'list':
            return ClienteListSerializer
        elif self.action in ['simple', 'autocompletar']:
            return ClienteSimpleSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def simple(self, request):
        """Lista simplificada para selects"""
        queryset = self.filter_queryset(self.get_queryset().filter(activo=True))
        
        # Búsqueda por término
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(numero_documento__icontains=search) |
                Q(razon_social__icontains=search) |
                Q(nombre_comercial__icontains=search)
            )[:20]  # Limitar resultados
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def autocompletar(self, request):
        """Autocompletado para búsquedas"""
        return self.simple(request)
    
    @action(detail=False, methods=['post'])
    def validar_documento(self, request):
        """Validar documento con APIs externas"""
        serializer = ValidarDocumentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tipo = serializer.validated_data['tipo_documento']
        numero = serializer.validated_data['numero_documento']
        
        try:
            apis_peru = ApisPeru()
            
            if tipo == 'dni':
                resultado = apis_peru.consultar_dni(numero)
            else:  # ruc
                resultado = apis_peru.consultar_ruc(numero)
            
            return Response(resultado)
            
        except Exception as e:
            logger.error(f"Error validando documento {numero}: {e}")
            return Response({
                'exito': False,
                'error': 'Error al validar documento con APIs externas'
            })
    
    @action(detail=False, methods=['post'])
    def importar(self, request):
        """Importar clientes desde Excel/CSV"""
        serializer = ImportarClientesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        archivo = serializer.validated_data['archivo']
        empresa = serializer.validated_data['empresa']
        sobrescribir = serializer.validated_data['sobrescribir_existentes']
        
        try:
            # Leer archivo según extensión
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            # Validar columnas requeridas
            columnas_requeridas = ['tipo_documento', 'numero_documento', 'razon_social']
            columnas_faltantes = set(columnas_requeridas) - set(df.columns)
            
            if columnas_faltantes:
                return Response({
                    'error': f'Columnas faltantes: {", ".join(columnas_faltantes)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Procesar clientes
            clientes_creados = 0
            clientes_actualizados = 0
            errores = []
            
            for index, row in df.iterrows():
                try:
                    # Preparar datos
                    datos_cliente = {
                        'empresa': empresa,
                        'tipo_documento': row['tipo_documento'],
                        'numero_documento': str(row['numero_documento']).strip(),
                        'razon_social': str(row['razon_social']).strip(),
                        'nombre_comercial': str(row.get('nombre_comercial', '')).strip() or None,
                        'direccion': str(row.get('direccion', '')).strip() or None,
                        'telefono': str(row.get('telefono', '')).strip() or None,
                        'email': str(row.get('email', '')).strip() or None,
                    }
                    
                    # Verificar si existe
                    cliente_existente = Cliente.objects.filter(
                        empresa=empresa,
                        numero_documento=datos_cliente['numero_documento']
                    ).first()
                    
                    if cliente_existente:
                        if sobrescribir:
                            # Actualizar cliente existente
                            for key, value in datos_cliente.items():
                                if key != 'empresa' and value is not None:
                                    setattr(cliente_existente, key, value)
                            cliente_existente.save()
                            clientes_actualizados += 1
                    else:
                        # Crear nuevo cliente
                        cliente = Cliente(**datos_cliente)
                        cliente.full_clean()
                        cliente.save()
                        clientes_creados += 1
                        
                except Exception as e:
                    errores.append(f"Fila {index + 2}: {str(e)}")
            
            return Response({
                'message': 'Importación completada',
                'clientes_creados': clientes_creados,
                'clientes_actualizados': clientes_actualizados,
                'errores': errores[:10]  # Máximo 10 errores
            })
            
        except Exception as e:
            logger.error(f"Error en importación de clientes: {e}")
            return Response({
                'error': 'Error procesando el archivo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def exportar(self, request):
        """Exportar clientes a Excel/CSV"""
        serializer = ExportarClientesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        empresa = serializer.validated_data.get('empresa')
        formato = serializer.validated_data['formato']
        incluir_inactivos = serializer.validated_data['incluir_inactivos']
        tipo_documento = serializer.validated_data.get('tipo_documento', 'todos')
        
        try:
            # Filtrar clientes
            queryset = self.get_queryset()
            
            if empresa:
                queryset = queryset.filter(empresa=empresa)
            
            if not incluir_inactivos:
                queryset = queryset.filter(activo=True)
            
            if tipo_documento != 'todos':
                queryset = queryset.filter(tipo_documento=tipo_documento)
            
            # Preparar datos
            datos = []
            for cliente in queryset:
                datos.append({
                    'Tipo Documento': cliente.get_tipo_documento_display(),
                    'Número Documento': cliente.numero_documento,
                    'Razón Social': cliente.razon_social,
                    'Nombre Comercial': cliente.nombre_comercial or '',
                    'Dirección': cliente.direccion or '',
                    'Teléfono': cliente.telefono or '',
                    'Email': cliente.email or '',
                    'Límite Crédito': cliente.limite_credito,
                    'Días Crédito': cliente.dias_credito,
                    'Activo': 'Sí' if cliente.activo else 'No',
                    'Fecha Creación': cliente.fecha_creacion.strftime('%d/%m/%Y'),
                })
            
            df = pd.DataFrame(datos)
            
            # Generar archivo según formato
            if formato == 'xlsx':
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Clientes', index=False)
                output.seek(0)
                
                response = HttpResponse(
                    output.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'
                
            elif formato == 'csv':
                output = StringIO()
                df.to_csv(output, index=False, encoding='utf-8')
                
                response = HttpResponse(output.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="clientes.csv"'
                
            return response
            
        except Exception as e:
            logger.error(f"Error exportando clientes: {e}")
            return Response({
                'error': 'Error al exportar clientes'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===========================================
# CONFIGURACIÓN VIEWSET
# ===========================================

class ConfiguracionViewSet(BaseViewSet):
    """ViewSet para Configuración"""
    
    queryset = Configuracion.objects.all()
    serializer_class = ConfiguracionSerializer
    filterset_fields = ['empresa']
    
    def get_queryset(self):
        """Una configuración por empresa"""
        queryset = super().get_queryset()
        
        # Si usuario tiene empresa, mostrar solo su configuración
        if hasattr(self.request.user, 'empresa') and self.request.user.empresa:
            return queryset.filter(empresa=self.request.user.empresa)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def mi_configuracion(self, request):
        """Obtener configuración de la empresa del usuario"""
        if not hasattr(request.user, 'empresa') or not request.user.empresa:
            return Response({
                'error': 'Usuario no tiene empresa asignada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        configuracion = get_object_or_404(
            Configuracion, 
            empresa=request.user.empresa
        )
        serializer = self.get_serializer(configuracion)
        return Response(serializer.data)

# ===========================================
# TIPO COMPROBANTE VIEWSET
# ===========================================

class TipoComprobanteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Tipo de Comprobante (solo lectura)"""
    
    queryset = TipoComprobante.objects.filter(activo=True)
    serializer_class = TipoComprobanteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']
    
    def get_serializer_class(self):
        """Usar serializer simple para lista"""
        if self.action == 'list':
            return TipoComprobanteSimpleSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def principales(self, request):
        """Obtener tipos principales (Factura, Boleta, NC, ND)"""
        tipos_principales = self.get_queryset().filter(
            codigo__in=['01', '03', '07', '08']
        )
        serializer = TipoComprobanteSimpleSerializer(tipos_principales, many=True)
        return Response(serializer.data)

# ===========================================
# SERIE COMPROBANTE VIEWSET
# ===========================================

class SerieComprobanteViewSet(BaseViewSet):
    """ViewSet para Serie de Comprobante"""
    
    queryset = SerieComprobante.objects.all()
    serializer_class = SerieComprobanteSerializer
    filterset_fields = ['empresa', 'tipo_comprobante', 'sucursal', 'activo']
    search_fields = ['serie']
    ordering_fields = ['serie', 'fecha_creacion']
    ordering = ['tipo_comprobante__codigo', 'serie']
    
    def get_serializer_class(self):
        """Usar serializer apropiado según acción"""
        if self.action in ['list', 'por_tipo']:
            return SerieComprobanteSimpleSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener series por tipo de comprobante"""
        tipo_id = request.query_params.get('tipo_comprobante')
        if not tipo_id:
            return Response({
                'error': 'Parámetro tipo_comprobante requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.filter_queryset(
            self.get_queryset().filter(
                tipo_comprobante_id=tipo_id,
                activo=True
            )
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def obtener_siguiente_numero(self, request, pk=None):
        """Obtener siguiente número correlativo"""
        serie = self.get_object()
        siguiente_numero = serie.obtener_siguiente_numero()
        
        return Response({
            'serie': serie.serie,
            'numero_anterior': siguiente_numero - 1,
            'numero_actual': siguiente_numero,
            'comprobante': f"{serie.serie}-{siguiente_numero:08d}"
        })
    
    @action(detail=True, methods=['post'])
    def reiniciar_numeracion(self, request, pk=None):
        """Reiniciar numeración (solo superusuario)"""
        if not request.user.is_superuser:
            return Response({
                'error': 'Solo superusuarios pueden reiniciar numeración'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serie = self.get_object()
        numero_anterior = serie.numero_actual
        serie.reiniciar_numeracion()
        
        logger.warning(
            f"Numeración reiniciada por {request.user.username} "
            f"para serie {serie}: {numero_anterior} -> 0"
        )
        
        return Response({
            'message': f'Numeración reiniciada para serie {serie.serie}',
            'numero_anterior': numero_anterior,
            'numero_actual': serie.numero_actual
        })