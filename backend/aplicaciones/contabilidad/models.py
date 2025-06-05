"""
Modelos de contabilidad para FELICITA
Sistema de Facturación Electrónica para Perú
Implementa Plan Contable General Empresarial (PCGE)
"""

from django.db import models, transaction
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime


class TipoCuenta(models.TextChoices):
    """Tipos de cuenta según PCGE"""
    ACTIVO = 'ACTIVO', 'Activo'
    PASIVO = 'PASIVO', 'Pasivo'
    PATRIMONIO = 'PATRIMONIO', 'Patrimonio'
    INGRESOS = 'INGRESOS', 'Ingresos'
    GASTOS = 'GASTOS', 'Gastos'
    CUENTAS_ORDEN = 'CUENTAS_ORDEN', 'Cuentas de Orden'


class Naturaleza(models.TextChoices):
    """Naturaleza de las cuentas contables"""
    DEUDOR = 'DEUDOR', 'Deudor'
    ACREEDOR = 'ACREEDOR', 'Acreedor'


class EstadoAsiento(models.TextChoices):
    """Estados de asientos contables"""
    BORRADOR = 'BORRADOR', 'Borrador'
    CONFIRMADO = 'CONFIRMADO', 'Confirmado'
    ANULADO = 'ANULADO', 'Anulado'


class PlanCuentas(models.Model):
    """
    Modelo para Plan Contable General Empresarial (PCGE)
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='plan_cuentas',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[\d\.]+$',
            message='El código debe contener solo números y puntos'
        )],
        verbose_name='Código de Cuenta',
        help_text='Código según PCGE (ej: 10.1.1.01)'
    )
    
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre de la Cuenta'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada de la cuenta'
    )
    
    # Jerarquía
    cuenta_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcuentas',
        verbose_name='Cuenta Padre'
    )
    
    nivel = models.PositiveIntegerField(
        verbose_name='Nivel',
        help_text='Nivel en la jerarquía del plan de cuentas'
    )
    
    # Configuración de la cuenta
    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TipoCuenta.choices,
        verbose_name='Tipo de Cuenta'
    )
    
    naturaleza = models.CharField(
        max_length=10,
        choices=Naturaleza.choices,
        default=Naturaleza.DEUDOR,
        verbose_name='Naturaleza'
    )
    
    acepta_movimientos = models.BooleanField(
        default=True,
        verbose_name='Acepta Movimientos',
        help_text='Si la cuenta puede tener movimientos contables'
    )
    
    requiere_documento = models.BooleanField(
        default=False,
        verbose_name='Requiere Documento',
        help_text='Si requiere número de documento en asientos'
    )
    
    requiere_referencia = models.BooleanField(
        default=False,
        verbose_name='Requiere Referencia',
        help_text='Si requiere referencia adicional en asientos'
    )
    
    # Configuración adicional
    moneda_extranjera = models.BooleanField(
        default=False,
        verbose_name='Maneja Moneda Extranjera',
        help_text='Si la cuenta maneja operaciones en moneda extranjera'
    )
    
    centro_costo = models.BooleanField(
        default=False,
        verbose_name='Maneja Centro de Costo',
        help_text='Si la cuenta requiere centro de costo'
    )
    
    # Cuentas especiales del sistema
    cuenta_ventas = models.BooleanField(
        default=False,
        verbose_name='Cuenta de Ventas',
        help_text='Cuenta utilizada para registrar ventas'
    )
    
    cuenta_compras = models.BooleanField(
        default=False,
        verbose_name='Cuenta de Compras',
        help_text='Cuenta utilizada para registrar compras'
    )
    
    cuenta_igv = models.BooleanField(
        default=False,
        verbose_name='Cuenta de IGV',
        help_text='Cuenta utilizada para registrar IGV'
    )
    
    cuenta_caja = models.BooleanField(
        default=False,
        verbose_name='Cuenta de Caja',
        help_text='Cuenta de efectivo en caja'
    )
    
    cuenta_banco = models.BooleanField(
        default=False,
        verbose_name='Cuenta de Banco',
        help_text='Cuenta bancaria'
    )
    
    # Estado y auditoria
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
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
        db_table = 'plan_cuentas'
        verbose_name = 'Cuenta Contable'
        verbose_name_plural = 'Plan de Cuentas'
        unique_together = ['empresa', 'codigo']
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['empresa', 'codigo']),
            models.Index(fields=['cuenta_padre']),
            models.Index(fields=['tipo_cuenta']),
            models.Index(fields=['acepta_movimientos']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones y cálculo automático de nivel"""
        # Calcular nivel automáticamente
        if self.cuenta_padre:
            self.nivel = self.cuenta_padre.nivel + 1
        else:
            self.nivel = len(self.codigo.split('.'))
        
        # Validar que las cuentas padre no acepten movimientos
        if self.acepta_movimientos and self.subcuentas.exists():
            raise ValueError("Las cuentas con subcuentas no pueden aceptar movimientos")
        
        super().save(*args, **kwargs)
        
        # Si esta cuenta ahora tiene subcuentas, no debe aceptar movimientos
        if self.subcuentas.exists():
            self.acepta_movimientos = False
            super().save(update_fields=['acepta_movimientos'])
    
    def get_ruta_completa(self):
        """Obtener ruta completa de la cuenta"""
        if self.cuenta_padre:
            return f"{self.cuenta_padre.get_ruta_completa()} > {self.nombre}"
        return self.nombre
    
    def get_subcuentas_activas(self):
        """Obtener subcuentas activas"""
        return self.subcuentas.filter(activo=True)
    
    def get_saldo_actual(self, fecha_hasta=None):
        """Obtener saldo actual de la cuenta"""
        if not self.acepta_movimientos:
            # Para cuentas padre, sumar saldos de subcuentas
            saldo_total = Decimal('0.00')
            for subcuenta in self.get_subcuentas_activas():
                saldo_total += subcuenta.get_saldo_actual(fecha_hasta)
            return saldo_total
        
        # Filtro base
        movimientos = self.movimientos.filter(
            asiento__estado=EstadoAsiento.CONFIRMADO
        )
        
        # Filtrar por fecha si se especifica
        if fecha_hasta:
            movimientos = movimientos.filter(
                asiento__fecha_asiento__lte=fecha_hasta
            )
        
        # Calcular saldo según naturaleza
        totales = movimientos.aggregate(
            total_debe=models.Sum('debe'),
            total_haber=models.Sum('haber')
        )
        
        debe = totales['total_debe'] or Decimal('0.00')
        haber = totales['total_haber'] or Decimal('0.00')
        
        if self.naturaleza == Naturaleza.DEUDOR:
            return debe - haber
        else:
            return haber - debe
    
    def get_movimientos_periodo(self, fecha_desde, fecha_hasta):
        """Obtener movimientos en un período"""
        return self.movimientos.filter(
            asiento__estado=EstadoAsiento.CONFIRMADO,
            asiento__fecha_asiento__range=[fecha_desde, fecha_hasta]
        ).order_by('asiento__fecha_asiento', 'asiento__numero_asiento')
    
    def puede_eliminar(self):
        """Verificar si la cuenta puede ser eliminada"""
        return (
            not self.movimientos.exists() and
            not self.subcuentas.exists()
        )
    
    def activar(self):
        """Activar cuenta"""
        self.activo = True
        self.save(update_fields=['activo'])
    
    def desactivar(self):
        """Desactivar cuenta"""
        if self.movimientos.filter(asiento__estado=EstadoAsiento.CONFIRMADO).exists():
            raise ValueError("No se puede desactivar una cuenta con movimientos confirmados")
        
        self.activo = False
        self.save(update_fields=['activo'])
    
    @classmethod
    def obtener_cuenta_ventas(cls, empresa):
        """Obtener cuenta principal de ventas"""
        return cls.objects.filter(
            empresa=empresa,
            cuenta_ventas=True,
            activo=True
        ).first()
    
    @classmethod
    def obtener_cuenta_igv(cls, empresa):
        """Obtener cuenta de IGV por pagar"""
        return cls.objects.filter(
            empresa=empresa,
            cuenta_igv=True,
            activo=True
        ).first()
    
    @classmethod
    def obtener_cuenta_caja(cls, empresa):
        """Obtener cuenta principal de caja"""
        return cls.objects.filter(
            empresa=empresa,
            cuenta_caja=True,
            activo=True
        ).first()


class AsientoContable(models.Model):
    """
    Modelo para asientos contables
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='asientos_contables',
        verbose_name='Empresa'
    )
    
    numero_asiento = models.PositiveIntegerField(
        verbose_name='Número de Asiento'
    )
    
    fecha_asiento = models.DateField(
        default=timezone.now,
        verbose_name='Fecha del Asiento'
    )
    
    concepto = models.TextField(
        verbose_name='Concepto',
        help_text='Descripción del asiento contable'
    )
    
    # Referencia al documento origen
    referencia_tabla = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tabla de Referencia',
        help_text='Tabla que origina el asiento (comprobantes, pagos, etc.)'
    )
    
    referencia_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID de Referencia',
        help_text='ID del registro que origina el asiento'
    )
    
    # Totales del asiento
    total_debe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Debe'
    )
    
    total_haber = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Haber'
    )
    
    # Estado y configuración
    estado = models.CharField(
        max_length=20,
        choices=EstadoAsiento.choices,
        default=EstadoAsiento.BORRADOR,
        verbose_name='Estado'
    )
    
    automatico = models.BooleanField(
        default=False,
        verbose_name='Asiento Automático',
        help_text='Si fue generado automáticamente por el sistema'
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    moneda = models.CharField(
        max_length=3,
        default='PEN',
        verbose_name='Moneda'
    )
    
    tipo_cambio = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal('1.0000'),
        verbose_name='Tipo de Cambio'
    )
    
    # Auditoria
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Confirmación'
    )
    
    usuario_creacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asientos_creados',
        verbose_name='Usuario que Creó'
    )
    
    usuario_confirmacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asientos_confirmados',
        verbose_name='Usuario que Confirmó'
    )
    
    class Meta:
        db_table = 'asientos_contables'
        verbose_name = 'Asiento Contable'
        verbose_name_plural = 'Asientos Contables'
        unique_together = ['empresa', 'numero_asiento']
        ordering = ['-fecha_asiento', '-numero_asiento']
        indexes = [
            models.Index(fields=['empresa', 'fecha_asiento']),
            models.Index(fields=['estado']),
            models.Index(fields=['referencia_tabla', 'referencia_id']),
            models.Index(fields=['automatico']),
        ]
    
    def __str__(self):
        return f"Asiento {self.numero_asiento} - {self.fecha_asiento}"
    
    @property
    def periodo(self):
        """Período contable del asiento (YYYY-MM)"""
        return self.fecha_asiento.strftime('%Y-%m')
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones y numeración automática"""
        # Asignar número automático si no existe
        if not self.numero_asiento:
            self.numero_asiento = self._obtener_siguiente_numero()
        
        # Calcular totales
        self.calcular_totales()
        
        # Validar cuadre
        self.validar_cuadre()
        
        super().save(*args, **kwargs)
    
    def _obtener_siguiente_numero(self):
        """Obtener siguiente número de asiento"""
        ultimo_asiento = AsientoContable.objects.filter(
            empresa=self.empresa
        ).aggregate(
            max_numero=models.Max('numero_asiento')
        )['max_numero']
        
        return (ultimo_asiento or 0) + 1
    
    def calcular_totales(self):
        """Calcular totales debe y haber"""
        totales = self.detalles.aggregate(
            total_debe=models.Sum('debe'),
            total_haber=models.Sum('haber')
        )
        
        self.total_debe = totales['total_debe'] or Decimal('0.00')
        self.total_haber = totales['total_haber'] or Decimal('0.00')
    
    def validar_cuadre(self):
        """Validar que el asiento esté cuadrado"""
        diferencia = abs(self.total_debe - self.total_haber)
        tolerancia = Decimal('0.01')
        
        if diferencia > tolerancia:
            raise ValueError(f"El asiento no está cuadrado. Diferencia: {diferencia}")
    
    def confirmar(self, usuario=None):
        """Confirmar el asiento contable"""
        if self.estado == EstadoAsiento.CONFIRMADO:
            raise ValueError("El asiento ya está confirmado")
        
        if self.estado == EstadoAsiento.ANULADO:
            raise ValueError("No se puede confirmar un asiento anulado")
        
        # Validar que tenga detalles
        if not self.detalles.exists():
            raise ValueError("El asiento debe tener al menos un detalle")
        
        # Recalcular totales y validar cuadre
        self.calcular_totales()
        self.validar_cuadre()
        
        # Confirmar asiento
        self.estado = EstadoAsiento.CONFIRMADO
        self.fecha_confirmacion = timezone.now()
        self.usuario_confirmacion = usuario
        self.save()
    
    def anular(self, motivo=""):
        """Anular el asiento contable"""
        if self.estado == EstadoAsiento.ANULADO:
            raise ValueError("El asiento ya está anulado")
        
        self.estado = EstadoAsiento.ANULADO
        if motivo:
            self.observaciones += f"\n\nANULADO: {motivo}"
        self.save()
    
    def duplicar(self, nueva_fecha=None, nuevo_concepto=None):
        """Duplicar el asiento con nueva fecha"""
        nuevo_asiento = AsientoContable.objects.create(
            empresa=self.empresa,
            fecha_asiento=nueva_fecha or self.fecha_asiento,
            concepto=nuevo_concepto or f"COPIA - {self.concepto}",
            observaciones=self.observaciones,
            moneda=self.moneda,
            tipo_cambio=self.tipo_cambio,
            usuario_creacion=self.usuario_creacion,
        )
        
        # Duplicar detalles
        for detalle in self.detalles.all():
            DetalleAsiento.objects.create(
                asiento=nuevo_asiento,
                cuenta=detalle.cuenta,
                numero_detalle=detalle.numero_detalle,
                descripcion=detalle.descripcion,
                debe=detalle.debe,
                haber=detalle.haber,
                documento=detalle.documento,
                referencia=detalle.referencia,
            )
        
        return nuevo_asiento
    
    @classmethod
    def crear_asiento_venta(cls, empresa, comprobante, usuario=None):
        """Crear asiento contable automático para venta"""
        # Obtener cuentas necesarias
        cuenta_ventas = PlanCuentas.obtener_cuenta_ventas(empresa)
        cuenta_igv = PlanCuentas.obtener_cuenta_igv(empresa)
        cuenta_caja = PlanCuentas.obtener_cuenta_caja(empresa)
        
        if not all([cuenta_ventas, cuenta_igv, cuenta_caja]):
            raise ValueError("No se encontraron todas las cuentas necesarias para el asiento")
        
        # Crear asiento
        asiento = cls.objects.create(
            empresa=empresa,
            fecha_asiento=comprobante.fecha_emision,
            concepto=f"Venta {comprobante.numero_completo} - {comprobante.cliente_razon_social}",
            referencia_tabla='comprobantes',
            referencia_id=comprobante.id,
            automatico=True,
            usuario_creacion=usuario,
        )
        
        # Detalle 1: Cargo a Caja (Total con IGV)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta=cuenta_caja,
            numero_detalle=1,
            descripcion=f"Venta {comprobante.numero_completo}",
            debe=comprobante.total_con_impuestos,
            haber=Decimal('0.00'),
            documento=comprobante.numero_completo,
        )
        
        # Detalle 2: Abono a Ventas (Subtotal)
        DetalleAsiento.objects.create(
            asiento=asiento,
            cuenta=cuenta_ventas,
            numero_detalle=2,
            descripcion=f"Venta {comprobante.numero_completo}",
            debe=Decimal('0.00'),
            haber=comprobante.base_imponible,
            documento=comprobante.numero_completo,
        )
        
        # Detalle 3: Abono a IGV por Pagar (si hay IGV)
        if comprobante.total_igv > 0:
            DetalleAsiento.objects.create(
                asiento=asiento,
                cuenta=cuenta_igv,
                numero_detalle=3,
                descripcion=f"IGV Venta {comprobante.numero_completo}",
                debe=Decimal('0.00'),
                haber=comprobante.total_igv,
                documento=comprobante.numero_completo,
            )
        
        # Confirmar asiento automáticamente
        asiento.confirmar(usuario)
        
        return asiento


class DetalleAsiento(models.Model):
    """
    Modelo para detalles/líneas de asientos contables
    """
    asiento = models.ForeignKey(
        AsientoContable,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Asiento'
    )
    
    cuenta = models.ForeignKey(
        PlanCuentas,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Cuenta'
    )
    
    numero_detalle = models.PositiveIntegerField(
        verbose_name='Número de Detalle'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    
    debe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Debe'
    )
    
    haber = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Haber'
    )
    
    # Información adicional
    documento = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Documento',
        help_text='Número de documento relacionado'
    )
    
    referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Referencia',
        help_text='Referencia adicional'
    )
    
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento',
        help_text='Para cuentas por cobrar/pagar'
    )
    
    # Moneda extranjera
    moneda = models.CharField(
        max_length=3,
        default='PEN',
        verbose_name='Moneda'
    )
    
    importe_moneda_extranjera = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Importe en Moneda Extranjera'
    )
    
    tipo_cambio = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal('1.0000'),
        verbose_name='Tipo de Cambio'
    )
    
    class Meta:
        db_table = 'detalles_asientos'
        verbose_name = 'Detalle de Asiento'
        verbose_name_plural = 'Detalles de Asiento'
        unique_together = ['asiento', 'numero_detalle']
        ordering = ['numero_detalle']
        indexes = [
            models.Index(fields=['asiento']),
            models.Index(fields=['cuenta']),
        ]
    
    def __str__(self):
        return f"Asiento {self.asiento.numero_asiento} - Detalle {self.numero_detalle}"
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones"""
        # Validar que la cuenta acepta movimientos
        if not self.cuenta.acepta_movimientos:
            raise ValueError("La cuenta seleccionada no acepta movimientos")
        
        # Validar que debe o haber sea mayor a cero (pero no ambos)
        if self.debe > 0 and self.haber > 0:
            raise ValueError("Un detalle no puede tener valores en debe y haber simultáneamente")
        
        if self.debe == 0 and self.haber == 0:
            raise ValueError("Un detalle debe tener valor en debe o haber")
        
        # Calcular importe en moneda extranjera si es necesario
        if self.moneda != 'PEN' and not self.importe_moneda_extranjera:
            if self.debe > 0:
                self.importe_moneda_extranjera = self.debe / self.tipo_cambio
            else:
                self.importe_moneda_extranjera = self.haber / self.tipo_cambio
        
        super().save(*args, **kwargs)
    
    def get_importe_total(self):
        """Obtener importe total (debe o haber)"""
        return self.debe if self.debe > 0 else self.haber
    
    def es_cargo(self):
        """Verificar si es un cargo (debe)"""
        return self.debe > 0
    
    def es_abono(self):
        """Verificar si es un abono (haber)"""
        return self.haber > 0


class CuentaPorCobrar(models.Model):
    """
    Modelo para cuentas por cobrar
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='cuentas_por_cobrar',
        verbose_name='Empresa'
    )
    
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='cuentas_por_cobrar',
        verbose_name='Cliente'
    )
    
    comprobante = models.ForeignKey(
        'facturacion.Comprobante',
        on_delete=models.PROTECT,
        related_name='cuentas_por_cobrar',
        verbose_name='Comprobante'
    )
    
    numero_documento = models.CharField(
        max_length=50,
        verbose_name='Número de Documento'
    )
    
    fecha_emision = models.DateField(
        verbose_name='Fecha de Emisión'
    )
    
    fecha_vencimiento = models.DateField(
        verbose_name='Fecha de Vencimiento'
    )
    
    moneda = models.CharField(
        max_length=3,
        default='PEN',
        verbose_name='Moneda'
    )
    
    importe_original = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Importe Original'
    )
    
    importe_pendiente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Importe Pendiente'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('PARCIAL', 'Pagado Parcial'),
            ('PAGADO', 'Pagado'),
            ('VENCIDO', 'Vencido'),
        ],
        default='PENDIENTE',
        verbose_name='Estado'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        db_table = 'cuentas_por_cobrar'
        verbose_name = 'Cuenta por Cobrar'
        verbose_name_plural = 'Cuentas por Cobrar'
        ordering = ['fecha_vencimiento', 'fecha_emision']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['cliente']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['comprobante']),
        ]
    
    def __str__(self):
        return f"{self.numero_documento} - {self.cliente.razon_social}"
    
    @property
    def importe_pagado(self):
        """Importe pagado"""
        return self.importe_original - self.importe_pendiente
    
    @property
    def dias_vencimiento(self):
        """Días de vencimiento (negativos si está vencido)"""
        return (self.fecha_vencimiento - timezone.now().date()).days
    
    def esta_vencido(self):
        """Verificar si está vencido"""
        return timezone.now().date() > self.fecha_vencimiento
    
    def get_pagos(self):
        """Obtener pagos aplicados a esta cuenta"""
        return self.pagos.all()
    
    def aplicar_pago(self, importe, fecha_pago, referencia="", usuario=None):
        """Aplicar un pago a la cuenta por cobrar"""
        if importe > self.importe_pendiente:
            raise ValueError("El importe del pago no puede ser mayor al pendiente")
        
        # Crear el pago
        pago = PagoCuentaPorCobrar.objects.create(
            cuenta_por_cobrar=self,
            importe=importe,
            fecha_pago=fecha_pago,
            referencia=referencia,
            usuario=usuario,
        )
        
        # Actualizar importe pendiente
        self.importe_pendiente -= importe
        
        # Actualizar estado
        if self.importe_pendiente <= 0:
            self.estado = 'PAGADO'
        elif self.importe_pendiente < self.importe_original:
            self.estado = 'PARCIAL'
        
        self.save()
        
        return pago
    
    @classmethod
    def crear_desde_comprobante(cls, comprobante):
        """Crear cuenta por cobrar desde comprobante"""
        if comprobante.forma_pago == 'CONTADO':
            return None
        
        dias_credito = comprobante.cliente.get_dias_credito() if comprobante.cliente else 30
        fecha_vencimiento = comprobante.fecha_emision + timezone.timedelta(days=dias_credito)
        
        cuenta = cls.objects.create(
            empresa=comprobante.empresa,
            cliente=comprobante.cliente,
            comprobante=comprobante,
            numero_documento=comprobante.numero_completo,
            fecha_emision=comprobante.fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            moneda=comprobante.moneda,
            importe_original=comprobante.total_con_impuestos,
            importe_pendiente=comprobante.total_con_impuestos,
        )
        
        return cuenta


class PagoCuentaPorCobrar(models.Model):
    """
    Modelo para pagos de cuentas por cobrar
    """
    cuenta_por_cobrar = models.ForeignKey(
        CuentaPorCobrar,
        on_delete=models.CASCADE,
        related_name='pagos',
        verbose_name='Cuenta por Cobrar'
    )
    
    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Importe'
    )
    
    fecha_pago = models.DateField(
        verbose_name='Fecha de Pago'
    )
    
    referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Referencia',
        help_text='Número de recibo, transferencia, etc.'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        db_table = 'pagos_cuentas_por_cobrar'
        verbose_name = 'Pago de Cuenta por Cobrar'
        verbose_name_plural = 'Pagos de Cuentas por Cobrar'
        ordering = ['-fecha_pago']
    
    def __str__(self):
        return f"Pago {self.importe} - {self.cuenta_por_cobrar.numero_documento}"