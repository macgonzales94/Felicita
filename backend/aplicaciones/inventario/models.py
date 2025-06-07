"""
MODELOS INVENTARIO - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Modelos para control de inventarios con método PEPS (obligatorio SUNAT):
- Almacen
- MovimientoInventario
- KardexProducto
- StockProducto
- TransferenciaAlmacen
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from aplicaciones.core.models import ModeloBase, Producto, Empresa
from aplicaciones.usuarios.models import Usuario
import uuid

# =============================================================================
# MODELO ALMACÉN
# =============================================================================
class Almacen(ModeloBase):
    """
    Almacenes para control de inventarios
    """
    
    TIPO_ALMACEN_CHOICES = [
        ('principal', 'Almacén Principal'),
        ('sucursal', 'Almacén de Sucursal'),
        ('deposito', 'Depósito'),
        ('transito', 'En Tránsito'),
        ('consignacion', 'Consignación'),
        ('virtual', 'Virtual'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='almacenes',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=20,
        verbose_name='Código del Almacén'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Almacén'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_almacen = models.CharField(
        max_length=20,
        choices=TIPO_ALMACEN_CHOICES,
        default='principal',
        verbose_name='Tipo de Almacén'
    )
    
    # Ubicación física
    direccion = models.TextField(
        verbose_name='Dirección'
    )
    
    ubigeo = models.CharField(
        max_length=6,
        blank=True,
        verbose_name='Ubigeo'
    )
    
    distrito = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Distrito'
    )
    
    # Responsable
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='almacenes_responsable',
        verbose_name='Responsable'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    
    # Configuración
    es_principal = models.BooleanField(
        default=False,
        verbose_name='Es Almacén Principal'
    )
    
    permite_ventas = models.BooleanField(
        default=True,
        verbose_name='Permite Ventas'
    )
    
    permite_compras = models.BooleanField(
        default=True,
        verbose_name='Permite Compras'
    )
    
    controla_lotes = models.BooleanField(
        default=False,
        verbose_name='Controla Lotes'
    )
    
    controla_vencimientos = models.BooleanField(
        default=False,
        verbose_name='Controla Vencimientos'
    )
    
    class Meta:
        db_table = 'inventario_almacen'
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['es_principal']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# =============================================================================
# MODELO LOTE PRODUCTO
# =============================================================================
class LoteProducto(ModeloBase):
    """
    Lotes de productos para control de vencimientos y trazabilidad
    """
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='lotes',
        verbose_name='Producto'
    )
    
    numero_lote = models.CharField(
        max_length=50,
        verbose_name='Número de Lote'
    )
    
    fecha_fabricacion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Fabricación'
    )
    
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Vencimiento'
    )
    
    proveedor_lote = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Proveedor del Lote'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    class Meta:
        db_table = 'inventario_lote_producto'
        verbose_name = 'Lote de Producto'
        verbose_name_plural = 'Lotes de Productos'
        unique_together = ['producto', 'numero_lote']
        indexes = [
            models.Index(fields=['numero_lote']),
            models.Index(fields=['fecha_vencimiento']),
        ]
    
    def __str__(self):
        return f"{self.producto.codigo} - Lote {self.numero_lote}"
    
    def esta_vencido(self):
        """Verifica si el lote está vencido"""
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.now().date()
        return False
    
    def dias_para_vencer(self):
        """Calcula los días restantes para vencer"""
        if self.fecha_vencimiento:
            delta = self.fecha_vencimiento - timezone.now().date()
            return delta.days
        return None

# =============================================================================
# MODELO MOVIMIENTO INVENTARIO
# =============================================================================
class MovimientoInventario(ModeloBase):
    """
    Registro de todos los movimientos de inventario para control PEPS
    """
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('transferencia_in', 'Transferencia Entrada'),
        ('transferencia_out', 'Transferencia Salida'),
        ('ajuste_positivo', 'Ajuste Positivo'),
        ('ajuste_negativo', 'Ajuste Negativo'),
        ('inicial', 'Inventario Inicial'),
    ]
    
    ORIGEN_MOVIMIENTO_CHOICES = [
        ('compra', 'Compra'),
        ('venta', 'Venta'),
        ('transferencia', 'Transferencia'),
        ('ajuste', 'Ajuste de Inventario'),
        ('devolucion_compra', 'Devolución de Compra'),
        ('devolucion_venta', 'Devolución de Venta'),
        ('merma', 'Merma'),
        ('promocion', 'Promoción'),
        ('inicial', 'Inventario Inicial'),
        ('produccion', 'Producción'),
    ]
    
    # Información básica
    numero_movimiento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Movimiento'
    )
    
    fecha_movimiento = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Movimiento'
    )
    
    tipo_movimiento = models.CharField(
        max_length=20,
        choices=TIPO_MOVIMIENTO_CHOICES,
        verbose_name='Tipo de Movimiento'
    )
    
    origen_movimiento = models.CharField(
        max_length=20,
        choices=ORIGEN_MOVIMIENTO_CHOICES,
        verbose_name='Origen del Movimiento'
    )
    
    # Producto y almacén
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos_inventario',
        verbose_name='Producto'
    )
    
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Almacén'
    )
    
    lote = models.ForeignKey(
        LoteProducto,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Lote'
    )
    
    # Cantidades
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Cantidad'
    )
    
    cantidad_anterior = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Cantidad Anterior'
    )
    
    cantidad_nueva = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Cantidad Nueva'
    )
    
    # Costos (para método PEPS)
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Unitario'
    )
    
    costo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo Total'
    )
    
    costo_promedio_anterior = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Promedio Anterior'
    )
    
    costo_promedio_nuevo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Promedio Nuevo'
    )
    
    # Documento de referencia
    tipo_documento_referencia = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Tipo de Documento de Referencia'
    )
    
    numero_documento_referencia = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Documento de Referencia'
    )
    
    # Usuario y observaciones
    usuario_movimiento = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='movimientos_inventario',
        verbose_name='Usuario que registra el movimiento'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    # Control
    procesado = models.BooleanField(
        default=False,
        verbose_name='Procesado'
    )
    
    fecha_procesado = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Procesamiento'
    )
    
    class Meta:
        db_table = 'inventario_movimiento'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        indexes = [
            models.Index(fields=['numero_movimiento']),
            models.Index(fields=['fecha_movimiento']),
            models.Index(fields=['producto', 'almacen']),
            models.Index(fields=['tipo_movimiento']),
            models.Index(fields=['origen_movimiento']),
            models.Index(fields=['procesado']),
        ]
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.numero_movimiento} - {self.producto.codigo} - {self.tipo_movimiento}"
    
    def save(self, *args, **kwargs):
        """Calcular valores automáticamente"""
        # Calcular costo total
        self.costo_total = self.cantidad * self.costo_unitario
        
        # Determinar nueva cantidad según tipo de movimiento
        if self.tipo_movimiento in ['entrada', 'transferencia_in', 'ajuste_positivo', 'inicial']:
            self.cantidad_nueva = self.cantidad_anterior + abs(self.cantidad)
        else:  # salida, transferencia_out, ajuste_negativo
            self.cantidad_nueva = self.cantidad_anterior - abs(self.cantidad)
        
        super().save(*args, **kwargs)

# =============================================================================
# MODELO STOCK PRODUCTO
# =============================================================================
class StockProducto(ModeloBase):
    """
    Stock actual de productos por almacén (tabla de resumen)
    """
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='Producto'
    )
    
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='Almacén'
    )
    
    lote = models.ForeignKey(
        LoteProducto,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Lote'
    )
    
    # Cantidades
    cantidad_actual = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Cantidad Actual'
    )
    
    cantidad_reservada = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Cantidad Reservada'
    )
    
    cantidad_disponible = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Cantidad Disponible'
    )
    
    # Costos PEPS
    costo_promedio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Promedio'
    )
    
    valor_inventario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor del Inventario'
    )
    
    # Control de fechas
    fecha_ultimo_movimiento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha Último Movimiento'
    )
    
    fecha_ultimo_ingreso = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha Último Ingreso'
    )
    
    fecha_ultima_salida = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha Última Salida'
    )
    
    class Meta:
        db_table = 'inventario_stock_producto'
        verbose_name = 'Stock de Producto'
        verbose_name_plural = 'Stock de Productos'
        unique_together = ['producto', 'almacen', 'lote']
        indexes = [
            models.Index(fields=['producto', 'almacen']),
            models.Index(fields=['cantidad_actual']),
            models.Index(fields=['cantidad_disponible']),
        ]
    
    def __str__(self):
        lote_info = f" - Lote {self.lote.numero_lote}" if self.lote else ""
        return f"{self.producto.codigo} - {self.almacen.codigo}{lote_info}: {self.cantidad_actual}"
    
    def save(self, *args, **kwargs):
        """Calcular valores automáticamente"""
        # Calcular cantidad disponible
        self.cantidad_disponible = self.cantidad_actual - self.cantidad_reservada
        
        # Calcular valor del inventario
        self.valor_inventario = self.cantidad_actual * self.costo_promedio
        
        super().save(*args, **kwargs)
    
    def tiene_stock_suficiente(self, cantidad_requerida):
        """Verifica si hay stock suficiente disponible"""
        return self.cantidad_disponible >= cantidad_requerida
    
    def reservar_stock(self, cantidad):
        """Reserva una cantidad de stock"""
        if self.cantidad_disponible >= cantidad:
            self.cantidad_reservada += cantidad
            self.save(update_fields=['cantidad_reservada'])
            return True
        return False
    
    def liberar_reserva(self, cantidad):
        """Libera una cantidad de stock reservado"""
        self.cantidad_reservada = max(0, self.cantidad_reservada - cantidad)
        self.save(update_fields=['cantidad_reservada'])

# =============================================================================
# MODELO KARDEX PRODUCTO (RESUMEN VALORIZADO PEPS)
# =============================================================================
class KardexProducto(ModeloBase):
    """
    Kardex valorizado de productos según método PEPS (requerido por SUNAT)
    """
    
    TIPO_OPERACION_CHOICES = [
        ('inicial', 'Inventario Inicial'),
        ('compra', 'Compra'),
        ('venta', 'Venta'),
        ('transferencia', 'Transferencia'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
        ('merma', 'Merma'),
        ('transformacion', 'Transformación'),
    ]
    
    fecha = models.DateField(
        verbose_name='Fecha'
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='kardex',
        verbose_name='Producto'
    )
    
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.CASCADE,
        related_name='kardex',
        verbose_name='Almacén'
    )
    
    # Operación
    tipo_operacion = models.CharField(
        max_length=20,
        choices=TIPO_OPERACION_CHOICES,
        verbose_name='Tipo de Operación'
    )
    
    numero_documento = models.CharField(
        max_length=50,
        verbose_name='Número de Documento'
    )
    
    # Entradas
    cantidad_entrada = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Cantidad Entrada'
    )
    
    costo_unitario_entrada = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Unitario Entrada'
    )
    
    costo_total_entrada = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo Total Entrada'
    )
    
    # Salidas
    cantidad_salida = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Cantidad Salida'
    )
    
    costo_unitario_salida = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Unitario Salida'
    )
    
    costo_total_salida = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo Total Salida'
    )
    
    # Saldos
    cantidad_saldo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Cantidad Saldo'
    )
    
    costo_unitario_saldo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Unitario Saldo'
    )
    
    costo_total_saldo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo Total Saldo'
    )
    
    # Referencias
    movimiento_inventario = models.ForeignKey(
        MovimientoInventario,
        on_delete=models.CASCADE,
        related_name='kardex_generado',
        verbose_name='Movimiento de Inventario'
    )
    
    class Meta:
        db_table = 'inventario_kardex_producto'
        verbose_name = 'Kardex de Producto'
        verbose_name_plural = 'Kardex de Productos'
        indexes = [
            models.Index(fields=['fecha', 'producto', 'almacen']),
            models.Index(fields=['producto', 'almacen', 'fecha']),
            models.Index(fields=['tipo_operacion']),
        ]
        ordering = ['fecha', 'creado_en']
    
    def __str__(self):
        return f"Kardex {self.producto.codigo} - {self.fecha} - {self.tipo_operacion}"
    
    def save(self, *args, **kwargs):
        """Calcular valores automáticamente"""
        # Calcular costos totales
        self.costo_total_entrada = self.cantidad_entrada * self.costo_unitario_entrada
        self.costo_total_salida = self.cantidad_salida * self.costo_unitario_salida
        self.costo_total_saldo = self.cantidad_saldo * self.costo_unitario_saldo
        
        super().save(*args, **kwargs)

# =============================================================================
# MODELO TRANSFERENCIA ALMACÉN
# =============================================================================
class TransferenciaAlmacen(ModeloBase):
    """
    Transferencias de productos entre almacenes
    """
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_transito', 'En Tránsito'),
        ('recibida', 'Recibida'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    ]
    
    numero_transferencia = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Transferencia'
    )
    
    fecha_transferencia = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Transferencia'
    )
    
    # Almacenes
    almacen_origen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='transferencias_salida',
        verbose_name='Almacén de Origen'
    )
    
    almacen_destino = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='transferencias_entrada',
        verbose_name='Almacén de Destino'
    )
    
    # Responsables
    usuario_envia = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='transferencias_enviadas',
        verbose_name='Usuario que Envía'
    )
    
    usuario_recibe = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='transferencias_recibidas',
        verbose_name='Usuario que Recibe'
    )
    
    # Estado y fechas
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    
    fecha_envio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Envío'
    )
    
    fecha_recepcion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Recepción'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    class Meta:
        db_table = 'inventario_transferencia_almacen'
        verbose_name = 'Transferencia entre Almacenes'
        verbose_name_plural = 'Transferencias entre Almacenes'
        indexes = [
            models.Index(fields=['numero_transferencia']),
            models.Index(fields=['fecha_transferencia']),
            models.Index(fields=['estado']),
            models.Index(fields=['almacen_origen']),
            models.Index(fields=['almacen_destino']),
        ]
    
    def __str__(self):
        return f"Transferencia {self.numero_transferencia} - {self.almacen_origen.codigo} → {self.almacen_destino.codigo}"
    
    def confirmar_envio(self, usuario):
        """Confirma el envío de la transferencia"""
        self.estado = 'en_transito'
        self.fecha_envio = timezone.now()
        self.usuario_envia = usuario
        self.save(update_fields=['estado', 'fecha_envio', 'usuario_envia'])
    
    def confirmar_recepcion(self, usuario):
        """Confirma la recepción de la transferencia"""
        self.estado = 'recibida'
        self.fecha_recepcion = timezone.now()
        self.usuario_recibe = usuario
        self.save(update_fields=['estado', 'fecha_recepcion', 'usuario_recibe'])

# =============================================================================
# MODELO DETALLE TRANSFERENCIA ALMACÉN
# =============================================================================
class DetalleTransferenciaAlmacen(ModeloBase):
    """
    Detalle de productos en transferencias entre almacenes
    """
    
    transferencia = models.ForeignKey(
        TransferenciaAlmacen,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Transferencia'
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name='Producto'
    )
    
    lote = models.ForeignKey(
        LoteProducto,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Lote'
    )
    
    cantidad_enviada = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Cantidad Enviada'
    )
    
    cantidad_recibida = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Cantidad Recibida'
    )
    
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Costo Unitario'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones del Item'
    )
    
    class Meta:
        db_table = 'inventario_detalle_transferencia_almacen'
        verbose_name = 'Detalle de Transferencia'
        verbose_name_plural = 'Detalles de Transferencias'
        unique_together = ['transferencia', 'producto', 'lote']
    
    def __str__(self):
        return f"{self.transferencia.numero_transferencia} - {self.producto.codigo}"