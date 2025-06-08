"""
MODELOS PUNTO DE VENTA - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Modelos para el módulo de punto de venta (POS):
- PuntoVenta
- SesionCaja
- Venta
- VentaItem
- MetodoPago
- PagoVenta
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from aplicaciones.core.models import ModeloBase, Cliente, Producto, Empresa
from aplicaciones.usuarios.models import Usuario
from aplicaciones.inventario.models import Almacen
import uuid

# =============================================================================
# MODELO PUNTO DE VENTA
# =============================================================================
class PuntoVenta(ModeloBase):
    """
    Configuración de puntos de venta físicos o virtuales
    """
    
    TIPO_POS_CHOICES = [
        ('fisico', 'Punto de Venta Físico'),
        ('virtual', 'Punto de Venta Virtual'),
        ('movil', 'Punto de Venta Móvil'),
        ('kiosco', 'Kiosco de Autoservicio'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='puntos_venta',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=20,
        verbose_name='Código del POS'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Punto de Venta'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_pos = models.CharField(
        max_length=10,
        choices=TIPO_POS_CHOICES,
        default='fisico',
        verbose_name='Tipo de POS'
    )
    
    # Ubicación
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    
    almacen_predeterminado = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='puntos_venta',
        verbose_name='Almacén Predeterminado'
    )
    
    # Configuración de operación
    permite_ventas_credito = models.BooleanField(
        default=True,
        verbose_name='Permite Ventas a Crédito'
    )
    
    permite_descuentos = models.BooleanField(
        default=True,
        verbose_name='Permite Descuentos'
    )
    
    descuento_maximo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        verbose_name='Descuento Máximo (%)'
    )
    
    requiere_cliente = models.BooleanField(
        default=False,
        verbose_name='Requiere Cliente para Venta'
    )
    
    # Series predeterminadas
    serie_factura_predeterminada = models.CharField(
        max_length=4,
        default='F001',
        verbose_name='Serie Factura Predeterminada'
    )
    
    serie_boleta_predeterminada = models.CharField(
        max_length=4,
        default='B001',
        verbose_name='Serie Boleta Predeterminada'
    )
    
    # Configuración de impresión
    impresora_predeterminada = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Impresora Predeterminada'
    )
    
    formato_ticket = models.CharField(
        max_length=20,
        choices=[
            ('80mm', 'Ticket 80mm'),
            ('58mm', 'Ticket 58mm'),
            ('a4', 'Hoja A4'),
        ],
        default='80mm',
        verbose_name='Formato de Ticket'
    )
    
    auto_imprimir = models.BooleanField(
        default=True,
        verbose_name='Auto Imprimir Comprobantes'
    )
    
    # Estado
    esta_activo = models.BooleanField(
        default=True,
        verbose_name='Está Activo'
    )
    
    ultima_actividad = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Actividad'
    )
    
    class Meta:
        db_table = 'pos_punto_venta'
        verbose_name = 'Punto de Venta'
        verbose_name_plural = 'Puntos de Venta'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['esta_activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# =============================================================================
# MODELO SESIÓN DE CAJA
# =============================================================================
class SesionCaja(ModeloBase):
    """
    Sesiones de trabajo en caja para control de turnos
    """
    
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
        ('suspendida', 'Suspendida'),
    ]
    
    punto_venta = models.ForeignKey(
        PuntoVenta,
        on_delete=models.CASCADE,
        related_name='sesiones_caja',
        verbose_name='Punto de Venta'
    )
    
    numero_sesion = models.CharField(
        max_length=20,
        verbose_name='Número de Sesión'
    )
    
    usuario_cajero = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='sesiones_cajero',
        verbose_name='Cajero'
    )
    
    # Fechas y horarios
    fecha_apertura = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Apertura'
    )
    
    fecha_cierre = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Cierre'
    )
    
    # Montos de apertura
    monto_apertura_efectivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Apertura Efectivo'
    )
    
    # Totales de ventas
    total_ventas_efectivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Ventas Efectivo'
    )
    
    total_ventas_tarjeta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Ventas Tarjeta'
    )
    
    total_ventas_transferencia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Ventas Transferencia'
    )
    
    total_ventas_otros = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Ventas Otros'
    )
    
    # Conteos y diferencias
    cantidad_ventas = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad de Ventas'
    )
    
    monto_esperado_caja = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Esperado en Caja'
    )
    
    monto_real_caja = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Real en Caja'
    )
    
    diferencia_caja = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Diferencia en Caja'
    )
    
    # Estado
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='abierta',
        verbose_name='Estado'
    )
    
    observaciones_apertura = models.TextField(
        blank=True,
        verbose_name='Observaciones de Apertura'
    )
    
    observaciones_cierre = models.TextField(
        blank=True,
        verbose_name='Observaciones de Cierre'
    )
    
    class Meta:
        db_table = 'pos_sesion_caja'
        verbose_name = 'Sesión de Caja'
        verbose_name_plural = 'Sesiones de Caja'
        indexes = [
            models.Index(fields=['numero_sesion']),
            models.Index(fields=['fecha_apertura']),
            models.Index(fields=['usuario_cajero']),
            models.Index(fields=['estado']),
        ]
        ordering = ['-fecha_apertura']
    
    def __str__(self):
        return f"Sesión {self.numero_sesion} - {self.usuario_cajero.get_nombre_completo()}"
    
    def calcular_totales(self):
        """Calcula los totales de la sesión basado en las ventas"""
        ventas = self.ventas.filter(estado='completada')
        
        self.cantidad_ventas = ventas.count()
        
        # Calcular totales por método de pago
        for venta in ventas:
            pagos = venta.pagos.all()
            for pago in pagos:
                if pago.metodo_pago.tipo == 'efectivo':
                    self.total_ventas_efectivo += pago.monto
                elif pago.metodo_pago.tipo == 'tarjeta':
                    self.total_ventas_tarjeta += pago.monto
                elif pago.metodo_pago.tipo == 'transferencia':
                    self.total_ventas_transferencia += pago.monto
                else:
                    self.total_ventas_otros += pago.monto
        
        # Calcular monto esperado
        self.monto_esperado_caja = self.monto_apertura_efectivo + self.total_ventas_efectivo
        
        # Calcular diferencia
        self.diferencia_caja = self.monto_real_caja - self.monto_esperado_caja
        
        return {
            'total_efectivo': self.total_ventas_efectivo,
            'total_tarjeta': self.total_ventas_tarjeta,
            'total_transferencia': self.total_ventas_transferencia,
            'total_otros': self.total_ventas_otros,
            'cantidad_ventas': self.cantidad_ventas,
            'diferencia': self.diferencia_caja
        }
    
    def cerrar_sesion(self, monto_real_caja, observaciones=""):
        """Cierra la sesión de caja"""
        self.fecha_cierre = timezone.now()
        self.monto_real_caja = monto_real_caja
        self.observaciones_cierre = observaciones
        self.estado = 'cerrada'
        self.calcular_totales()
        self.save()

# =============================================================================
# MODELO MÉTODO DE PAGO
# =============================================================================
class MetodoPago(ModeloBase):
    """
    Métodos de pago disponibles en el POS
    """
    
    TIPO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('yape', 'Yape'),
        ('plin', 'Plin'),
        ('billetera_digital', 'Billetera Digital'),
        ('cheque', 'Cheque'),
        ('credito_empresa', 'Crédito de la Empresa'),
        ('vales', 'Vales de Consumo'),
    ]
    
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Método'
    )
    
    # Configuración
    requiere_referencia = models.BooleanField(
        default=False,
        verbose_name='Requiere Número de Referencia'
    )
    
    permite_vuelto = models.BooleanField(
        default=False,
        verbose_name='Permite Vuelto'
    )
    
    comision_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Comisión (%)'
    )
    
    comision_fija = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Comisión Fija'
    )
    
    # Cuenta contable asociada
    cuenta_contable_codigo = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Código Cuenta Contable'
    )
    
    class Meta:
        db_table = 'pos_metodo_pago'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# =============================================================================
# MODELO VENTA POS
# =============================================================================
class VentaPOS(ModeloBase):
    """
    Ventas realizadas desde el punto de venta
    """
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('anulada', 'Anulada'),
    ]
    
    TIPO_COMPROBANTE_CHOICES = [
        ('boleta', 'Boleta de Venta'),
        ('factura', 'Factura'),
        ('nota_venta', 'Nota de Venta'),
    ]
    
    # Identificación
    numero_venta = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Venta'
    )
    
    punto_venta = models.ForeignKey(
        PuntoVenta,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Punto de Venta'
    )
    
    sesion_caja = models.ForeignKey(
        SesionCaja,
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Sesión de Caja'
    )
    
    # Cliente
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='ventas_pos',
        verbose_name='Cliente'
    )
    
    # Fechas
    fecha_venta = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Venta'
    )
    
    # Comprobante
    tipo_comprobante = models.CharField(
        max_length=15,
        choices=TIPO_COMPROBANTE_CHOICES,
        default='boleta',
        verbose_name='Tipo de Comprobante'
    )
    
    generar_comprobante_electronico = models.BooleanField(
        default=True,
        verbose_name='Generar Comprobante Electrónico'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    
    descuento_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento Total'
    )
    
    igv_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='IGV Total'
    )
    
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total'
    )
    
    # Usuario
    usuario_vendedor = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='ventas_realizadas',
        verbose_name='Vendedor'
    )
    
    # Estado
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    
    # Observaciones
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    # Referencias a comprobantes electrónicos
    factura_generada = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Factura Generada'
    )
    
    boleta_generada = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Boleta Generada'
    )
    
    class Meta:
        db_table = 'pos_venta'
        verbose_name = 'Venta POS'
        verbose_name_plural = 'Ventas POS'
        indexes = [
            models.Index(fields=['numero_venta']),
            models.Index(fields=['fecha_venta']),
            models.Index(fields=['cliente']),
            models.Index(fields=['estado']),
            models.Index(fields=['punto_venta']),
            models.Index(fields=['sesion_caja']),
        ]
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta {self.numero_venta} - {self.fecha_venta.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_totales(self):
        """Calcula los totales de la venta basado en los items"""
        items = self.items.all()
        
        subtotal = sum(item.valor_venta for item in items)
        igv_total = sum(item.igv for item in items)
        descuento_total = sum(item.descuento_total for item in items)
        total = subtotal + igv_total - descuento_total
        
        self.subtotal = subtotal
        self.igv_total = igv_total
        self.descuento_total = descuento_total
        self.total = total
        
        return {
            'subtotal': self.subtotal,
            'igv_total': self.igv_total,
            'descuento_total': self.descuento_total,
            'total': self.total
        }
    
    def completar_venta(self):
        """Completa la venta y genera movimientos de inventario"""
        if self.estado == 'en_proceso':
            self.estado = 'completada'
            self.save(update_fields=['estado'])
            
            # Aquí se generarían los movimientos de inventario
            # y el comprobante electrónico si corresponde
            
            return True
        return False

# =============================================================================
# MODELO ITEM VENTA POS
# =============================================================================
class ItemVentaPOS(ModeloBase):
    """
    Items de ventas del punto de venta
    """
    
    venta = models.ForeignKey(
        VentaPOS,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Venta'
    )
    
    numero_item = models.PositiveIntegerField(
        verbose_name='Número de Item'
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name='Producto'
    )
    
    # Descripción (puede ser diferente al producto)
    descripcion = models.CharField(
        max_length=250,
        verbose_name='Descripción'
    )
    
    # Cantidades
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Cantidad'
    )
    
    # Precios
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Precio Unitario'
    )
    
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento (%)'
    )
    
    descuento_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Descuento Unitario'
    )
    
    descuento_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento Total'
    )
    
    # Cálculos
    valor_venta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor de Venta'
    )
    
    igv = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='IGV'
    )
    
    precio_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio Total'
    )
    
    class Meta:
        db_table = 'pos_item_venta'
        verbose_name = 'Item de Venta POS'
        verbose_name_plural = 'Items de Ventas POS'
        unique_together = ['venta', 'numero_item']
        ordering = ['numero_item']
    
    def save(self, *args, **kwargs):
        """Calcular valores automáticamente"""
        # Calcular descuentos
        if self.descuento_porcentaje > 0:
            self.descuento_unitario = self.precio_unitario * (self.descuento_porcentaje / 100)
        
        self.descuento_total = self.cantidad * self.descuento_unitario
        
        # Calcular valor de venta
        precio_con_descuento = self.precio_unitario - self.descuento_unitario
        self.valor_venta = self.cantidad * precio_con_descuento
        
        # Calcular IGV (18%)
        if self.producto.tipo_afectacion_igv == '10':  # Gravado
            # Si el precio incluye IGV, lo separamos
            if self.producto.incluye_igv:
                valor_sin_igv = self.valor_venta / Decimal('1.18')
                self.igv = self.valor_venta - valor_sin_igv
                self.valor_venta = valor_sin_igv
            else:
                self.igv = self.valor_venta * Decimal('0.18')
        else:
            self.igv = Decimal('0.00')
        
        # Calcular precio total
        self.precio_total = self.valor_venta + self.igv
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.descripcion} - {self.cantidad} x {self.precio_unitario}"

# =============================================================================
# MODELO PAGO VENTA
# =============================================================================
class PagoVenta(ModeloBase):
    """
    Pagos realizados para una venta
    """
    
    venta = models.ForeignKey(
        VentaPOS,
        on_delete=models.CASCADE,
        related_name='pagos',
        verbose_name='Venta'
    )
    
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        verbose_name='Método de Pago'
    )
    
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto'
    )
    
    # Información adicional según método de pago
    numero_referencia = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Referencia',
        help_text='Número de operación, autorización, etc.'
    )
    
    numero_tarjeta_ultimos_4 = models.CharField(
        max_length=4,
        blank=True,
        verbose_name='Últimos 4 dígitos de tarjeta'
    )
    
    nombre_titular = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nombre del Titular'
    )
    
    # Vuelto (solo para efectivo)
    monto_recibido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Recibido'
    )
    
    vuelto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Vuelto'
    )
    
    # Comisiones
    comision = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Comisión'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    class Meta:
        db_table = 'pos_pago_venta'
        verbose_name = 'Pago de Venta'
        verbose_name_plural = 'Pagos de Ventas'
        indexes = [
            models.Index(fields=['venta']),
            models.Index(fields=['metodo_pago']),
        ]
    
    def save(self, *args, **kwargs):
        """Calcular comisión y vuelto automáticamente"""
        # Calcular comisión
        self.comision = (self.monto * self.metodo_pago.comision_porcentaje / 100) + self.metodo_pago.comision_fija
        
        # Calcular vuelto (solo para efectivo)
        if self.metodo_pago.permite_vuelto and self.monto_recibido > self.monto:
            self.vuelto = self.monto_recibido - self.monto
        else:
            self.vuelto = Decimal('0.00')
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.metodo_pago.nombre} - S/ {self.monto}"