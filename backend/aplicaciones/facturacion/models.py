"""
Modelos de facturación para FELICITA
Sistema de Facturación Electrónica para Perú
Cumple normativa SUNAT y integración con Nubefact
"""

from django.db import models, transaction
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import json


class TipoComprobante(models.TextChoices):
    """Tipos de comprobante según SUNAT"""
    FACTURA = '01', 'Factura'
    BOLETA = '03', 'Boleta de Venta'
    NOTA_CREDITO = '07', 'Nota de Crédito'
    NOTA_DEBITO = '08', 'Nota de Débito'
    GUIA_REMISION = '09', 'Guía de Remisión'


class EstadoSunat(models.TextChoices):
    """Estados del comprobante en SUNAT"""
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    ENVIADO = 'ENVIADO', 'Enviado'
    ACEPTADO = 'ACEPTADO', 'Aceptado'
    RECHAZADO = 'RECHAZADO', 'Rechazado'
    ANULADO = 'ANULADO', 'Anulado'


class FormaPago(models.TextChoices):
    """Formas de pago disponibles"""
    CONTADO = 'CONTADO', 'Contado'
    CREDITO = 'CREDITO', 'Crédito'
    TARJETA_CREDITO = 'TARJETA_CREDITO', 'Tarjeta de Crédito'
    TARJETA_DEBITO = 'TARJETA_DEBITO', 'Tarjeta de Débito'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia Bancaria'
    EFECTIVO = 'EFECTIVO', 'Efectivo'


class TipoMoneda(models.TextChoices):
    """Tipos de moneda según SUNAT"""
    PEN = 'PEN', 'Sol Peruano'
    USD = 'USD', 'Dólar Americano'
    EUR = 'EUR', 'Euro'


class SerieComprobante(models.Model):
    """
    Modelo para series de comprobantes electrónicos
    Maneja numeración correlativa obligatoria por SUNAT
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='series_comprobantes',
        verbose_name='Empresa'
    )
    
    tipo_comprobante = models.CharField(
        max_length=2,
        choices=TipoComprobante.choices,
        verbose_name='Tipo de Comprobante'
    )
    
    serie = models.CharField(
        max_length=4,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]{4}$',
            message='La serie debe tener 4 caracteres alfanuméricos'
        )],
        verbose_name='Serie',
        help_text='Serie de 4 caracteres (ej: F001, B001)'
    )
    
    numero_actual = models.PositiveIntegerField(
        default=0,
        verbose_name='Número Actual',
        help_text='Último número utilizado'
    )
    
    numero_maximo = models.PositiveIntegerField(
        default=99999999,
        verbose_name='Número Máximo',
        help_text='Número máximo permitido'
    )
    
    # Configuración
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    electronico = models.BooleanField(
        default=True,
        verbose_name='Electrónico',
        help_text='Si la serie es para comprobantes electrónicos'
    )
    
    por_defecto = models.BooleanField(
        default=False,
        verbose_name='Por Defecto',
        help_text='Serie por defecto para este tipo de comprobante'
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
        db_table = 'series_comprobantes'
        verbose_name = 'Serie de Comprobante'
        verbose_name_plural = 'Series de Comprobantes'
        unique_together = ['empresa', 'tipo_comprobante', 'serie']
        ordering = ['tipo_comprobante', 'serie']
        indexes = [
            models.Index(fields=['empresa', 'tipo_comprobante']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_comprobante_display()} - {self.serie}"
    
    def save(self, *args, **kwargs):
        """Asegurar que solo hay una serie por defecto por tipo de comprobante"""
        if self.por_defecto:
            SerieComprobante.objects.filter(
                empresa=self.empresa,
                tipo_comprobante=self.tipo_comprobante,
                por_defecto=True
            ).exclude(id=self.id).update(por_defecto=False)
        
        super().save(*args, **kwargs)
    
    def obtener_siguiente_numero(self):
        """Obtener siguiente número correlativo"""
        if self.numero_actual >= self.numero_maximo:
            raise ValueError(f"Se alcanzó el número máximo para la serie {self.serie}")
        
        with transaction.atomic():
            # Bloquear el registro para evitar concurrencia
            serie = SerieComprobante.objects.select_for_update().get(id=self.id)
            serie.numero_actual += 1
            serie.save()
            
            return serie.numero_actual
    
    def get_numero_completo(self, numero=None):
        """Obtener número completo del comprobante"""
        num = numero or self.numero_actual
        return f"{self.serie}-{num:08d}"
    
    def puede_emitir(self):
        """Verificar si se puede emitir con esta serie"""
        return (
            self.activo and 
            self.numero_actual < self.numero_maximo
        )
    
    def get_comprobantes_emitidos(self):
        """Obtener comprobantes emitidos con esta serie"""
        return self.comprobantes.all()
    
    def get_total_emitidos(self):
        """Obtener total de comprobantes emitidos"""
        return self.comprobantes.count()


class Comprobante(models.Model):
    """
    Modelo principal para comprobantes electrónicos
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='comprobantes',
        verbose_name='Empresa'
    )
    
    # Identificación del comprobante
    tipo_comprobante = models.CharField(
        max_length=2,
        choices=TipoComprobante.choices,
        verbose_name='Tipo de Comprobante'
    )
    
    serie = models.CharField(
        max_length=4,
        verbose_name='Serie'
    )
    
    numero = models.PositiveIntegerField(
        verbose_name='Número'
    )
    
    # Cliente
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='comprobantes',
        verbose_name='Cliente'
    )
    
    cliente_numero_documento = models.CharField(
        max_length=20,
        verbose_name='Número de Documento del Cliente'
    )
    
    cliente_tipo_documento = models.CharField(
        max_length=1,
        verbose_name='Tipo de Documento del Cliente'
    )
    
    cliente_razon_social = models.CharField(
        max_length=255,
        verbose_name='Razón Social del Cliente'
    )
    
    cliente_direccion = models.TextField(
        blank=True,
        verbose_name='Dirección del Cliente'
    )
    
    cliente_email = models.EmailField(
        blank=True,
        verbose_name='Email del Cliente'
    )
    
    # Fechas
    fecha_emision = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Emisión'
    )
    
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento'
    )
    
    # Montos
    moneda = models.CharField(
        max_length=3,
        choices=TipoMoneda.choices,
        default=TipoMoneda.PEN,
        verbose_name='Moneda'
    )
    
    tipo_cambio = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal('1.0000'),
        verbose_name='Tipo de Cambio'
    )
    
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    
    total_descuentos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Descuentos'
    )
    
    base_imponible = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Base Imponible'
    )
    
    total_igv = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total IGV'
    )
    
    total_otros_impuestos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Otros Impuestos'
    )
    
    total_gratuito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Gratuito'
    )
    
    total_sin_impuestos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total sin Impuestos'
    )
    
    total_con_impuestos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total con Impuestos'
    )
    
    # Configuración de pago
    forma_pago = models.CharField(
        max_length=20,
        choices=FormaPago.choices,
        default=FormaPago.CONTADO,
        verbose_name='Forma de Pago'
    )
    
    condicion_pago = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Condición de Pago'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    # Estado SUNAT y facturación electrónica
    estado_sunat = models.CharField(
        max_length=20,
        choices=EstadoSunat.choices,
        default=EstadoSunat.PENDIENTE,
        verbose_name='Estado SUNAT'
    )
    
    codigo_hash = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Código Hash'
    )
    
    codigo_qr = models.TextField(
        blank=True,
        verbose_name='Código QR'
    )
    
    xml_enviado = models.TextField(
        blank=True,
        verbose_name='XML Enviado a SUNAT'
    )
    
    xml_respuesta = models.TextField(
        blank=True,
        verbose_name='XML Respuesta de SUNAT'
    )
    
    pdf_url = models.URLField(
        blank=True,
        verbose_name='URL del PDF'
    )
    
    # Referencia para notas de crédito/débito
    comprobante_referencia = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='notas_relacionadas',
        verbose_name='Comprobante de Referencia'
    )
    
    motivo_nota = models.TextField(
        blank=True,
        verbose_name='Motivo de la Nota',
        help_text='Motivo para notas de crédito/débito'
    )
    
    # Auditoria
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    usuario_creacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comprobantes_creados',
        verbose_name='Usuario que Creó'
    )
    
    usuario_actualizacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comprobantes_actualizados',
        verbose_name='Usuario que Actualizó'
    )
    
    class Meta:
        db_table = 'comprobantes'
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'
        unique_together = ['empresa', 'tipo_comprobante', 'serie', 'numero']
        ordering = ['-fecha_emision', '-numero']
        indexes = [
            models.Index(fields=['empresa', 'fecha_emision']),
            models.Index(fields=['cliente']),
            models.Index(fields=['estado_sunat']),
            models.Index(fields=['tipo_comprobante']),
            models.Index(fields=['serie', 'numero']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_comprobante_display()} {self.numero_completo}"
    
    @property
    def numero_completo(self):
        """Número completo del comprobante"""
        return f"{self.serie}-{self.numero:08d}"
    
    def save(self, *args, **kwargs):
        """Guardar con cálculos automáticos y validaciones"""
        # Validar que el tipo de comprobante coincide con la serie
        if hasattr(self, '_serie_obj') and self._serie_obj.tipo_comprobante != self.tipo_comprobante:
            raise ValueError("El tipo de comprobante no coincide con la serie")
        
        # Calcular totales automáticamente
        self.calcular_totales()
        
        # Validar totales
        self.validar_totales()
        
        super().save(*args, **kwargs)
    
    def calcular_totales(self):
        """Calcular todos los totales del comprobante"""
        items = self.items.all()
        
        # Inicializar totales
        self.subtotal = Decimal('0.00')
        self.total_descuentos = Decimal('0.00')
        self.base_imponible = Decimal('0.00')
        self.total_igv = Decimal('0.00')
        self.total_gratuito = Decimal('0.00')
        
        for item in items:
            self.subtotal += item.valor_venta
            self.total_descuentos += item.descuento_total
            self.base_imponible += item.base_imponible
            self.total_igv += item.igv_total
            
            # Si es gratuito, sumar al total gratuito
            if item.precio_unitario == 0:
                self.total_gratuito += item.valor_venta
        
        # Calcular totales finales
        self.total_sin_impuestos = self.base_imponible
        self.total_con_impuestos = self.base_imponible + self.total_igv + self.total_otros_impuestos
        
        # Redondear a 2 decimales
        self._redondear_montos()
    
    def _redondear_montos(self):
        """Redondear todos los montos a 2 decimales"""
        campos_monto = [
            'subtotal', 'total_descuentos', 'base_imponible', 'total_igv',
            'total_otros_impuestos', 'total_gratuito', 'total_sin_impuestos',
            'total_con_impuestos'
        ]
        
        for campo in campos_monto:
            valor = getattr(self, campo)
            setattr(self, campo, valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def validar_totales(self):
        """Validar que los totales sean correctos"""
        tolerancia = Decimal('0.01')
        
        # Validar que el total con impuestos sea la suma correcta
        total_calculado = self.base_imponible + self.total_igv + self.total_otros_impuestos
        diferencia = abs(self.total_con_impuestos - total_calculado)
        
        if diferencia > tolerancia:
            raise ValueError(f"Error en cálculo de totales. Diferencia: {diferencia}")
    
    def get_serie_objeto(self):
        """Obtener el objeto serie del comprobante"""
        try:
            return SerieComprobante.objects.get(
                empresa=self.empresa,
                tipo_comprobante=self.tipo_comprobante,
                serie=self.serie
            )
        except SerieComprobante.DoesNotExist:
            return None
    
    def puede_ser_modificado(self):
        """Verificar si el comprobante puede ser modificado"""
        return self.estado_sunat in [EstadoSunat.PENDIENTE, EstadoSunat.RECHAZADO]
    
    def puede_ser_anulado(self):
        """Verificar si el comprobante puede ser anulado"""
        return self.estado_sunat in [EstadoSunat.ACEPTADO, EstadoSunat.ENVIADO]
    
    def es_factura(self):
        """Verificar si es una factura"""
        return self.tipo_comprobante == TipoComprobante.FACTURA
    
    def es_boleta(self):
        """Verificar si es una boleta"""
        return self.tipo_comprobante == TipoComprobante.BOLETA
    
    def es_nota_credito(self):
        """Verificar si es una nota de crédito"""
        return self.tipo_comprobante == TipoComprobante.NOTA_CREDITO
    
    def es_nota_debito(self):
        """Verificar si es una nota de débito"""
        return self.tipo_comprobante == TipoComprobante.NOTA_DEBITO
    
    def get_datos_cliente(self):
        """Obtener datos del cliente para el comprobante"""
        return {
            'numero_documento': self.cliente_numero_documento,
            'tipo_documento': self.cliente_tipo_documento,
            'razon_social': self.cliente_razon_social,
            'direccion': self.cliente_direccion,
            'email': self.cliente_email,
        }
    
    def get_datos_para_xml(self):
        """Obtener datos formateados para XML SUNAT"""
        return {
            'tipo_comprobante': self.tipo_comprobante,
            'serie': self.serie,
            'numero': self.numero,
            'fecha_emision': self.fecha_emision.strftime('%Y-%m-%d'),
            'moneda': self.moneda,
            'cliente': self.get_datos_cliente(),
            'totales': {
                'subtotal': str(self.subtotal),
                'total_descuentos': str(self.total_descuentos),
                'base_imponible': str(self.base_imponible),
                'total_igv': str(self.total_igv),
                'total_con_impuestos': str(self.total_con_impuestos),
            },
            'items': [item.get_datos_para_xml() for item in self.items.all()],
        }
    
    def enviar_a_sunat(self):
        """Enviar comprobante a SUNAT via Nubefact"""
        if self.estado_sunat == EstadoSunat.ACEPTADO:
            raise ValueError("El comprobante ya fue aceptado por SUNAT")
        
        # Aquí se implementaría la integración con Nubefact
        # Por ahora solo cambiar el estado
        self.estado_sunat = EstadoSunat.ENVIADO
        self.save()
    
    def anular(self, motivo="Anulación del comprobante"):
        """Anular comprobante"""
        if not self.puede_ser_anulado():
            raise ValueError("El comprobante no puede ser anulado en su estado actual")
        
        with transaction.atomic():
            # Actualizar estado
            self.estado_sunat = EstadoSunat.ANULADO
            self.observaciones += f"\n\nANULADO: {motivo}"
            self.save()
            
            # Revertir movimientos de inventario si existen
            self._revertir_inventario()
            
            # Aquí se enviaría la comunicación de baja a SUNAT
    
    def _revertir_inventario(self):
        """Revertir movimientos de inventario del comprobante"""
        from aplicaciones.inventarios.models import MovimientoInventario
        
        movimientos = MovimientoInventario.objects.filter(
            referencia_tabla='comprobantes',
            referencia_id=self.id
        )
        
        for movimiento in movimientos:
            movimiento.anular()
    
    @classmethod
    def crear_con_serie(cls, empresa, tipo_comprobante, cliente_data, items_data, 
                       serie=None, usuario=None, **kwargs):
        """Crear comprobante con serie automática"""
        # Obtener serie
        if serie:
            serie_obj = SerieComprobante.objects.get(
                empresa=empresa,
                tipo_comprobante=tipo_comprobante,
                serie=serie,
                activo=True
            )
        else:
            serie_obj = SerieComprobante.objects.filter(
                empresa=empresa,
                tipo_comprobante=tipo_comprobante,
                activo=True,
                por_defecto=True
            ).first()
            
            if not serie_obj:
                serie_obj = SerieComprobante.objects.filter(
                    empresa=empresa,
                    tipo_comprobante=tipo_comprobante,
                    activo=True
                ).first()
        
        if not serie_obj:
            raise ValueError(f"No hay series activas para {tipo_comprobante}")
        
        # Obtener siguiente número
        numero = serie_obj.obtener_siguiente_numero()
        
        # Crear comprobante
        comprobante = cls.objects.create(
            empresa=empresa,
            tipo_comprobante=tipo_comprobante,
            serie=serie_obj.serie,
            numero=numero,
            usuario_creacion=usuario,
            **cliente_data,
            **kwargs
        )
        
        # Almacenar referencia a la serie para validación
        comprobante._serie_obj = serie_obj
        
        # Crear items
        for item_data in items_data:
            ItemComprobante.objects.create(
                comprobante=comprobante,
                **item_data
            )
        
        # Recalcular totales
        comprobante.calcular_totales()
        comprobante.save()
        
        return comprobante


class ItemComprobante(models.Model):
    """
    Modelo para items/líneas de comprobantes
    """
    comprobante = models.ForeignKey(
        Comprobante,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Comprobante'
    )
    
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='items_comprobante',
        verbose_name='Producto'
    )
    
    # Identificación del item
    numero_item = models.PositiveIntegerField(
        verbose_name='Número de Item'
    )
    
    codigo_producto = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Código del Producto'
    )
    
    descripcion = models.CharField(
        max_length=255,
        verbose_name='Descripción'
    )
    
    unidad_medida = models.CharField(
        max_length=10,
        default='NIU',
        verbose_name='Unidad de Medida'
    )
    
    # Cantidades y precios
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Cantidad'
    )
    
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Precio Unitario'
    )
    
    descuento_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Descuento Unitario'
    )
    
    # Impuestos
    base_imponible = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Base Imponible'
    )
    
    igv_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='IGV Unitario'
    )
    
    igv_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='IGV Total'
    )
    
    codigo_impuesto = models.CharField(
        max_length=10,
        default='1000',
        verbose_name='Código de Impuesto'
    )
    
    class Meta:
        db_table = 'items_comprobantes'
        verbose_name = 'Item de Comprobante'
        verbose_name_plural = 'Items de Comprobante'
        unique_together = ['comprobante', 'numero_item']
        ordering = ['numero_item']
        indexes = [
            models.Index(fields=['comprobante']),
            models.Index(fields=['producto']),
        ]
    
    def __str__(self):
        return f"{self.comprobante.numero_completo} - Item {self.numero_item}"
    
    @property
    def precio_unitario_con_descuento(self):
        """Precio unitario después del descuento"""
        return self.precio_unitario - self.descuento_unitario
    
    @property
    def valor_venta(self):
        """Valor de venta total (cantidad * precio con descuento)"""
        return self.cantidad * self.precio_unitario_con_descuento
    
    @property
    def descuento_total(self):
        """Descuento total del item"""
        return self.cantidad * self.descuento_unitario
    
    @property
    def precio_total(self):
        """Precio total con impuestos"""
        return self.valor_venta + self.igv_total
    
    def save(self, *args, **kwargs):
        """Guardar con cálculos automáticos"""
        self.calcular_impuestos()
        super().save(*args, **kwargs)
    
    def calcular_impuestos(self):
        """Calcular impuestos del item"""
        # Obtener tasa de IGV de la empresa
        tasa_igv = self.comprobante.empresa.get_tasa_igv()
        
        # Calcular valor de venta
        valor_venta = self.valor_venta
        
        # Determinar si está afecto a IGV
        afecto_igv = True
        if self.producto:
            afecto_igv = self.producto.afecto_igv
            self.codigo_impuesto = self.producto.codigo_impuesto
        
        if afecto_igv and self.codigo_impuesto == '1000':
            # Operación gravada
            self.base_imponible = valor_venta
            self.igv_unitario = self.precio_unitario_con_descuento * tasa_igv
            self.igv_total = self.cantidad * self.igv_unitario
        else:
            # Operación exonerada, inafecta o gratuita
            self.base_imponible = Decimal('0.00')
            self.igv_unitario = Decimal('0.0000')
            self.igv_total = Decimal('0.00')
        
        # Redondear valores
        self.base_imponible = self.base_imponible.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        self.igv_total = self.igv_total.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    def get_datos_para_xml(self):
        """Obtener datos formateados para XML SUNAT"""
        return {
            'numero_item': self.numero_item,
            'codigo_producto': self.codigo_producto,
            'descripcion': self.descripcion,
            'unidad_medida': self.unidad_medida,
            'cantidad': str(self.cantidad),
            'precio_unitario': str(self.precio_unitario),
            'descuento_unitario': str(self.descuento_unitario),
            'valor_venta': str(self.valor_venta),
            'igv_total': str(self.igv_total),
            'precio_total': str(self.precio_total),
            'codigo_impuesto': self.codigo_impuesto,
        }
    
    def crear_movimiento_inventario(self):
        """Crear movimiento de inventario para este item"""
        if not self.producto or not self.producto.maneja_stock:
            return None
        
        from aplicaciones.inventarios.models import MovimientoInventario
        
        # Determinar almacén (usar almacén principal de la empresa)
        almacen = self.comprobante.empresa.get_almacen_principal()
        if not almacen:
            raise ValueError("No hay almacén principal configurado")
        
        # Crear movimiento de salida
        movimiento = MovimientoInventario.crear_salida(
            empresa=self.comprobante.empresa,
            producto=self.producto,
            almacen=almacen,
            cantidad=self.cantidad,
            referencia_tabla='comprobantes',
            referencia_id=self.comprobante.id,
            numero_documento=self.comprobante.numero_completo,
            observaciones=f"Venta - {self.comprobante.numero_completo}",
            usuario=self.comprobante.usuario_creacion,
            confirmar=True
        )
        
        return movimiento