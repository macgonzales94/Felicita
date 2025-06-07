"""
VIEWS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Views para la API REST del módulo core
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    Empresa, Cliente, Proveedor, CategoriaProducto,
    Producto, ConfiguracionSistema
)
from .serializers import (
    EmpresaSerializer, EmpresaResumenSerializer,
    ClienteSerializer, ClienteResumenSerializer,
    ProveedorSerializer,
    CategoriaProductoSerializer, CategoriaProductoResumenSerializer,
    ProductoSerializer, ProductoResumenSerializer,
    ConfiguracionSistemaSerializer,
    BusquedaClienteSerializer, BusquedaProductoSerializer
)
from .filters import ClienteFilter, ProductoFilter
from .utils import validar_ruc_sunat, validar_dni_reniec

logger = logging.getLogger('felicita.core')


# =============================================================================
# VIEWSET BASE
# =============================================================================
class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base con funcionalidades comunes
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        """
        Filtrar por empresa del usuario autenticado
        """
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            return queryset.filter(empresa=self.request.user.empresa)
        return queryset.none()
    
    def perform_create(self, serializer):
        """
        Asignar empresa automáticamente al crear
        """
        if hasattr(self.request.user, 'empresa') and hasattr(serializer.Meta.model, 'empresa'):
            serializer.save(empresa=self.request.user.empresa)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas del modelo
        """
        queryset = self.get_queryset()
        total = queryset.count()
        activos = queryset.filter(activo=True).count()
        
        return Response({
            'total': total,
            'activos': activos,
            'inactivos': total - activos,
            'porcentaje_activos': round((activos / total * 100) if total > 0 else 0, 2)
        })


# =============================================================================
# VIEWSET EMPRESA
# =============================================================================
class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de empresas
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmpresaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['razon_social', 'nombre_comercial', 'ruc']
    ordering_fields = ['razon_social', 'creado_en']
    ordering = ['razon_social']
    
    def get_queryset(self):
        """Solo la empresa del usuario autenticado"""
        if hasattr(self.request.user, 'empresa'):
            return Empresa.objects.filter(id=self.request.user.empresa.id)
        return Empresa.objects.none()
    
    def get_serializer_class(self):
        """Usar serializer resumido para listas"""
        if self.action == 'list':
            return EmpresaResumenSerializer
        return EmpresaSerializer
    
    @action(detail=True, methods=['post'])
    def validar_ruc(self, request, pk=None):
        """
        Validar RUC con SUNAT
        """
        empresa = self.get_object()
        
        try:
            # Validación local
            es_valido_local = empresa.validar_ruc()
            
            # Validación con SUNAT (opcional)
            datos_sunat = None
            if request.data.get('consultar_sunat', False):
                datos_sunat = validar_ruc_sunat(empresa.ruc)
            
            return Response({
                'ruc': empresa.ruc,
                'es_valido_local': es_valido_local,
                'datos_sunat': datos_sunat,
                'validado_en': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error validando RUC {empresa.ruc}: {e}")
            return Response(
                {'error': 'Error al validar RUC'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfiguracionEmpresaView(APIView):
    """
    Vista para configuraciones específicas de la empresa
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Obtener configuraciones de la empresa
        """
        try:
            empresa = Empresa.objects.get(pk=pk)
            
            if empresa != request.user.empresa:
                return Response(
                    {'error': 'No tiene permisos para esta empresa'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            configuraciones = ConfiguracionSistema.objects.all()
            serializer = ConfiguracionSistemaSerializer(configuraciones, many=True)
            
            return Response({
                'empresa': EmpresaSerializer(empresa).data,
                'configuraciones': serializer.data
            })
            
        except Empresa.DoesNotExist:
            return Response(
                {'error': 'Empresa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class SeriesComprobantesEmpresaView(APIView):
    """
    Vista para series de comprobantes de la empresa
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Obtener series de comprobantes
        """
        # TODO: Implementar cuando se tenga el modelo SerieComprobante
        return Response([])


class PlanCuentasEmpresaView(APIView):
    """
    Vista para plan de cuentas de la empresa
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Obtener plan de cuentas
        """
        # TODO: Implementar cuando se tenga el módulo de contabilidad
        return Response([])


# =============================================================================
# VIEWSET CLIENTE
# =============================================================================
class ClienteViewSet(BaseViewSet):
    """
    ViewSet para gestión de clientes
    """
    serializer_class = ClienteSerializer
    filterset_class = ClienteFilter
    search_fields = ['razon_social', 'nombres', 'apellido_paterno', 'numero_documento']
    ordering_fields = ['razon_social', 'creado_en', 'numero_documento']
    ordering = ['razon_social']
    
    def get_queryset(self):
        """Clientes de la empresa del usuario"""
        return Cliente.objects.all()
    
    def get_serializer_class(self):
        """Usar serializer resumido para listas"""
        if self.action == 'list':
            return ClienteResumenSerializer
        return ClienteSerializer
    
    @action(detail=False, methods=['post'])
    def buscar(self, request):
        """
        Búsqueda avanzada de clientes
        """
        serializer = BusquedaClienteSerializer(data=request.data)
        if serializer.is_valid():
            termino = serializer.validated_data['termino']
            tipo_documento = serializer.validated_data.get('tipo_documento', 'TODOS')
            incluir_bloqueados = serializer.validated_data.get('incluir_bloqueados', False)
            
            queryset = self.get_queryset()
            
            # Filtrar por término de búsqueda
            queryset = queryset.filter(
                Q(razon_social__icontains=termino) |
                Q(nombres__icontains=termino) |
                Q(apellido_paterno__icontains=termino) |
                Q(numero_documento__icontains=termino) |
                Q(email__icontains=termino)
            )
            
            # Filtrar por tipo de documento
            if tipo_documento != 'TODOS':
                queryset = queryset.filter(tipo_documento=tipo_documento)
            
            # Filtrar bloqueados
            if not incluir_bloqueados:
                queryset = queryset.filter(bloqueado=False)
            
            # Ordenar por relevancia
            queryset = queryset.order_by('razon_social')[:20]  # Limitar a 20 resultados
            
            serializer = ClienteResumenSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def validar_documento(self, request):
        """
        Validar documento de cliente (DNI/RUC)
        """
        numero_documento = request.data.get('numero_documento')
        tipo_documento = request.data.get('tipo_documento', 'DNI')
        
        if not numero_documento:
            return Response(
                {'error': 'Número de documento requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if tipo_documento == 'DNI':
                # Validar DNI
                if len(numero_documento) != 8 or not numero_documento.isdigit():
                    return Response({'es_valido': False, 'mensaje': 'DNI inválido'})
                
                # Consultar RENIEC (opcional)
                datos_reniec = None
                if request.data.get('consultar_reniec', False):
                    datos_reniec = validar_dni_reniec(numero_documento)
                
                return Response({
                    'numero_documento': numero_documento,
                    'tipo_documento': tipo_documento,
                    'es_valido': True,
                    'datos_reniec': datos_reniec
                })
            
            elif tipo_documento == 'RUC':
                # Validar RUC
                if len(numero_documento) != 11 or not numero_documento.isdigit():
                    return Response({'es_valido': False, 'mensaje': 'RUC inválido'})
                
                # Validar con algoritmo SUNAT
                factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
                suma = sum(int(numero_documento[i]) * factores[i] for i in range(10))
                resto = suma % 11
                digito_verificador = 11 - resto if resto >= 2 else resto
                
                es_valido = digito_verificador == int(numero_documento[10])
                
                # Consultar SUNAT (opcional)
                datos_sunat = None
                if request.data.get('consultar_sunat', False) and es_valido:
                    datos_sunat = validar_ruc_sunat(numero_documento)
                
                return Response({
                    'numero_documento': numero_documento,
                    'tipo_documento': tipo_documento,
                    'es_valido': es_valido,
                    'datos_sunat': datos_sunat
                })
            
            else:
                return Response({'es_valido': True, 'mensaje': 'Tipo de documento no validado automáticamente'})
                
        except Exception as e:
            logger.error(f"Error validando documento {numero_documento}: {e}")
            return Response(
                {'error': 'Error al validar documento'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def historial_compras(self, request, pk=None):
        """
        Historial de compras del cliente
        """
        cliente = self.get_object()
        # TODO: Implementar cuando se tenga el módulo de facturación
        return Response([])
    
    @action(detail=True, methods=['get'])
    def estado_cuenta(self, request, pk=None):
        """
        Estado de cuenta del cliente
        """
        cliente = self.get_object()
        # TODO: Implementar estado de cuenta
        return Response({
            'cliente': ClienteResumenSerializer(cliente).data,
            'limite_credito': cliente.limite_credito,
            'credito_usado': 0,  # TODO: Calcular
            'credito_disponible': cliente.limite_credito,
            'facturas_pendientes': [],
            'total_pendiente': 0
        })


class BuscarClienteView(APIView):
    """
    Vista para búsqueda simple de clientes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Búsqueda simple por query parameter
        """
        q = request.query_params.get('q', '')
        if len(q) < 2:
            return Response([])
        
        clientes = Cliente.objects.filter(
            Q(razon_social__icontains=q) |
            Q(numero_documento__icontains=q) |
            Q(email__icontains=q)
        ).filter(activo=True, bloqueado=False)[:10]
        
        serializer = ClienteResumenSerializer(clientes, many=True)
        return Response(serializer.data)


# =============================================================================
# VIEWSET PROVEEDOR
# =============================================================================
class ProveedorViewSet(BaseViewSet):
    """
    ViewSet para gestión de proveedores
    """
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    search_fields = ['razon_social', 'nombre_comercial', 'ruc']
    ordering_fields = ['razon_social', 'creado_en']
    ordering = ['razon_social']


# =============================================================================
# VIEWSET CATEGORÍA PRODUCTO
# =============================================================================
class CategoriaProductoViewSet(BaseViewSet):
    """
    ViewSet para gestión de categorías de productos
    """
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer
    search_fields = ['codigo', 'nombre']
    ordering_fields = ['codigo', 'nombre', 'creado_en']
    ordering = ['codigo']
    
    def get_serializer_class(self):
        """Usar serializer resumido para listas"""
        if self.action == 'list':
            return CategoriaProductoResumenSerializer
        return CategoriaProductoSerializer
    
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """
        Productos de una categoría
        """
        categoria = self.get_object()
        productos = categoria.productos.filter(activo=True)
        serializer = ProductoResumenSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subcategorias(self, request, pk=None):
        """
        Subcategorías de una categoría
        """
        categoria = self.get_object()
        subcategorias = categoria.subcategorias.filter(activo=True)
        serializer = CategoriaProductoResumenSerializer(subcategorias, many=True)
        return Response(serializer.data)


class ProductosPorCategoriaView(APIView):
    """
    Vista para productos por categoría
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Obtener productos de una categoría
        """
        try:
            categoria = CategoriaProducto.objects.get(pk=pk)
            productos = categoria.productos.filter(activo=True, activo_venta=True)
            serializer = ProductoResumenSerializer(productos, many=True)
            return Response(serializer.data)
        except CategoriaProducto.DoesNotExist:
            return Response(
                {'error': 'Categoría no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


# =============================================================================
# VIEWSET PRODUCTO
# =============================================================================
class ProductoViewSet(BaseViewSet):
    """
    ViewSet para gestión de productos
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filterset_class = ProductoFilter
    search_fields = ['codigo', 'nombre', 'descripcion', 'codigo_barras']
    ordering_fields = ['codigo', 'nombre', 'precio_venta', 'creado_en']
    ordering = ['codigo']
    
    def get_serializer_class(self):
        """Usar serializer resumido para listas"""
        if self.action == 'list':
            return ProductoResumenSerializer
        return ProductoSerializer
    
    @action(detail=False, methods=['post'])
    def buscar(self, request):
        """
        Búsqueda avanzada de productos
        """
        serializer = BusquedaProductoSerializer(data=request.data)
        if serializer.is_valid():
            termino = serializer.validated_data['termino']
            categoria = serializer.validated_data.get('categoria')
            solo_activos_venta = serializer.validated_data.get('solo_activos_venta', True)
            con_stock = serializer.validated_data.get('con_stock', False)
            
            queryset = self.get_queryset()
            
            # Filtrar por término
            queryset = queryset.filter(
                Q(codigo__icontains=termino) |
                Q(nombre__icontains=termino) |
                Q(descripcion__icontains=termino) |
                Q(codigo_barras__icontains=termino)
            )
            
            # Filtros adicionales
            if categoria:
                queryset = queryset.filter(categoria=categoria)
            
            if solo_activos_venta:
                queryset = queryset.filter(activo_venta=True)
            
            # TODO: Implementar filtro con_stock cuando se tenga StockProducto
            
            queryset = queryset.order_by('nombre')[:20]
            
            serializer = ProductoResumenSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def por_codigo_barras(self, request):
        """
        Buscar producto por código de barras
        """
        codigo_barras = request.query_params.get('codigo')
        if not codigo_barras:
            return Response(
                {'error': 'Código de barras requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            producto = self.get_queryset().get(codigo_barras=codigo_barras, activo=True)
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """
        Stock actual del producto
        """
        producto = self.get_object()
        # TODO: Implementar cuando se tenga StockProducto
        return Response({
            'producto': ProductoResumenSerializer(producto).data,
            'stock_total': 0,
            'stock_disponible': 0,
            'stock_reservado': 0,
            'almacenes': []
        })


class BuscarProductoView(APIView):
    """
    Vista para búsqueda simple de productos
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Búsqueda simple por query parameter
        """
        q = request.query_params.get('q', '')
        if len(q) < 2:
            return Response([])
        
        productos = Producto.objects.filter(
            Q(codigo__icontains=q) |
            Q(nombre__icontains=q) |
            Q(codigo_barras__icontains=q)
        ).filter(activo=True, activo_venta=True)[:10]
        
        serializer = ProductoResumenSerializer(productos, many=True)
        return Response(serializer.data)


class ProductoPorCodigoBarrasView(APIView):
    """
    Vista para búsqueda por código de barras
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Buscar por código de barras
        """
        codigo = request.query_params.get('codigo')
        if not codigo:
            return Response({'error': 'Código requerido'}, status=400)
        
        try:
            producto = Producto.objects.get(
                codigo_barras=codigo,
                activo=True,
                activo_venta=True
            )
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=404)


# =============================================================================
# VIEWSET CONFIGURACIÓN SISTEMA
# =============================================================================
class ConfiguracionSistemaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para configuraciones del sistema
    """
    queryset = ConfiguracionSistema.objects.all()
    serializer_class = ConfiguracionSistemaSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['clave', 'descripcion']
    ordering_fields = ['clave', 'actualizado_en']
    ordering = ['clave']
    
    @action(detail=False, methods=['get'])
    def por_clave(self, request):
        """
        Obtener configuración por clave
        """
        clave = request.query_params.get('clave')
        if not clave:
            return Response({'error': 'Clave requerida'}, status=400)
        
        try:
            config = ConfiguracionSistema.objects.get(clave=clave)
            serializer = ConfiguracionSistemaSerializer(config)
            return Response(serializer.data)
        except ConfiguracionSistema.DoesNotExist:
            return Response({'error': 'Configuración no encontrada'}, status=404)


class ConfiguracionPorClaveView(APIView):
    """
    Vista para obtener configuración por clave
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, clave):
        """
        Obtener configuración específica
        """
        try:
            config = ConfiguracionSistema.objects.get(clave=clave)
            serializer = ConfiguracionSistemaSerializer(config)
            return Response(serializer.data)
        except ConfiguracionSistema.DoesNotExist:
            return Response(
                {'error': 'Configuración no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


# =============================================================================
# VISTAS DE ESTADÍSTICAS Y DASHBOARD
# =============================================================================
class EstadisticasDashboardView(APIView):
    """
    Estadísticas generales para el dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Obtener estadísticas del dashboard
        """
        try:
            # Estadísticas básicas
            total_clientes = Cliente.objects.filter(activo=True).count()
            total_productos = Producto.objects.filter(activo=True).count()
            productos_activos_venta = Producto.objects.filter(activo=True, activo_venta=True).count()
            clientes_bloqueados = Cliente.objects.filter(bloqueado=True).count()
            
            # Estadísticas de crecimiento (últimos 30 días)
            hace_30_dias = timezone.now() - timedelta(days=30)
            clientes_nuevos = Cliente.objects.filter(creado_en__gte=hace_30_dias).count()
            productos_nuevos = Producto.objects.filter(creado_en__gte=hace_30_dias).count()
            
            return Response({
                'resumen': {
                    'total_clientes': total_clientes,
                    'total_productos': total_productos,
                    'productos_activos_venta': productos_activos_venta,
                    'clientes_bloqueados': clientes_bloqueados
                },
                'crecimiento_30_dias': {
                    'clientes_nuevos': clientes_nuevos,
                    'productos_nuevos': productos_nuevos
                },
                'fecha_actualizacion': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del dashboard: {e}")
            return Response(
                {'error': 'Error al obtener estadísticas'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )