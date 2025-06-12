"""
SERVICES DE INVENTARIO - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Servicios para manejo de inventario con método PEPS (Primeras Entradas, Primeras Salidas)
según normativa SUNAT
"""

from decimal import Decimal
from django.db import transaction, models
from django.utils import timezone
from django.conf import settings
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, date

from .models import (
    Producto, Almacen, MovimientoInventario, LoteInventario,
    StockProducto, AlertaStock, TransferenciaInventario,
    HistorialPrecio
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


class LoteNoEncontradoError(InventarioError):
    """Error cuando no se encuentra un lote específico"""
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
        observaciones: str = '',
        fecha_vencimiento: date = None,
        lote_proveedor: str = ''
    ) -> MovimientoInventario:
        """
        Registrar entrada de inventario
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad que ingresa
            costo_unitario: Costo unitario del producto
            almacen_id: ID del almacén
            tipo_documento: Tipo de documento (COMPRA, TRANSFERENCIA, AJUSTE, etc.)
            documento_referencia: Número de documento de referencia
            observaciones: Observaciones adicionales
            fecha_vencimiento: Fecha de vencimiento del lote (opcional)
            lote_proveedor: Número de lote del proveedor
            
        Returns:
            MovimientoInventario: El movimiento creado
        """
        logger.info(f"Registrando entrada - Producto: {producto_id}, Cantidad: {cantidad}")
        
        # Validaciones
        producto = self._validar_producto(producto_id)
        almacen = self._validar_almacen(almacen_id)
        self._validar_cantidad_positiva(cantidad)
        self._validar_costo_positivo(costo_unitario)
        
        # Crear lote de inventario
        lote = self._crear_lote_entrada(
            producto=producto,
            almacen=almacen,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            fecha_vencimiento=fecha_vencimiento,
            lote_proveedor=lote_proveedor
        )
        
        # Crear movimiento de inventario
        movimiento = MovimientoInventario.objects.create(
            producto=producto,
            almacen=almacen,
            tipo_movimiento='ENTRADA',
            cantidad=cantidad,
            cantidad_anterior=self._obtener_stock_actual(producto, almacen),
            costo_unitario=costo_unitario,
            costo_total=cantidad * costo_unitario,
            tipo_documento=tipo_documento,
            documento_referencia=documento_referencia,
            observaciones=observaciones,
            lote=lote,
            usuario_creacion_id=getattr(self, 'usuario_id', None)
        )
        
        # Actualizar stock del producto
        self._actualizar_stock_producto(producto, almacen, cantidad, 'suma')
        
        # Actualizar precio promedio
        self._actualizar_precio_promedio(producto, cantidad, costo_unitario)
        
        # Registrar historial de precio
        self._registrar_historial_precio(producto, costo_unitario, 'ENTRADA')
        
        logger.info(f"Entrada registrada exitosamente - Movimiento ID: {movimiento.id}")
        
        return movimiento
    
    @transaction.atomic
    def registrar_salida(
        self,
        producto_id: int,
        cantidad: Decimal,
        almacen_id: int,
        tipo_documento: str = 'VENTA',
        documento_referencia: str = '',
        observaciones: str = '',
        precio_venta: Decimal = None
    ) -> Tuple[MovimientoInventario, List[Dict]]:
        """
        Registrar salida de inventario usando método PEPS
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad que sale
            almacen_id: ID del almacén
            tipo_documento: Tipo de documento (VENTA, TRANSFERENCIA, AJUSTE, etc.)
            documento_referencia: Número de documento de referencia
            observaciones: Observaciones adicionales
            precio_venta: Precio de venta (opcional)
            
        Returns:
            Tuple[MovimientoInventario, List[Dict]]: El movimiento y detalle de lotes consumidos
        """
        logger.info(f"Registrando salida PEPS - Producto: {producto_id}, Cantidad: {cantidad}")
        
        # Validaciones
        producto = self._validar_producto(producto_id)
        almacen = self._validar_almacen(almacen_id)
        self._validar_cantidad_positiva(cantidad)
        
        # Verificar stock disponible
        stock_disponible = self._obtener_stock_actual(producto, almacen)
        if stock_disponible < cantidad:
            raise StockInsuficienteError(
                f"Stock insuficiente. Disponible: {stock_disponible}, Requerido: {cantidad}"
            )
        
        # Aplicar método PEPS para determinar lotes a consumir
        lotes_consumidos = self._aplicar_metodo_peps(producto, almacen, cantidad)
        
        # Calcular costo promedio de la salida
        costo_total_salida = sum(
            lote['cantidad_consumida'] * lote['costo_unitario'] 
            for lote in lotes_consumidos
        )
        costo_unitario_promedio = costo_total_salida / cantidad if cantidad > 0 else Decimal('0')
        
        # Crear movimiento de inventario
        movimiento = MovimientoInventario.objects.create(
            producto=producto,
            almacen=almacen,
            tipo_movimiento='SALIDA',
            cantidad=cantidad,
            cantidad_anterior=stock_disponible,
            costo_unitario=costo_unitario_promedio,
            costo_total=costo_total_salida,
            precio_venta=precio_venta,
            tipo_documento=tipo_documento,
            documento_referencia=documento_referencia,
            observaciones=observaciones,
            detalle_peps=lotes_consumidos,  # JSON con detalle de lotes
            usuario_creacion_id=getattr(self, 'usuario_id', None)
        )
        
        # Actualizar lotes consumidos
        self._actualizar_lotes_consumidos(lotes_consumidos)
        
        # Actualizar stock del producto
        self._actualizar_stock_producto(producto, almacen, cantidad, 'resta')
        
        # Verificar alertas de stock mínimo
        self._verificar_alerta_stock_minimo(producto, almacen)
        
        logger.info(f"Salida PEPS registrada exitosamente - Movimiento ID: {movimiento.id}")
        
        return movimiento, lotes_consumidos
    
    @transaction.atomic
    def transferir_productos(
        self,
        producto_id: int,
        cantidad: Decimal,
        almacen_origen_id: int,
        almacen_destino_id: int,
        documento_referencia: str = '',
        observaciones: str = ''
    ) -> TransferenciaInventario:
        """
        Transferir productos entre almacenes usando PEPS
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a transferir
            almacen_origen_id: ID del almacén origen
            almacen_destino_id: ID del almacén destino
            documento_referencia: Número de documento de referencia
            observaciones: Observaciones adicionales
            
        Returns:
            TransferenciaInventario: La transferencia creada
        """
        logger.info(f"Transfiriendo producto {producto_id} - Cantidad: {cantidad}")
        
        # Validaciones
        producto = self._validar_producto(producto_id)
        almacen_origen = self._validar_almacen(almacen_origen_id)
        almacen_destino = self._validar_almacen(almacen_destino_id)
        
        if almacen_origen_id == almacen_destino_id:
            raise InventarioError("El almacén origen y destino no pueden ser el mismo")
        
        # Registrar salida del almacén origen
        movimiento_salida, lotes_consumidos = self.registrar_salida(
            producto_id=producto_id,
            cantidad=cantidad,
            almacen_id=almacen_origen_id,
            tipo_documento='TRANSFERENCIA',
            documento_referencia=documento_referencia,
            observaciones=f"Transferencia a {almacen_destino.nombre}"
        )
        
        # Calcular costo promedio de los lotes transferidos
        costo_promedio = sum(
            lote['cantidad_consumida'] * lote['costo_unitario'] 
            for lote in lotes_consumidos
        ) / cantidad
        
        # Registrar entrada en el almacén destino
        movimiento_entrada = self.registrar_entrada(
            producto_id=producto_id,
            cantidad=cantidad,
            costo_unitario=costo_promedio,
            almacen_id=almacen_destino_id,
            tipo_documento='TRANSFERENCIA',
            documento_referencia=documento_referencia,
            observaciones=f"Transferencia desde {almacen_origen.nombre}"
        )
        
        # Crear registro de transferencia
        transferencia = TransferenciaInventario.objects.create(
            producto=producto,
            almacen_origen=almacen_origen,
            almacen_destino=almacen_destino,
            cantidad=cantidad,
            costo_unitario=costo_promedio,
            movimiento_salida=movimiento_salida,
            movimiento_entrada=movimiento_entrada,
            documento_referencia=documento_referencia,
            observaciones=observaciones,
            usuario_creacion_id=getattr(self, 'usuario_id', None)
        )
        
        logger.info(f"Transferencia completada exitosamente - ID: {transferencia.id}")
        
        return transferencia
    
    @transaction.atomic
    def ajustar_inventario(
        self,
        producto_id: int,
        almacen_id: int,
        cantidad_fisica: Decimal,
        motivo: str,
        observaciones: str = ''
    ) -> MovimientoInventario:
        """
        Realizar ajuste de inventario (positivo o negativo)
        
        Args:
            producto_id: ID del producto
            almacen_id: ID del almacén
            cantidad_fisica: Cantidad física real encontrada
            motivo: Motivo del ajuste
            observaciones: Observaciones adicionales
            
        Returns:
            MovimientoInventario: El movimiento de ajuste
        """
        logger.info(f"Ajustando inventario - Producto: {producto_id}, Cantidad física: {cantidad_fisica}")
        
        # Validaciones
        producto = self._validar_producto(producto_id)
        almacen = self._validar_almacen(almacen_id)
        
        # Obtener stock actual del sistema
        stock_sistema = self._obtener_stock_actual(producto, almacen)
        diferencia = cantidad_fisica - stock_sistema
        
        if diferencia == 0:
            logger.info("No hay diferencia en el inventario, no se requiere ajuste")
            return None
        
        # Determinar tipo de ajuste
        tipo_ajuste = 'AJUSTE_POSITIVO' if diferencia > 0 else 'AJUSTE_NEGATIVO'
        cantidad_ajuste = abs(diferencia)
        
        if diferencia > 0:
            # Ajuste positivo - agregar stock
            movimiento = self.registrar_entrada(
                producto_id=producto_id,
                cantidad=cantidad_ajuste,
                costo_unitario=producto.costo_promedio or Decimal('0'),
                almacen_id=almacen_id,
                tipo_documento=tipo_ajuste,
                documento_referencia=f"AJUSTE-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                observaciones=f"{motivo}. {observaciones}"
            )
        else:
            # Ajuste negativo - quitar stock
            movimiento, _ = self.registrar_salida(
                producto_id=producto_id,
                cantidad=cantidad_ajuste,
                almacen_id=almacen_id,
                tipo_documento=tipo_ajuste,
                documento_referencia=f"AJUSTE-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                observaciones=f"{motivo}. {observaciones}"
            )
        
        logger.info(f"Ajuste de inventario completado - Diferencia: {diferencia}")
        
        return movimiento
    
    # =============================================================================
    # MÉTODOS DE CONSULTA
    # =============================================================================
    
    def obtener_stock_producto(self, producto_id: int, almacen_id: int = None) -> Dict:
        """
        Obtener stock actual de un producto
        
        Args:
            producto_id: ID del producto
            almacen_id: ID del almacén (opcional, si no se especifica trae todos)
            
        Returns:
            Dict: Información de stock
        """
        producto = self._validar_producto(producto_id)
        
        if almacen_id:
            almacen = self._validar_almacen(almacen_id)
            stock = self._obtener_stock_actual(producto, almacen)
            
            return {
                'producto_id': producto_id,
                'producto_codigo': producto.codigo_producto,
                'producto_descripcion': producto.descripcion,
                'almacen_id': almacen_id,
                'almacen_nombre': almacen.nombre,
                'stock_actual': stock,
                'stock_minimo': producto.stock_minimo,
                'stock_maximo': producto.stock_maximo,
                'requiere_reposicion': stock <= producto.stock_minimo
            }
        else:
            # Obtener stock de todos los almacenes
            stocks = StockProducto.objects.filter(producto=producto)
            
            stock_total = sum(stock.cantidad_actual for stock in stocks)
            
            stock_por_almacen = []
            for stock in stocks:
                stock_por_almacen.append({
                    'almacen_id': stock.almacen.id,
                    'almacen_nombre': stock.almacen.nombre,
                    'stock_actual': stock.cantidad_actual,
                    'requiere_reposicion': stock.cantidad_actual <= producto.stock_minimo
                })
            
            return {
                'producto_id': producto_id,
                'producto_codigo': producto.codigo_producto,
                'producto_descripcion': producto.descripcion,
                'stock_total': stock_total,
                'stock_minimo': producto.stock_minimo,
                'stock_maximo': producto.stock_maximo,
                'stock_por_almacen': stock_por_almacen,
                'requiere_reposicion': stock_total <= producto.stock_minimo
            }
    
    def obtener_lotes_disponibles(self, producto_id: int, almacen_id: int) -> List[Dict]:
        """
        Obtener lotes disponibles de un producto ordenados por PEPS
        
        Args:
            producto_id: ID del producto
            almacen_id: ID del almacén
            
        Returns:
            List[Dict]: Lista de lotes disponibles
        """
        producto = self._validar_producto(producto_id)
        almacen = self._validar_almacen(almacen_id)
        
        lotes = LoteInventario.objects.filter(
            producto=producto,
            almacen=almacen,
            cantidad_disponible__gt=0
        ).order_by('fecha_ingreso', 'id')
        
        lotes_data = []
        for lote in lotes:
            lotes_data.append({
                'id': lote.id,
                'numero_lote': lote.numero_lote,
                'fecha_ingreso': lote.fecha_ingreso,
                'fecha_vencimiento': lote.fecha_vencimiento,
                'cantidad_inicial': lote.cantidad_inicial,
                'cantidad_disponible': lote.cantidad_disponible,
                'costo_unitario': lote.costo_unitario,
                'lote_proveedor': lote.lote_proveedor,
                'dias_desde_ingreso': (date.today() - lote.fecha_ingreso).days
            })
        
        return lotes_data
    
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
        producto = self._validar_producto(producto_id)
        
        # Construir filtros
        filtros = {'producto': producto}
        
        if almacen_id:
            almacen = self._validar_almacen(almacen_id)
            filtros['almacen'] = almacen
        
        if fecha_desde:
            filtros['created_at__date__gte'] = fecha_desde
        
        if fecha_hasta:
            filtros['created_at__date__lte'] = fecha_hasta
        
        # Obtener movimientos ordenados por fecha
        movimientos = MovimientoInventario.objects.filter(
            **filtros
        ).select_related('almacen', 'lote').order_by('created_at')
        
        kardex = []
        stock_acumulado = Decimal('0')
        
        for movimiento in movimientos:
            if movimiento.tipo_movimiento in ['ENTRADA', 'AJUSTE_POSITIVO']:
                stock_acumulado += movimiento.cantidad
            else:
                stock_acumulado -= movimiento.cantidad
            
            kardex.append({
                'fecha': movimiento.created_at.date(),
                'hora': movimiento.created_at.time(),
                'tipo_movimiento': movimiento.tipo_movimiento,
                'tipo_documento': movimiento.tipo_documento,
                'documento_referencia': movimiento.documento_referencia,
                'cantidad_entrada': movimiento.cantidad if movimiento.tipo_movimiento in ['ENTRADA', 'AJUSTE_POSITIVO'] else None,
                'cantidad_salida': movimiento.cantidad if movimiento.tipo_movimiento in ['SALIDA', 'AJUSTE_NEGATIVO'] else None,
                'stock_anterior': movimiento.cantidad_anterior,
                'stock_actual': stock_acumulado,
                'costo_unitario': movimiento.costo_unitario,
                'costo_total': movimiento.costo_total,
                'precio_venta': movimiento.precio_venta,
                'almacen': movimiento.almacen.nombre,
                'observaciones': movimiento.observaciones,
                'lote': movimiento.lote.numero_lote if movimiento.lote else None
            })
        
        return kardex
    
    def obtener_productos_stock_minimo(self, almacen_id: int = None) -> List[Dict]:
        """
        Obtener productos que están en stock mínimo o por debajo
        
        Args:
            almacen_id: ID del almacén (opcional)
            
        Returns:
            List[Dict]: Lista de productos con stock bajo
        """
        # Construir consulta
        if almacen_id:
            almacen = self._validar_almacen(almacen_id)
            stocks = StockProducto.objects.filter(
                almacen=almacen
            ).select_related('producto', 'almacen')
        else:
            stocks = StockProducto.objects.all().select_related('producto', 'almacen')
        
        productos_bajo_stock = []
        
        for stock in stocks:
            if stock.cantidad_actual <= stock.producto.stock_minimo:
                productos_bajo_stock.append({
                    'producto_id': stock.producto.id,
                    'producto_codigo': stock.producto.codigo_producto,
                    'producto_descripcion': stock.producto.descripcion,
                    'almacen_id': stock.almacen.id,
                    'almacen_nombre': stock.almacen.nombre,
                    'stock_actual': stock.cantidad_actual,
                    'stock_minimo': stock.producto.stock_minimo,
                    'stock_maximo': stock.producto.stock_maximo,
                    'diferencia': stock.producto.stock_minimo - stock.cantidad_actual,
                    'sugerido_compra': stock.producto.stock_maximo - stock.cantidad_actual,
                    'dias_sin_stock': self._calcular_dias_sin_stock(stock.producto)
                })
        
        # Ordenar por criticidad (menor stock primero)
        productos_bajo_stock.sort(key=lambda x: x['stock_actual'])
        
        return productos_bajo_stock
    
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
    
    def _crear_lote_entrada(
        self,
        producto: Producto,
        almacen: Almacen,
        cantidad: Decimal,
        costo_unitario: Decimal,
        fecha_vencimiento: date = None,
        lote_proveedor: str = ''
    ) -> LoteInventario:
        """Crear nuevo lote de entrada"""
        numero_lote = self._generar_numero_lote(producto, almacen)
        
        lote = LoteInventario.objects.create(
            producto=producto,
            almacen=almacen,
            numero_lote=numero_lote,
            cantidad_inicial=cantidad,
            cantidad_disponible=cantidad,
            costo_unitario=costo_unitario,
            fecha_ingreso=date.today(),
            fecha_vencimiento=fecha_vencimiento,
            lote_proveedor=lote_proveedor
        )
        
        return lote
    
    def _generar_numero_lote(self, producto: Producto, almacen: Almacen) -> str:
        """Generar número de lote único"""
        fecha_str = date.today().strftime('%Y%m%d')
        
        # Buscar el último lote del día para este producto
        ultimo_lote = LoteInventario.objects.filter(
            producto=producto,
            numero_lote__startswith=f"{producto.codigo_producto}-{fecha_str}"
        ).order_by('-numero_lote').first()
        
        if ultimo_lote:
            # Extraer el consecutivo del último lote
            try:
                consecutivo = int(ultimo_lote.numero_lote.split('-')[-1]) + 1
            except (ValueError, IndexError):
                consecutivo = 1
        else:
            consecutivo = 1
        
        return f"{producto.codigo_producto}-{fecha_str}-{consecutivo:03d}"
    
    def _aplicar_metodo_peps(
        self,
        producto: Producto,
        almacen: Almacen,
        cantidad_requerida: Decimal
    ) -> List[Dict]:
        """
        Aplicar método PEPS para determinar qué lotes consumir
        
        Returns:
            List[Dict]: Lista de lotes con cantidad a consumir
        """
        lotes_disponibles = LoteInventario.objects.filter(
            producto=producto,
            almacen=almacen,
            cantidad_disponible__gt=0
        ).order_by('fecha_ingreso', 'id')
        
        lotes_consumidos = []
        cantidad_pendiente = cantidad_requerida
        
        for lote in lotes_disponibles:
            if cantidad_pendiente <= 0:
                break
            
            cantidad_a_consumir = min(lote.cantidad_disponible, cantidad_pendiente)
            
            lotes_consumidos.append({
                'lote_id': lote.id,
                'numero_lote': lote.numero_lote,
                'cantidad_disponible': lote.cantidad_disponible,
                'cantidad_consumida': cantidad_a_consumir,
                'costo_unitario': lote.costo_unitario,
                'fecha_ingreso': lote.fecha_ingreso.isoformat()
            })
            
            cantidad_pendiente -= cantidad_a_consumir
        
        if cantidad_pendiente > 0:
            raise StockInsuficienteError(
                f"Stock insuficiente. Faltan {cantidad_pendiente} unidades"
            )
        
        return lotes_consumidos
    
    def _actualizar_lotes_consumidos(self, lotes_consumidos: List[Dict]):
        """Actualizar las cantidades disponibles de los lotes consumidos"""
        for lote_data in lotes_consumidos:
            lote = LoteInventario.objects.get(id=lote_data['lote_id'])
            lote.cantidad_disponible -= lote_data['cantidad_consumida']
            lote.save()
    
    def _obtener_stock_actual(self, producto: Producto, almacen: Almacen) -> Decimal:
        """Obtener stock actual de un producto en un almacén"""
        stock, created = StockProducto.objects.get_or_create(
            producto=producto,
            almacen=almacen,
            defaults={'cantidad_actual': Decimal('0')}
        )
        return stock.cantidad_actual
    
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
            defaults={'cantidad_actual': Decimal('0')}
        )
        
        if operacion == 'suma':
            stock.cantidad_actual += cantidad
        elif operacion == 'resta':
            stock.cantidad_actual -= cantidad
        
        stock.fecha_ultimo_movimiento = timezone.now()
        stock.save()
    
    def _actualizar_precio_promedio(
        self,
        producto: Producto,
        cantidad_nueva: Decimal,
        costo_nuevo: Decimal
    ):
        """Actualizar precio promedio del producto"""
        stock_total = sum(
            StockProducto.objects.filter(producto=producto).values_list('cantidad_actual', flat=True)
        )
        
        if stock_total > 0:
            # Calcular nuevo precio promedio ponderado
            valor_anterior = (stock_total - cantidad_nueva) * (producto.costo_promedio or Decimal('0'))
            valor_nuevo = cantidad_nueva * costo_nuevo
            
            producto.costo_promedio = (valor_anterior + valor_nuevo) / stock_total
            producto.save()
    
    def _registrar_historial_precio(
        self,
        producto: Producto,
        precio: Decimal,
        tipo_movimiento: str
    ):
        """Registrar historial de precios"""
        HistorialPrecio.objects.create(
            producto=producto,
            precio=precio,
            tipo_movimiento=tipo_movimiento,
            fecha_registro=timezone.now()
        )
    
    def _verificar_alerta_stock_minimo(self, producto: Producto, almacen: Almacen):
        """Verificar y crear alerta si el stock está por debajo del mínimo"""
        stock_actual = self._obtener_stock_actual(producto, almacen)
        
        if stock_actual <= producto.stock_minimo:
            # Verificar si ya existe una alerta activa
            alerta_existente = AlertaStock.objects.filter(
                producto=producto,
                almacen=almacen,
                activa=True
            ).first()
            
            if not alerta_existente:
                AlertaStock.objects.create(
                    producto=producto,
                    almacen=almacen,
                    tipo_alerta='STOCK_MINIMO',
                    mensaje=f"Stock bajo para {producto.descripcion} en {almacen.nombre}",
                    stock_actual=stock_actual,
                    stock_minimo=producto.stock_minimo,
                    activa=True
                )
    
    def _calcular_dias_sin_stock(self, producto: Producto) -> int:
        """Calcular días estimados sin stock basado en consumo promedio"""
        # Obtener movimientos de salida de los últimos 30 días
        fecha_desde = date.today() - timedelta(days=30)
        
        salidas = MovimientoInventario.objects.filter(
            producto=producto,
            tipo_movimiento__in=['SALIDA', 'AJUSTE_NEGATIVO'],
            created_at__date__gte=fecha_desde
        ).aggregate(
            total_salidas=models.Sum('cantidad')
        )
        
        total_salidas = salidas.get('total_salidas') or Decimal('0')
        
        if total_salidas > 0:
            consumo_diario = total_salidas / 30
            stock_actual = sum(
                StockProducto.objects.filter(producto=producto).values_list('cantidad_actual', flat=True)
            )
            
            if consumo_diario > 0:
                return int(stock_actual / consumo_diario)
        
        return 999  # Stock suficiente por mucho tiempo


# =============================================================================
# FUNCIONES DE CONVENIENCIA
# =============================================================================
def actualizar_inventario_venta(producto_id: int, cantidad_vendida: Decimal, comprobante_referencia: str = '') -> Dict:
    """
    Función de conveniencia para actualizar inventario por venta
    
    Args:
        producto_id: ID del producto vendido
        cantidad_vendida: Cantidad vendida
        comprobante_referencia: Referencia del comprobante de venta
        
    Returns:
        Dict: Resultado de la operación
    """
    try:
        # Obtener almacén principal (se puede configurar)
        almacen_principal = Almacen.objects.filter(es_principal=True).first()
        if not almacen_principal:
            almacen_principal = Almacen.objects.first()
        
        if not almacen_principal:
            raise InventarioError("No hay almacenes configurados")
        
        service = InventarioService()
        movimiento, lotes = service.registrar_salida(
            producto_id=producto_id,
            cantidad=cantidad_vendida,
            almacen_id=almacen_principal.id,
            tipo_documento='VENTA',
            documento_referencia=comprobante_referencia,
            observaciones=f"Venta según comprobante {comprobante_referencia}"
        )
        
        return {
            'success': True,
            'movimiento_id': movimiento.id,
            'lotes_consumidos': lotes,
            'mensaje': 'Inventario actualizado exitosamente'
        }
        
    except Exception as e:
        logger.error(f"Error al actualizar inventario por venta: {e}")
        return {
            'success': False,
            'error': str(e),
            'mensaje': 'Error al actualizar inventario'
        }


def obtener_stock_disponible(producto_id: int) -> Decimal:
    """
    Función de conveniencia para obtener stock total disponible de un producto
    
    Args:
        producto_id: ID del producto
        
    Returns:
        Decimal: Stock total disponible
    """
    try:
        stocks = StockProducto.objects.filter(producto_id=producto_id)
        return sum(stock.cantidad_actual for stock in stocks)
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
        
        stock_disponible = obtener_stock_disponible(producto_id)
        
        if stock_disponible < cantidad_requerida:
            try:
                producto = Producto.objects.get(id=producto_id)
                productos_sin_stock.append({
                    'producto_id': producto_id,
                    'codigo': producto.codigo_producto,
                    'descripcion': producto.descripcion,
                    'cantidad_requerida': cantidad_requerida,
                    'stock_disponible': stock_disponible,
                    'faltante': cantidad_requerida - stock_disponible
                })
            except Producto.DoesNotExist:
                productos_sin_stock.append({
                    'producto_id': producto_id,
                    'error': 'Producto no encontrado'
                })
        elif stock_disponible <= Decimal(str(item.get('stock_minimo', 0))):
            try:
                producto = Producto.objects.get(id=producto_id)
                productos_stock_bajo.append({
                    'producto_id': producto_id,
                    'codigo': producto.codigo_producto,
                    'descripcion': producto.descripcion,
                    'stock_disponible': stock_disponible,
                    'stock_minimo': producto.stock_minimo
                })
            except Producto.DoesNotExist:
                pass
    
    return {
        'disponible': len(productos_sin_stock) == 0,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_bajo': productos_stock_bajo,
        'mensaje': 'Stock suficiente' if len(productos_sin_stock) == 0 else 'Stock insuficiente para algunos productos'
    }