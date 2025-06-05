"""
Modelos de inventarios para FELICITA
Sistema de Facturación Electrónica para Perú
Implementa método PEPS (FIFO) obligatorio según SUNAT
"""

from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


class TipoMovimiento(models.TextChoices):
    """Tipos de movimiento de inventario"""
    ENTRADA = 'ENTRADA', 'Entrada'
    SALIDA = 'SALIDA', 'Salida'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
    AJUSTE = 'AJUSTE', 'Ajuste'


class EstadoMovimiento(models.TextChoices):
    """Estados de movimiento de inventario"""
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    CONFIRMADO = 'CONFIRMADO', 'Confirmado'
    ANULADO = 'ANULADO', 'Anulado'


class Almacen(models.Model):
    """
    Modelo para almacenes de la empresa
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='almacenes',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=20,
        verbose_name='Código',
        help_text='Código único del almacén'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Almacén'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    
    responsable = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='almacenes_a_cargo',
        verbose_name='Responsable'
    )
    
    es_principal = models.BooleanField(
        default=False,
        verbose_name='Almacén Principal',
        help_text='Almacén principal para ventas'
    )
    
    permite_ventas = models.BooleanField(
        default=True,
        verbose_name='Permite Ventas',
        help_text='Si se puede vender desde este almacén'
    )
    
    permite_compras = models.BooleanField(
        default=True,
        verbose_name='Permite Compras',
        help_text='Si se pueden recibir compras en este almacén'
    )
    
    estado = models.BooleanField(
        default=True,
        verbose_name='Estado'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        db_table = 'almacenes'
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        unique_together = ['empresa', 'codigo']
        ordering = ['-es_principal', 'nombre']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['responsable']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """Asegurar que solo hay un almacén principal por empresa"""
        if self.es_principal:
            Almacen.objects.filter(
                empresa=self.empresa,
                es_principal=True
            ).exclude(id=self.id).update(es_principal=False)
        
        super().save(*args, **kwargs)
    
    def get_total_productos(self):
        """Obtener total de productos en el almacén"""
        return self.stocks.filter(cantidad_total__gt=0).count()
    
    def get_valor_total_inventario(self):
        """Obtener valor total del inventario en el almacén"""
        total = self.stocks.aggregate(
            total=models.Sum('valor_total')
        )['total']
        return total or Decimal('0.00')
    
    def get_productos_stock_bajo(self):
        """Obtener productos con stock bajo en este almacén"""
        from aplicaciones.productos.models import Producto
        
        productos_stock_bajo = []
        stocks = self.stocks.filter(cantidad_disponible__gt=0).select_related('producto')
        
        for stock in stocks:
            if (stock.producto.stock_minimo > 0 and 
                stock.cantidad_disponible <= stock.producto.stock_minimo):
                productos_stock_bajo.append(stock)
        
        return productos_stock_bajo


class Stock(models.Model):
    """
    Modelo para control de stock por producto y almacén
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='Empresa'
    )
    
    producto = models.ForeignKey(
        'productos.Producto',
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
    
    # Cantidades
    cantidad_disponible = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Cantidad Disponible'
    )
    
    cantidad_reservada = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Cantidad Reservada',
        help_text='Stock reservado para pedidos pendientes'
    )
    
    # Valuación PEPS
    costo_promedio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Costo Promedio Unitario'
    )
    
    fecha_ultimo_movimiento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último Movimiento'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        db_table = 'stocks'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        unique_together = ['producto', 'almacen']
        indexes = [
            models.Index(fields=['producto']),
            models.Index(fields=['almacen']),
            models.Index(fields=['cantidad_disponible']),
        ]
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.almacen.nombre}: {self.cantidad_total}"
    
    @property
    def cantidad_total(self):
        """Cantidad total (disponible + reservada)"""
        return self.cantidad_disponible + self.cantidad_reservada
    
    @property
    def valor_total(self):
        """Valor total del stock"""
        return self.cantidad_total * self.costo_promedio
    
    def puede_sacar(self, cantidad):
        """Verificar si se puede sacar una cantidad del stock"""
        return self.cantidad_disponible >= cantidad
    
    def reservar_cantidad(self, cantidad):
        """Reservar una cantidad del stock"""
        if not self.puede_sacar(cantidad):
            raise ValueError(f"Stock insuficiente. Disponible: {self.cantidad_disponible}")
        
        self.cantidad_disponible -= cantidad
        self.cantidad_reservada += cantidad
        self.save()
    
    def liberar_reserva(self, cantidad):
        """Liberar cantidad reservada"""
        cantidad_a_liberar = min(cantidad, self.cantidad_reservada)
        self.cantidad_reservada -= cantidad_a_liberar
        self.cantidad_disponible += cantidad_a_liberar
        self.save()
    
    def confirmar_salida_reservada(self, cantidad):
        """Confirmar salida de cantidad reservada"""
        cantidad_a_confirmar = min(cantidad, self.cantidad_reservada)
        self.cantidad_reservada -= cantidad_a_confirmar
        self.save()
        return cantidad_a_confirmar


class MovimientoInventario(models.Model):
    """
    Modelo para registrar todos los movimientos de inventario
    Implementa trazabilidad completa para método PEPS
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='movimientos_inventario',
        verbose_name='Empresa'
    )
    
    # Referencia del movimiento
    tipo_movimiento = models.CharField(
        max_length=20,
        choices=TipoMovimiento.choices,
        verbose_name='Tipo de Movimiento'
    )
    
    numero_documento = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Documento',
        help_text='Número de factura, guía, etc.'
    )
    
    referencia_tabla = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tabla de Referencia',
        help_text='Tabla que origina el movimiento'
    )
    
    referencia_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID de Referencia',
        help_text='ID del registro que origina el movimiento'
    )
    
    # Producto y almacén
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name='Producto'
    )
    
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name='Almacén'
    )
    
    # Detalles del movimiento
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Cantidad',
        help_text='Cantidad positiva para entradas, negativa para salidas'
    )
    
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Costo Unitario'
    )
    
    # Stock resultante (para validación y trazabilidad)
    stock_anterior = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Stock Anterior'
    )
    
    stock_actual = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Stock Actual'
    )
    
    # Para control PEPS
    lote_numero = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Lote',
        help_text='Para trazabilidad PEPS'
    )
    
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento'
    )
    
    # Metadatos
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoMovimiento.choices,
        default=EstadoMovimiento.PENDIENTE,
        verbose_name='Estado'
    )
    
    fecha_movimiento = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha del Movimiento'
    )
    
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_inventario',
        verbose_name='Usuario'
    )
    
    class Meta:
        db_table = 'movimientos_inventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha_movimiento']
        indexes = [
            models.Index(fields=['producto', 'fecha_movimiento']),
            models.Index(fields=['almacen', 'fecha_movimiento']),
            models.Index(fields=['tipo_movimiento']),
            models.Index(fields=['referencia_tabla', 'referencia_id']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        signo = '+' if self.cantidad >= 0 else ''
        return f"{self.producto.codigo} - {signo}{self.cantidad} - {self.fecha_movimiento}"
    
    @property
    def costo_total(self):
        """Costo total del movimiento"""
        return abs(self.cantidad) * self.costo_unitario
    
    def es_entrada(self):
        """Verificar si es un movimiento de entrada"""
        return self.cantidad > 0
    
    def es_salida(self):
        """Verificar si es un movimiento de salida"""
        return self.cantidad < 0
    
    def confirmar(self):
        """Confirmar el movimiento"""
        if self.estado == EstadoMovimiento.CONFIRMADO:
            return
        
        with transaction.atomic():
            # Actualizar stock
            stock, created = Stock.objects.get_or_create(
                producto=self.producto,
                almacen=self.almacen,
                defaults={
                    'empresa': self.empresa,
                    'cantidad_disponible': Decimal('0.0000'),
                    'costo_promedio': Decimal('0.0000'),
                }
            )
            
            # Registrar stock anterior
            self.stock_anterior = stock.cantidad_disponible
            
            if self.es_entrada():
                self._procesar_entrada(stock)
            else:
                self._procesar_salida(stock)
            
            # Actualizar campos del movimiento
            self.stock_actual = stock.cantidad_disponible
            self.estado = EstadoMovimiento.CONFIRMADO
            stock.fecha_ultimo_movimiento = self.fecha_movimiento
            
            stock.save()
            self.save()
    
    def _procesar_entrada(self, stock):
        """Procesar entrada de inventario con método PEPS"""
        cantidad_entrada = abs(self.cantidad)
        
        # Calcular nuevo costo promedio ponderado
        if stock.cantidad_disponible > 0:
            valor_actual = stock.cantidad_disponible * stock.costo_promedio
            valor_entrada = cantidad_entrada * self.costo_unitario
            cantidad_total = stock.cantidad_disponible + cantidad_entrada
            
            nuevo_costo_promedio = (valor_actual + valor_entrada) / cantidad_total
        else:
            nuevo_costo_promedio = self.costo_unitario
        
        # Actualizar stock
        stock.cantidad_disponible += cantidad_entrada
        stock.costo_promedio = nuevo_costo_promedio.quantize(
            Decimal('0.0001'), rounding=ROUND_HALF_UP
        )
        
        # Crear lote PEPS si no existe
        if not self.lote_numero:
            self.lote_numero = self._generar_numero_lote()
        
        # Registrar lote PEPS
        LotePEPS.objects.create(
            empresa=self.empresa,
            producto=self.producto,
            almacen=self.almacen,
            movimiento_origen=self,
            numero_lote=self.lote_numero,
            cantidad_inicial=cantidad_entrada,
            cantidad_disponible=cantidad_entrada,
            costo_unitario=self.costo_unitario,
            fecha_ingreso=self.fecha_movimiento,
            fecha_vencimiento=self.fecha_vencimiento,
        )
    
    def _procesar_salida(self, stock):
        """Procesar salida de inventario con método PEPS"""
        cantidad_salida = abs(self.cantidad)
        
        if stock.cantidad_disponible < cantidad_salida:
            if not self.empresa.puede_tener_stock_negativo():
                raise ValueError(f"Stock insuficiente. Disponible: {stock.cantidad_disponible}")
        
        # Aplicar PEPS para salidas
        self._aplicar_peps_salida(cantidad_salida, stock)
        
        # Actualizar stock
        stock.cantidad_disponible -= cantidad_salida
        
        # Recalcular costo promedio si es necesario
        if stock.cantidad_disponible <= 0:
            stock.costo_promedio = Decimal('0.0000')
        else:
            # El costo promedio se mantiene basado en los lotes restantes
            stock.costo_promedio = self._calcular_costo_promedio_peps(stock)
    
    def _aplicar_peps_salida(self, cantidad_salida, stock):
        """Aplicar método PEPS para salidas"""
        cantidad_restante = cantidad_salida
        costo_total_salida = Decimal('0.00')
        
        # Obtener lotes PEPS ordenados por fecha (FIFO)
        lotes = LotePEPS.objects.filter(
            producto=self.producto,
            almacen=self.almacen,
            cantidad_disponible__gt=0
        ).order_by('fecha_ingreso', 'id')
        
        for lote in lotes:
            if cantidad_restante <= 0:
                break
            
            cantidad_del_lote = min(cantidad_restante, lote.cantidad_disponible)
            
            # Registrar movimiento PEPS
            MovimientoPEPS.objects.create(
                movimiento_inventario=self,
                lote=lote,
                cantidad_utilizada=cantidad_del_lote,
                costo_unitario=lote.costo_unitario,
            )
            
            # Actualizar lote
            lote.cantidad_disponible -= cantidad_del_lote
            lote.save()
            
            # Acumular costo
            costo_total_salida += cantidad_del_lote * lote.costo_unitario
            cantidad_restante -= cantidad_del_lote
        
        # Calcular costo unitario promedio de la salida
        if cantidad_salida > 0:
            self.costo_unitario = costo_total_salida / cantidad_salida
        
        if cantidad_restante > 0 and not self.empresa.puede_tener_stock_negativo():
            raise ValueError(f"No hay suficientes lotes PEPS para cubrir la salida")
    
    def _calcular_costo_promedio_peps(self, stock):
        """Calcular costo promedio basado en lotes PEPS disponibles"""
        lotes = LotePEPS.objects.filter(
            producto=self.producto,
            almacen=self.almacen,
            cantidad_disponible__gt=0
        )
        
        if not lotes.exists():
            return Decimal('0.0000')
        
        valor_total = sum(
            lote.cantidad_disponible * lote.costo_unitario 
            for lote in lotes
        )
        cantidad_total = sum(lote.cantidad_disponible for lote in lotes)
        
        if cantidad_total > 0:
            return valor_total / cantidad_total
        
        return Decimal('0.0000')
    
    def _generar_numero_lote(self):
        """Generar número de lote automático"""
        fecha_str = self.fecha_movimiento.strftime('%Y%m%d')
        secuencia = MovimientoInventario.objects.filter(
            empresa=self.empresa,
            fecha_movimiento__date=self.fecha_movimiento.date(),
            lote_numero__startswith=f"L{fecha_str}"
        ).count() + 1
        
        return f"L{fecha_str}{secuencia:04d}"
    
    def anular(self):
        """Anular el movimiento"""
        if self.estado != EstadoMovimiento.CONFIRMADO:
            raise ValueError("Solo se pueden anular movimientos confirmados")
        
        with transaction.atomic():
            # Crear movimiento inverso
            movimiento_inverso = MovimientoInventario.objects.create(
                empresa=self.empresa,
                tipo_movimiento=self.tipo_movimiento,
                numero_documento=f"ANULACION-{self.numero_documento}",
                referencia_tabla=self.referencia_tabla,
                referencia_id=self.referencia_id,
                producto=self.producto,
                almacen=self.almacen,
                cantidad=-self.cantidad,  # Cantidad inversa
                costo_unitario=self.costo_unitario,
                observaciones=f"Anulación de movimiento {self.id}",
                usuario=self.usuario,
                lote_numero=f"ANULACION-{self.lote_numero}",
            )
            
            # Confirmar movimiento inverso
            movimiento_inverso.confirmar()
            
            # Marcar este movimiento como anulado
            self.estado = EstadoMovimiento.ANULADO
            self.save()
    
    @classmethod
    def crear_entrada(cls, empresa, producto, almacen, cantidad, costo_unitario,
                     referencia_tabla=None, referencia_id=None, numero_documento=None,
                     observaciones=None, usuario=None, confirmar=True):
        """Método de clase para crear entrada de inventario"""
        movimiento = cls.objects.create(
            empresa=empresa,
            tipo_movimiento=TipoMovimiento.ENTRADA,
            producto=producto,
            almacen=almacen,
            cantidad=abs(cantidad),
            costo_unitario=costo_unitario,
            referencia_tabla=referencia_tabla,
            referencia_id=referencia_id,
            numero_documento=numero_documento,
            observaciones=observaciones,
            usuario=usuario,
        )
        
        if confirmar:
            movimiento.confirmar()
        
        return movimiento
    
    @classmethod
    def crear_salida(cls, empresa, producto, almacen, cantidad,
                    referencia_tabla=None, referencia_id=None, numero_documento=None,
                    observaciones=None, usuario=None, confirmar=True):
        """Método de clase para crear salida de inventario"""
        movimiento = cls.objects.create(
            empresa=empresa,
            tipo_movimiento=TipoMovimiento.SALIDA,
            producto=producto,
            almacen=almacen,
            cantidad=-abs(cantidad),
            costo_unitario=Decimal('0.0000'),  # Se calculará con PEPS
            referencia_tabla=referencia_tabla,
            referencia_id=referencia_id,
            numero_documento=numero_documento,
            observaciones=observaciones,
            usuario=usuario,
        )
        
        if confirmar:
            movimiento.confirmar()
        
        return movimiento


class LotePEPS(models.Model):
    """
    Modelo para manejo de lotes PEPS (FIFO)
    Cada entrada de inventario genera un lote
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='lotes_peps',
        verbose_name='Empresa'
    )
    
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE,
        related_name='lotes_peps',
        verbose_name='Producto'
    )
    
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.CASCADE,
        related_name='lotes_peps',
        verbose_name='Almacén'
    )
    
    movimiento_origen = models.ForeignKey(
        MovimientoInventario,
        on_delete=models.CASCADE,
        related_name='lotes_generados',
        verbose_name='Movimiento de Origen'
    )
    
    numero_lote = models.CharField(
        max_length=50,
        verbose_name='Número de Lote'
    )
    
    cantidad_inicial = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Cantidad Inicial'
    )
    
    cantidad_disponible = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Cantidad Disponible'
    )
    
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Costo Unitario'
    )
    
    fecha_ingreso = models.DateTimeField(
        verbose_name='Fecha de Ingreso'
    )
    
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento'
    )
    
    class Meta:
        db_table = 'lotes_peps'
        verbose_name = 'Lote PEPS'
        verbose_name_plural = 'Lotes PEPS'
        ordering = ['fecha_ingreso', 'id']
        indexes = [
            models.Index(fields=['producto', 'almacen', 'fecha_ingreso']),
            models.Index(fields=['numero_lote']),
            models.Index(fields=['cantidad_disponible']),
        ]
    
    def __str__(self):
        return f"Lote {self.numero_lote} - {self.producto.codigo}"
    
    @property
    def cantidad_utilizada(self):
        """Cantidad ya utilizada del lote"""
        return self.cantidad_inicial - self.cantidad_disponible
    
    @property
    def valor_disponible(self):
        """Valor disponible del lote"""
        return self.cantidad_disponible * self.costo_unitario
    
    def esta_agotado(self):
        """Verificar si el lote está agotado"""
        return self.cantidad_disponible <= 0
    
    def esta_vencido(self):
        """Verificar si el lote está vencido"""
        if not self.fecha_vencimiento:
            return False
        return timezone.now().date() > self.fecha_vencimiento


class MovimientoPEPS(models.Model):
    """
    Modelo para rastrear qué lotes se utilizaron en cada salida
    Garantiza trazabilidad completa del método PEPS
    """
    movimiento_inventario = models.ForeignKey(
        MovimientoInventario,
        on_delete=models.CASCADE,
        related_name='movimientos_peps',
        verbose_name='Movimiento de Inventario'
    )
    
    lote = models.ForeignKey(
        LotePEPS,
        on_delete=models.CASCADE,
        related_name='movimientos_peps',
        verbose_name='Lote PEPS'
    )
    
    cantidad_utilizada = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Cantidad Utilizada'
    )
    
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name='Costo Unitario'
    )
    
    class Meta:
        db_table = 'movimientos_peps'
        verbose_name = 'Movimiento PEPS'
        verbose_name_plural = 'Movimientos PEPS'
        ordering = ['lote__fecha_ingreso']
    
    def __str__(self):
        return f"PEPS: {self.lote.numero_lote} - {self.cantidad_utilizada}"
    
    @property
    def costo_total(self):
        """Costo total del movimiento PEPS"""
        return self.cantidad_utilizada * self.costo_unitario