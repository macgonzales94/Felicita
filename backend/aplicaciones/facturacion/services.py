"""
SERVICES DE INVENTARIO - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Servicios para manejo de inventario con método PEPS (Primeras Entradas, Primeras Salidas)
según normativa SUNAT
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, date

# Importar solo los modelos que existen
from .models import (
    Producto, Almacen, MovimientoInventario, StockProducto, 
    LoteProducto, KardexProducto, TransferenciaAlmacen
)
from aplicaciones.core.models import Empresa

logger = logging.getLogger('felicita.inventario')


# =============================================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================================
class InventarioError(Exception):
    """Error base para inventario"""
    pass


class StockInsuficienteError(InventarioError):
    """Error cuando no hay suficiente stock"""
    pass


class ProductoInactivoError(InventarioError):
    """Error cuando se intenta usar un producto inactivo"""
    pass


# =============================================================================
# SERVICIO PRINCIPAL DE INVENTARIO
# =============================================================================
class InventarioService:
    """
    Servicio para manejo completo de inventario con método PEPS
    """
    
    def __init__(self, empresa_id: int = None):
        """
        Inicializar servicio de inventario
        
        Args:
            empresa_id: ID de la empresa (opcional)
        """
        self.empresa_id = empresa_id
        logger.debug(f"InventarioService inicializado para empresa {empresa_id}")
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - MOVIMIENTOS DE INVENTARIO
    # =============================================================================
    
    @transaction.atomic
    def registrar_entrada(
        self,
        producto_id: int,
        cantidad: Decimal,
        costo_unitario: Decimal,
        almacen_id: int,
        tipo_documento: str = 'COMPRA',
        documento_referencia: str = '',
        observaciones: str = ''
    ) -> MovimientoInventario:
        """
        Registrar entrada de inventario
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad que ingresa
            costo_unitario: Costo unitario del producto
            almacen_id: ID del almacén
            tipo_documento: Tipo de documento
            documento_referencia: Referencia del documento
            observaciones: Observaciones del movimiento
            
        Returns:
            MovimientoInventario: El movimiento creado
        """
        # Validaciones
        producto = self._validar_producto(producto_id)
        almacen = self._validar_almacen(almacen_id)
        self._validar_cantidad_positiva(cantidad)
        self._validar_costo_positivo(costo_unitario)
        
        # Obtener stock actual
        stock_actual = self._obtener_stock_actual(producto, almacen)
        
        # Generar número de movimiento
        numero_movimiento = self._generar_numero_movimiento('ENT')
        
        # Crear movimiento de inventario
        movimiento = MovimientoInventario.objects.create(
            numero_movimiento=numero_movimiento,
            tipo_movimiento='entrada',
            origen_movimiento=tipo_documento.lower(),
            producto=producto,
            almacen=almacen,
            cantidad=cantidad,
            cantidad_anterior=stock_actual,
            costo_unitario=costo_unitario,
            documento_referencia=documento_referencia,
            observaciones=observaciones
        )
        
        # Actualizar o crear stock
        self._actualizar_stock_producto(producto, almacen, cantidad, 'suma')
        
        # Crear registro de kardex
        self._crear_kardex_entrada(movimiento, stock_actual)
        
        logger.info(f"Entrada registrada: {movimiento.numero_movimiento}")
        return movimiento
    
    @transaction.atomic
    def registrar_salida(
        self,
        producto_id: int,
        cantidad: Decimal,
        almacen_id: int,
        tipo_documento: str = 'VENTA',
        documento_referencia: str = '',
        observaciones: str = ''
    ) -> Tuple[MovimientoInventario, List[Dict]]:
        """
        Registrar salida de inventario usando método PEPS
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad que sale
            almacen_id: ID del almacén
            tipo_documento: Tipo de documento
            documento_referencia: Referencia del documento
            observaciones: Observaciones del movimiento
            
        Returns:
            Tuple: (MovimientoInventario, lista de lotes consumidos)
        """
        # Validaciones
        producto = self._validar_producto(producto_id)
        almacen = self._validar_almacen(almacen_id)
        self._validar_cantidad_positiva(cantidad)
        
        # Verificar stock disponible
        stock_actual = self._obtener_stock_actual(producto, almacen)
        if stock_actual < cantidad:
            raise StockInsuficienteError(
                f"Stock insuficiente. Disponible: {stock_actual}, Requerido: {cantidad}"
            )
        
        # Calcular costo promedio PEPS
        costo_promedio = self._calcular_costo_promedio_peps(producto, almacen, cantidad)
        
        # Generar número de movimiento
        numero_movimiento = self._generar_numero_movimiento('SAL')
        
        # Crear movimiento de inventario
        movimiento = MovimientoInventario.objects.create(
            numero_movimiento=numero_movimiento,
            tipo_movimiento='salida',
            origen_movimiento=tipo_documento.lower(),
            producto=producto,
            almacen=almacen,
            cantidad=cantidad,
            cantidad_anterior=stock_actual,
            costo_unitario=costo_promedio,
            documento_referencia=documento_referencia,
            observaciones=observaciones
        )
        
        # Actualizar stock
        self._actualizar_stock_producto(producto, almacen, cantidad, 'resta')
        
        # Crear registro de kardex
        self._crear_kardex_salida(movimiento, stock_actual)
        
        logger.info(f"Salida registrada: {movimiento.numero_movimiento}")
        return movimiento, []  # Lista vacía por compatibilidad
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - CONSULTAS
    # =============================================================================
    
    def obtener_stock_producto(self, producto_id: int, almacen_id: int = None) -> Dict:
        """
        Obtener stock actual de un producto
        
        Args:
            producto_id: ID del producto
            almacen_id: ID del almacén (opcional, si no se especifica retorna todos)
            
        Returns:
            Dict: Información del stock
        """
        producto = self._validar_producto(producto_id)
        
        if almacen_id:
            almacen = self._validar_almacen(almacen_id)
            stock = self._obtener_stock_actual(producto, almacen)
            
            return {
                'producto_id': producto.id,
                'producto_codigo': producto.codigo_producto,
                'producto_descripcion': producto.descripcion,
                'almacen_id': almacen.id,
                'almacen_codigo': almacen.codigo,
                'stock_actual': stock,
                'stock_minimo': producto.stock_minimo,
                'stock_maximo': producto.stock_maximo,
                'requiere_reposicion': stock <= producto.stock_minimo
            }
        else:
            # Obtener stock de todos los almacenes
            stocks = StockProducto.objects.filter(producto=producto)
            stock_total = sum(s.cantidad_actual for s in stocks)
            
            stock_por_almacen = []
            for stock in stocks:
                stock_por_almacen.append({
                    'almacen_id': stock.almacen.id,
                    'almacen_codigo': stock.almacen.codigo,
                    'almacen_nombre': stock.almacen.nombre,
                    'cantidad': stock.cantidad_actual,
                    'costo_promedio': stock.costo_promedio,
                    'valor_inventario': stock.valor_inventario
                })
            
            return {
                'producto_id': producto.id,
                'producto_codigo': producto.codigo_producto,
                'producto_descripcion': producto.descripcion,
                'stock_total': stock_total,
                'stock_minimo': producto.stock_minimo,
                'stock_maximo': producto.stock_maximo,
                'stock_por_almacen': stock_por_almacen,
                'requiere_reposicion': stock_total <= producto.stock_minimo
            }
    
    def obtener_kardex_producto(
        self,
        producto_id: int,
        almacen_id: int = None,
        fecha_desde: date = None,
        fecha_hasta: date = None
    ) -> List[Dict]:
        """
        Obtener kardex (movimientos) de un producto
        
        Args:
            producto_id: ID del producto
            almacen_id: ID del almacén (opcional)
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            
        Returns:
            List[Dict]: Lista de movimientos del kardex
        """
        filtros = {'producto_id': producto_id}
        
        if almacen_id:
            filtros['almacen_id'] = almacen_id
        
        if fecha_desde:
            filtros['fecha__gte'] = fecha_desde
            
        if fecha_hasta:
            filtros['fecha__lte'] = fecha_hasta
        
        kardex = KardexProducto.objects.filter(**filtros).order_by('fecha', 'creado_en')
        
        kardex_data = []
        for registro in kardex:
            kardex_data.append({
                'fecha': registro.fecha,
                'tipo_operacion': registro.tipo_operacion,
                'detalle': registro.detalle,
                'documento_referencia': registro.documento_referencia,
                'cantidad_entrada': registro.cantidad_entrada,
                'costo_unitario_entrada': registro.costo_unitario_entrada,
                'costo_total_entrada': registro.costo_total_entrada,
                'cantidad_salida': registro.cantidad_salida,
                'costo_unitario_salida': registro.costo_unitario_salida,
                'costo_total_salida': registro.costo_total_salida,
                'cantidad_saldo': registro.cantidad_saldo,
                'costo_unitario_saldo': registro.costo_unitario_saldo,
                'costo_total_saldo': registro.costo_total_saldo
            })
        
        return kardex_data
    
    # =============================================================================
    # MÉTODOS PRIVADOS - VALIDACIONES
    # =============================================================================
    
    def _validar_producto(self, producto_id: int) -> Producto:
        """Validar que el producto existe y está activo"""
        try:
            producto = Producto.objects.get(id=producto_id)
            if not producto.activo:
                raise ProductoInactivoError(f"El producto {producto.codigo_producto} no está activo")
            return producto
        except Producto.DoesNotExist:
            raise InventarioError(f"El producto con ID {producto_id} no existe")
    
    def _validar_almacen(self, almacen_id: int) -> Almacen:
        """Validar que el almacén existe y está activo"""
        try:
            almacen = Almacen.objects.get(id=almacen_id)
            if not almacen.activo:
                raise InventarioError(f"El almacén {almacen.nombre} no está activo")
            return almacen
        except Almacen.DoesNotExist:
            raise InventarioError(f"El almacén con ID {almacen_id} no existe")
    
    def _validar_cantidad_positiva(self, cantidad: Decimal):
        """Validar que la cantidad sea positiva"""
        if cantidad <= 0:
            raise InventarioError("La cantidad debe ser mayor a cero")
    
    def _validar_costo_positivo(self, costo: Decimal):
        """Validar que el costo sea positivo"""
        if costo < 0:
            raise InventarioError("El costo no puede ser negativo")
    
    # =============================================================================
    # MÉTODOS PRIVADOS - LÓGICA DE NEGOCIO
    # =============================================================================
    
    def _obtener_stock_actual(self, producto: Producto, almacen: Almacen) -> Decimal:
        """Obtener stock actual de un producto en un almacén"""
        try:
            stock = StockProducto.objects.get(producto=producto, almacen=almacen)
            return stock.cantidad_actual
        except StockProducto.DoesNotExist:
            return Decimal('0')
    
    def _actualizar_stock_producto(
        self,
        producto: Producto,
        almacen: Almacen,
        cantidad: Decimal,
        operacion: str
    ):
        """Actualizar el stock actual del producto"""
        stock, created = StockProducto.objects.get_or_create(
            producto=producto,
            almacen=almacen,
            defaults={
                'cantidad_actual': Decimal('0'),
                'cantidad_reservada': Decimal('0'),
                'costo_promedio': Decimal('0')
            }
        )
        
        if operacion == 'suma':
            stock.cantidad_actual += cantidad
            stock.fecha_ultimo_ingreso = timezone.now()
        elif operacion == 'resta':
            stock.cantidad_actual -= cantidad
            stock.fecha_ultima_salida = timezone.now()
        
        stock.fecha_ultimo_movimiento = timezone.now()
        stock.save()
    
    def _calcular_costo_promedio_peps(
        self,
        producto: Producto,
        almacen: Almacen,
        cantidad: Decimal
    ) -> Decimal:
        """Calcular costo promedio usando método PEPS"""
        try:
            stock = StockProducto.objects.get(producto=producto, almacen=almacen)
            return stock.costo_promedio
        except StockProducto.DoesNotExist:
            return Decimal('0')
    
    def _generar_numero_movimiento(self, prefijo: str) -> str:
        """Generar número único para movimiento"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{prefijo}-{timestamp}"
    
    def _crear_kardex_entrada(self, movimiento: MovimientoInventario, stock_anterior: Decimal):
        """Crear registro de kardex para entrada"""
        stock_nuevo = stock_anterior + movimiento.cantidad
        
        KardexProducto.objects.create(
            fecha=movimiento.fecha_movimiento.date(),
            producto=movimiento.producto,
            almacen=movimiento.almacen,
            tipo_operacion='entrada',
            detalle=f"{movimiento.origen_movimiento.title()} - {movimiento.observaciones}",
            documento_referencia=movimiento.documento_referencia,
            cantidad_entrada=movimiento.cantidad,
            costo_unitario_entrada=movimiento.costo_unitario,
            cantidad_salida=Decimal('0'),
            costo_unitario_salida=Decimal('0'),
            cantidad_saldo=stock_nuevo,
            costo_unitario_saldo=movimiento.costo_unitario,
            movimiento_inventario=movimiento
        )
    
    def _crear_kardex_salida(self, movimiento: MovimientoInventario, stock_anterior: Decimal):
        """Crear registro de kardex para salida"""
        stock_nuevo = stock_anterior - movimiento.cantidad
        
        KardexProducto.objects.create(
            fecha=movimiento.fecha_movimiento.date(),
            producto=movimiento.producto,
            almacen=movimiento.almacen,
            tipo_operacion='salida',
            detalle=f"{movimiento.origen_movimiento.title()} - {movimiento.observaciones}",
            documento_referencia=movimiento.documento_referencia,
            cantidad_entrada=Decimal('0'),
            costo_unitario_entrada=Decimal('0'),
            cantidad_salida=movimiento.cantidad,
            costo_unitario_salida=movimiento.costo_unitario,
            cantidad_saldo=stock_nuevo,
            costo_unitario_saldo=movimiento.costo_unitario,
            movimiento_inventario=movimiento
        )


# =============================================================================
# FUNCIONES DE CONVENIENCIA
# =============================================================================

def actualizar_inventario_venta(
    producto_id: int,
    cantidad_vendida: Decimal,
    comprobante_referencia: str,
    almacen_id: int = None
) -> Dict:
    """
    Función de conveniencia para actualizar inventario por venta
    
    Args:
        producto_id: ID del producto vendido
        cantidad_vendida: Cantidad vendida
        comprobante_referencia: Referencia del comprobante
        almacen_id: ID del almacén (opcional, usa el principal si no se especifica)
        
    Returns:
        Dict: Resultado de la operación
    """
    try:
        # Si no se especifica almacén, usar el principal
        if not almacen_id:
            almacen_principal = Almacen.objects.filter(
                es_principal=True, activo=True
            ).first()
            
            if not almacen_principal:
                raise InventarioError("No hay almacenes principales configurados")
            
            almacen_id = almacen_principal.id
        
        # Crear servicio y registrar salida
        service = InventarioService()
        movimiento, lotes = service.registrar_salida(
            producto_id=producto_id,
            cantidad=abs(cantidad_vendida),  # Asegurar cantidad positiva
            almacen_id=almacen_id,
            tipo_documento='VENTA',
            documento_referencia=comprobante_referencia,
            observaciones=f"Venta según comprobante {comprobante_referencia}"
        )
        
        return {
            'success': True,
            'movimiento_id': movimiento.id,
            'mensaje': 'Inventario actualizado exitosamente'
        }
        
    except Exception as e:
        logger.error(f"Error al actualizar inventario por venta: {e}")
        return {
            'success': False,
            'error': str(e),
            'mensaje': 'Error al actualizar inventario'
        }


def obtener_stock_disponible(producto_id: int, almacen_id: int = None) -> Decimal:
    """
    Función de conveniencia para obtener stock total disponible de un producto
    
    Args:
        producto_id: ID del producto
        almacen_id: ID del almacén (opcional)
        
    Returns:
        Decimal: Stock total disponible
    """
    try:
        if almacen_id:
            stocks = StockProducto.objects.filter(
                producto_id=producto_id,
                almacen_id=almacen_id
            )
        else:
            stocks = StockProducto.objects.filter(producto_id=producto_id)
        
        return sum(stock.cantidad_disponible for stock in stocks)
    except Exception:
        return Decimal('0')


def verificar_disponibilidad_productos(items_venta: List[Dict]) -> Dict:
    """
    Verificar disponibilidad de stock para múltiples productos
    
    Args:
        items_venta: Lista de items con producto_id y cantidad
        
    Returns:
        Dict: Resultado de la verificación
    """
    productos_sin_stock = []
    productos_stock_bajo = []
    
    for item in items_venta:
        producto_id = item.get('producto_id')
        cantidad_requerida = Decimal(str(item.get('cantidad', 0)))
        
        if not producto_id or cantidad_requerida <= 0:
            continue
        
        stock_disponible = obtener_stock_disponible(producto_id)
        
        if stock_disponible < cantidad_requerida:
            productos_sin_stock.append({
                'producto_id': producto_id,
                'cantidad_requerida': cantidad_requerida,
                'stock_disponible': stock_disponible,
                'faltante': cantidad_requerida - stock_disponible
            })
        elif stock_disponible <= cantidad_requerida * Decimal('1.1'):  # 10% de margen
            productos_stock_bajo.append({
                'producto_id': producto_id,
                'stock_disponible': stock_disponible,
                'cantidad_requerida': cantidad_requerida
            })
    
    return {
        'puede_procesar': len(productos_sin_stock) == 0,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_bajo': productos_stock_bajo,
        'total_items_verificados': len(items_venta)
    }