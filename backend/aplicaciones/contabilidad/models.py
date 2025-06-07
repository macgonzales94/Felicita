"""
MODELOS CONTABILIDAD - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Modelos para el módulo contable según PCGE:
- PlanCuentas
- CuentaContable
- CentroGasto
- AsientoContable
- DetalleAsientoContable
- LibroElectronico
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from aplicaciones.core.models import ModeloBase, Empresa
from aplicaciones.usuarios.models import Usuario
import uuid

# =============================================================================
# MODELO PLAN DE CUENTAS
# =============================================================================
class PlanCuentas(ModeloBase):
    """
    Plan de cuentas contables (PCGE para Perú)
    """
    
    TIPO_PLAN_CHOICES = [
        ('PCGE', 'Plan Contable General Empresarial'),
        ('PCGR', 'Plan Contable General Revisado'),
        ('PERSONALIZADO', 'Plan Personalizado'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='planes_cuentas',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=20,
        verbose_name='Código del Plan'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Plan'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_plan = models.CharField(
        max_length=20,
        choices=TIPO_PLAN_CHOICES,
        default='PCGE',
        verbose_name='Tipo de Plan'
    )
    
    anio_vigencia = models.PositiveIntegerField(
        verbose_name='Año de Vigencia'
    )
    
    es_plan_activo = models.BooleanField(
        default=True,
        verbose_name='Es Plan Activo'
    )
    
    class Meta:
        db_table = 'contabilidad_plan_cuentas'
        verbose_name = 'Plan de Cuentas'
        verbose_name_plural = 'Planes de Cuentas'
        unique_together = ['empresa', 'codigo', 'anio_vigencia']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.anio_vigencia})"

# =============================================================================
# MODELO CUENTA CONTABLE
# =============================================================================
class CuentaContable(ModeloBase):
    """
    Cuentas contables del plan de cuentas
    """
    
    NATURALEZA_CHOICES = [
        ('deudora', 'Deudora'),
        ('acreedora', 'Acreedora'),
    ]
    
    TIPO_CUENTA_CHOICES = [
        ('activo', 'Activo'),
        ('pasivo', 'Pasivo'),
        ('patrimonio', 'Patrimonio'),
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
        ('costo', 'Costo'),
        ('resultado', 'Resultado'),
        ('orden', 'Cuentas de Orden'),
    ]
    
    NIVEL_CHOICES = [
        (1, 'Elemento (1 dígito)'),
        (2, 'Rubro (2 dígitos)'),
        (3, 'Cuenta (3 dígitos)'),
        (4, 'Divisionaria (4 dígitos)'),
        (5, 'Subdivisionaria (5 dígitos)'),
        (6, 'Sub-subdivisionaria (6+ dígitos)'),
    ]
    
    plan_cuentas = models.ForeignKey(
        PlanCuentas,
        on_delete=models.CASCADE,
        related_name='cuentas',
        verbose_name='Plan de Cuentas'
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=20,
        verbose_name='Código de Cuenta'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Cuenta'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Jerarquía
    cuenta_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcuentas',
        verbose_name='Cuenta Padre'
    )
    
    nivel = models.PositiveIntegerField(
        choices=NIVEL_CHOICES,
        verbose_name='Nivel de Cuenta'
    )
    
    # Características contables
    naturaleza = models.CharField(
        max_length=10,
        choices=NATURALEZA_CHOICES,
        verbose_name='Naturaleza'
    )
    
    tipo_cuenta = models.CharField(
        max_length=15,
        choices=TIPO_CUENTA_CHOICES,
        verbose_name='Tipo de Cuenta'
    )
    
    # Control
    acepta_movimientos = models.BooleanField(
        default=True,
        verbose_name='Acepta Movimientos',
        help_text='Las cuentas padre no aceptan movimientos directos'
    )
    
    requiere_centro_gasto = models.BooleanField(
        default=False,
        verbose_name='Requiere Centro de Gasto'
    )
    
    requiere_documento = models.BooleanField(
        default=False,
        verbose_name='Requiere Documento de Sustento'
    )
    
    # Configuración específica Perú
    codigo_sunat = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Código SUNAT',
        help_text='Código para reportes PLE'
    )
    
    incluir_en_balance = models.BooleanField(
        default=True,
        verbose_name='Incluir en Balance'
    )
    
    incluir_en_resultados = models.BooleanField(
        default=False,
        verbose_name='Incluir en Estado de Resultados'
    )
    
    # Saldos
    saldo_inicial_debe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Inicial Debe'
    )
    
    saldo_inicial_haber = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Inicial Haber'
    )
    
    class Meta:
        db_table = 'contabilidad_cuenta_contable'
        verbose_name = 'Cuenta Contable'
        verbose_name_plural = 'Cuentas Contables'
        unique_together = ['plan_cuentas', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['tipo_cuenta']),
            models.Index(fields=['acepta_movimientos']),
        ]
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def get_codigo_completo(self):
        """Retorna el código completo con jerarquía"""
        if self.cuenta_padre:
            return f"{self.cuenta_padre.get_codigo_completo()}.{self.codigo}"
        return self.codigo
    
    def es_cuenta_padre(self):
        """Verifica si la cuenta tiene subcuentas"""
        return self.subcuentas.exists()
    
    def calcular_saldo_actual(self, fecha_hasta=None):
        """Calcula el saldo actual de la cuenta"""
        from django.db.models import Sum
        
        filtros = {'cuenta': self}
        if fecha_hasta:
            filtros['asiento__fecha'] = fecha_hasta
        
        movimientos = DetalleAsientoContable.objects.filter(**filtros)
        
        total_debe = movimientos.aggregate(
            total=Sum('debe')
        )['total'] or Decimal('0.00')
        
        total_haber = movimientos.aggregate(
            total=Sum('haber')
        )['total'] or Decimal('0.00')
        
        saldo_inicial = self.saldo_inicial_debe - self.saldo_inicial_haber
        
        if self.naturaleza == 'deudora':
            return saldo_inicial + total_debe - total_haber
        else:
            return saldo_inicial + total_haber - total_debe

# =============================================================================
# MODELO CENTRO DE GASTO
# =============================================================================
class CentroGasto(ModeloBase):
    """
    Centros de gasto para control presupuestal
    """
    
    TIPO_CENTRO_CHOICES = [
        ('sucursal', 'Sucursal'),
        ('departamento', 'Departamento'),
        ('proyecto', 'Proyecto'),
        ('area', 'Área'),
        ('actividad', 'Actividad'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='centros_gasto',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=20,
        verbose_name='Código'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_centro = models.CharField(
        max_length=15,
        choices=TIPO_CENTRO_CHOICES,
        verbose_name='Tipo de Centro'
    )
    
    centro_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcentros',
        verbose_name='Centro Padre'
    )
    
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='centros_gasto_responsable',
        verbose_name='Responsable'
    )
    
    presupuesto_anual = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Presupuesto Anual'
    )
    
    class Meta:
        db_table = 'contabilidad_centro_gasto'
        verbose_name = 'Centro de Gasto'
        verbose_name_plural = 'Centros de Gasto'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# =============================================================================
# MODELO PERÍODO CONTABLE
# =============================================================================
class PeriodoContable(ModeloBase):
    """
    Períodos contables para control de apertura/cierre
    """
    
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
        ('en_cierre', 'En Proceso de Cierre'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='periodos_contables',
        verbose_name='Empresa'
    )
    
    anio = models.PositiveIntegerField(
        verbose_name='Año'
    )
    
    mes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='Mes'
    )
    
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='abierto',
        verbose_name='Estado'
    )
    
    fecha_cierre = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Cierre'
    )
    
    usuario_cierre = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='periodos_cerrados',
        verbose_name='Usuario que Cerró'
    )
    
    class Meta:
        db_table = 'contabilidad_periodo_contable'
        verbose_name = 'Período Contable'
        verbose_name_plural = 'Períodos Contables'
        unique_together = ['empresa', 'anio', 'mes']
        indexes = [
            models.Index(fields=['anio', 'mes']),
            models.Index(fields=['estado']),
        ]
        ordering = ['-anio', '-mes']
    
    def __str__(self):
        meses = [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        return f"{meses[self.mes]} {self.anio}"
    
    def puede_registrar_asientos(self):
        """Verifica si se pueden registrar asientos en este período"""
        return self.estado == 'abierto'

# =============================================================================
# MODELO ASIENTO CONTABLE
# =============================================================================
class AsientoContable(ModeloBase):
    """
    Asientos contables del sistema
    """
    
    TIPO_ASIENTO_CHOICES = [
        ('apertura', 'Asiento de Apertura'),
        ('diario', 'Asiento del Diario'),
        ('ajuste', 'Asiento de Ajuste'),
        ('cierre', 'Asiento de Cierre'),
        ('automatico', 'Asiento Automático'),
    ]
    
    ORIGEN_CHOICES = [
        ('manual', 'Manual'),
        ('factura', 'Factura'),
        ('boleta', 'Boleta'),
        ('nota_credito', 'Nota de Crédito'),
        ('nota_debito', 'Nota de Débito'),
        ('compra', 'Compra'),
        ('pago', 'Pago'),
        ('cobro', 'Cobro'),
        ('nomina', 'Nómina'),
        ('inventario', 'Inventario'),
        ('banco', 'Movimiento Bancario'),
        ('cierre', 'Cierre Contable'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('validado', 'Validado'),
        ('contabilizado', 'Contabilizado'),
        ('anulado', 'Anulado'),
    ]
    
    # Identificación
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='asientos_contables',
        verbose_name='Empresa'
    )
    
    numero_asiento = models.CharField(
        max_length=20,
        verbose_name='Número de Asiento'
    )
    
    fecha = models.DateField(
        default=timezone.now,
        verbose_name='Fecha del Asiento'
    )
    
    periodo = models.ForeignKey(
        PeriodoContable,
        on_delete=models.PROTECT,
        related_name='asientos',
        verbose_name='Período Contable'
    )
    
    # Clasificación
    tipo_asiento = models.CharField(
        max_length=15,
        choices=TIPO_ASIENTO_CHOICES,
        default='diario',
        verbose_name='Tipo de Asiento'
    )
    
    origen = models.CharField(
        max_length=15,
        choices=ORIGEN_CHOICES,
        default='manual',
        verbose_name='Origen del Asiento'
    )
    
    # Descripción
    concepto = models.TextField(
        verbose_name='Concepto del Asiento'
    )
    
    # Referencia al documento origen
    tipo_documento_origen = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Tipo de Documento de Origen'
    )
    
    numero_documento_origen = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Documento de Origen'
    )
    
    # Totales
    total_debe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Debe'
    )
    
    total_haber = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Haber'
    )
    
    # Control
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='borrador',
        verbose_name='Estado'
    )
    
    es_automatico = models.BooleanField(
        default=False,
        verbose_name='Es Automático',
        help_text='Asiento generado automáticamente por el sistema'
    )
    
    # Usuario y auditoría
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='asientos_registrados',
        verbose_name='Usuario que Registra'
    )
    
    fecha_contabilizacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Contabilización'
    )
    
    usuario_contabilizacion = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='asientos_contabilizados',
        verbose_name='Usuario que Contabiliza'
    )
    
    class Meta:
        db_table = 'contabilidad_asiento_contable'
        verbose_name = 'Asiento Contable'
        verbose_name_plural = 'Asientos Contables'
        unique_together = ['empresa', 'numero_asiento', 'periodo']
        indexes = [
            models.Index(fields=['numero_asiento']),
            models.Index(fields=['fecha']),
            models.Index(fields=['tipo_asiento']),
            models.Index(fields=['origen']),
            models.Index(fields=['estado']),
            models.Index(fields=['periodo']),
        ]
        ordering = ['-fecha', '-numero_asiento']
    
    def __str__(self):
        return f"Asiento {self.numero_asiento} - {self.fecha}"
    
    def save(self, *args, **kwargs):
        """Calcular totales automáticamente"""
        # Los totales se calculan después de guardar los detalles
        super().save(*args, **kwargs)
    
    def calcular_totales(self):
        """Calcula los totales del asiento"""
        from django.db.models import Sum
        
        totales = self.detalles.aggregate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber')
        )
        
        self.total_debe = totales['total_debe'] or Decimal('0.00')
        self.total_haber = totales['total_haber'] or Decimal('0.00')
        
        return self.total_debe, self.total_haber
    
    def esta_cuadrado(self):
        """Verifica si el asiento está cuadrado"""
        self.calcular_totales()
        return self.total_debe == self.total_haber
    
    def puede_ser_contabilizado(self):
        """Verifica si el asiento puede ser contabilizado"""
        return (
            self.estado == 'validado' and
            self.esta_cuadrado() and
            self.periodo.puede_registrar_asientos()
        )
    
    def contabilizar(self, usuario):
        """Contabiliza el asiento"""
        if self.puede_ser_contabilizado():
            self.estado = 'contabilizado'
            self.fecha_contabilizacion = timezone.now()
            self.usuario_contabilizacion = usuario
            self.save(update_fields=['estado', 'fecha_contabilizacion', 'usuario_contabilizacion'])
            return True
        return False

# =============================================================================
# MODELO DETALLE ASIENTO CONTABLE
# =============================================================================
class DetalleAsientoContable(ModeloBase):
    """
    Detalle de los asientos contables (partidas)
    """
    
    asiento = models.ForeignKey(
        AsientoContable,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Asiento Contable'
    )
    
    numero_linea = models.PositiveIntegerField(
        verbose_name='Número de Línea'
    )
    
    cuenta = models.ForeignKey(
        CuentaContable,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Cuenta Contable'
    )
    
    centro_gasto = models.ForeignKey(
        CentroGasto,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='movimientos',
        verbose_name='Centro de Gasto'
    )
    
    # Descripción del movimiento
    concepto = models.TextField(
        verbose_name='Concepto del Movimiento'
    )
    
    # Importes
    debe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Debe'
    )
    
    haber = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Haber'
    )
    
    # Moneda extranjera (si aplica)
    moneda = models.CharField(
        max_length=3,
        default='PEN',
        verbose_name='Moneda'
    )
    
    tipo_cambio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        verbose_name='Tipo de Cambio'
    )
    
    debe_me = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Debe M.E.'
    )
    
    haber_me = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Haber M.E.'
    )
    
    # Documento de sustento
    tipo_documento = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Tipo de Documento'
    )
    
    numero_documento = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Documento'
    )
    
    fecha_documento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha del Documento'
    )
    
    # Datos adicionales para reportes PLE
    codigo_libro = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Código de Libro',
        help_text='Código para PLE 5.1 Libro Diario'
    )
    
    class Meta:
        db_table = 'contabilidad_detalle_asiento_contable'
        verbose_name = 'Detalle de Asiento Contable'
        verbose_name_plural = 'Detalles de Asientos Contables'
        unique_together = ['asiento', 'numero_linea']
        indexes = [
            models.Index(fields=['cuenta']),
            models.Index(fields=['centro_gasto']),
            models.Index(fields=['asiento', 'numero_linea']),
        ]
        ordering = ['numero_linea']
    
    def __str__(self):
        return f"Línea {self.numero_linea} - {self.cuenta.codigo} - {self.concepto[:50]}"
    
    def save(self, *args, **kwargs):
        """Validaciones y cálculos automáticos"""
        # Validar que solo uno de debe o haber tenga valor
        if self.debe > 0 and self.haber > 0:
            raise ValueError("Una línea no puede tener valores en Debe y Haber simultáneamente")
        
        if self.debe == 0 and self.haber == 0:
            raise ValueError("Una línea debe tener valor en Debe o Haber")
        
        # Verificar que la cuenta acepta movimientos
        if not self.cuenta.acepta_movimientos:
            raise ValueError(f"La cuenta {self.cuenta.codigo} no acepta movimientos directos")
        
        # Verificar centro de gasto si es requerido
        if self.cuenta.requiere_centro_gasto and not self.centro_gasto:
            raise ValueError(f"La cuenta {self.cuenta.codigo} requiere centro de gasto")
        
        super().save(*args, **kwargs)
        
        # Recalcular totales del asiento
        self.asiento.calcular_totales()
        self.asiento.save(update_fields=['total_debe', 'total_haber'])

# =============================================================================
# MODELO LIBRO ELECTRÓNICO PLE
# =============================================================================
class LibroElectronico(ModeloBase):
    """
    Libros electrónicos PLE para SUNAT
    """
    
    TIPO_LIBRO_CHOICES = [
        ('5.1', '5.1 - Libro Diario'),
        ('5.2', '5.2 - Libro Mayor'),
        ('6.1', '6.1 - Libro de Inventarios y Balances - Balance de Comprobación'),
        ('3.1', '3.1 - Libro de Inventarios y Balances - Inventario Permanente Valorizado'),
        ('8.1', '8.1 - Registro de Compras'),
        ('14.1', '14.1 - Registro de Ventas e Ingresos'),
    ]
    
    ESTADO_CHOICES = [
        ('generando', 'Generando'),
        ('generado', 'Generado'),
        ('enviado', 'Enviado a SUNAT'),
        ('error', 'Error'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='libros_electronicos',
        verbose_name='Empresa'
    )
    
    tipo_libro = models.CharField(
        max_length=5,
        choices=TIPO_LIBRO_CHOICES,
        verbose_name='Tipo de Libro'
    )
    
    periodo = models.ForeignKey(
        PeriodoContable,
        on_delete=models.PROTECT,
        related_name='libros_electronicos',
        verbose_name='Período'
    )
    
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Generación'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='generando',
        verbose_name='Estado'
    )
    
    archivo_txt = models.FileField(
        upload_to='ple/txt/',
        blank=True,
        null=True,
        verbose_name='Archivo TXT'
    )
    
    archivo_excel = models.FileField(
        upload_to='ple/excel/',
        blank=True,
        null=True,
        verbose_name='Archivo Excel'
    )
    
    hash_archivo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Hash del Archivo'
    )
    
    numero_registros = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de Registros'
    )
    
    usuario_generacion = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='libros_ple_generados',
        verbose_name='Usuario que Genera'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    class Meta:
        db_table = 'contabilidad_libro_electronico'
        verbose_name = 'Libro Electrónico PLE'
        verbose_name_plural = 'Libros Electrónicos PLE'
        unique_together = ['empresa', 'tipo_libro', 'periodo']
        indexes = [
            models.Index(fields=['tipo_libro']),
            models.Index(fields=['periodo']),
            models.Index(fields=['estado']),
        ]
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"PLE {self.tipo_libro} - {self.periodo} - {self.empresa.razon_social}"