"""
MODELOS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Modelos base y entidades principales del sistema:
- Empresa
- Cliente  
- Proveedor
- Producto
- Configuraciones generales
"""

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

# =============================================================================
# MODELO BASE ABSTRACTO
# =============================================================================
class ModeloBase(models.Model):
    """
    Modelo base abstracto con campos comunes para auditoría
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado en'
    )
    
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado en'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        abstract = True
        ordering = ['-creado_en']

# =============================================================================
# VALIDADORES PERSONALIZADOS PERÚ
# =============================================================================
validador_ruc = RegexValidator(
    regex=r'^\d{11}$',
    message='El RUC debe tener exactamente 11 dígitos'
)

validador_dni = RegexValidator(
    regex=r'^\d{8}$',
    message='El DNI debe tener exactamente 8 dígitos'
)

validador_telefono = RegexValidator(
    regex=r'^(\+51\s?)?(\d{2,3}\s?)?[\d\s-]{6,9}$',
    message='Formato de teléfono inválido'
)

# =============================================================================
# MODELO EMPRESA
# =============================================================================
class Empresa(ModeloBase):
    """
    Modelo para la empresa emisora de comprobantes
    """
    
    # Datos principales
    ruc = models.CharField(
        max_length=11,
        unique=True,
        validators=[validador_ruc],
        verbose_name='RUC',
        help_text='Registro Único de Contribuyente'
    )
    
    razon_social = models.CharField(
        max_length=200,
        verbose_name='Razón Social'
    )
    
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre Comercial'
    )
    
    # Dirección
    direccion = models.TextField(
        verbose_name='Dirección'
    )
    
    ubigeo = models.CharField(
        max_length=6,
        verbose_name='Ubigeo INEI',
        help_text='Código de ubigeo INEI de 6 dígitos'
    )
    
    distrito = models.CharField(
        max_length=100,
        verbose_name='Distrito'
    )
    
    provincia = models.CharField(
        max_length=100,
        verbose_name='Provincia'
    )
    
    departamento = models.CharField(
        max_length=100,
        verbose_name='Departamento'
    )
    
    # Contacto
    telefono = models.CharField(
        max_length=20,
        validators=[validador_telefono],
        blank=True,
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        verbose_name='Email'
    )
    
    pagina_web = models.URLField(
        blank=True,
        verbose_name='Página Web'
    )
    
    # Configuración contable
    plan_cuentas = models.CharField(
        max_length=10,
        default='PCGE',
        choices=[
            ('PCGE', 'Plan Contable General Empresarial'),
            ('PCGR', 'Plan Contable General Revisado'),
        ],
        verbose_name='Plan de Cuentas'
    )
    
    moneda_base = models.CharField(
        max_length=3,
        default='PEN',
        choices=[
            ('PEN', 'Nuevos Soles'),
            ('USD', 'Dólares Americanos'),
            ('EUR', 'Euros'),
        ],
        verbose_name='Moneda Base'
    )
    
    # Configuración facturación
    regimen_tributario = models.CharField(
        max_length=50,
        choices=[
            ('GENERAL', 'Régimen General'),
            ('ESPECIAL', 'Régimen Especial de Renta'),
            ('MYPE', 'Régimen MYPE Tributario'),
            ('RUS', 'Nuevo RUS'),
        ],
        default='GENERAL',
        verbose_name='Régimen Tributario'
    )
    
    logo = models.ImageField(
        upload_to='empresas/logos/',
        blank=True,
        null=True,
        verbose_name='Logo'
    )
    
    class Meta:
        db_table = 'core_empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
    
    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"
    
    def validar_ruc(self):
        """Validar RUC con algoritmo SUNAT"""
        if len(self.ruc) != 11:
            return False
        
        # Algoritmo de validación RUC SUNAT
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(self.ruc[i]) * factores[i] for i in range(10))
        resto = suma % 11
        digito_verificador = 11 - resto if resto >= 2 else resto
        
        return digito_verificador == int(self.ruc[10])

# =============================================================================
# MODELO CLIENTE
# =============================================================================
class Cliente(ModeloBase):
    """
    Modelo para clientes del sistema
    """
    
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'DNI - Documento Nacional de Identidad'),
        ('RUC', 'RUC - Registro Único de Contribuyente'),
        ('CE', 'CE - Carnet de Extranjería'),
        ('PASSPORT', 'Pasaporte'),
        ('OTROS', 'Otros documentos'),
    ]
    
    TIPO_CLIENTE_CHOICES = [
        ('PERSONA_NATURAL', 'Persona Natural'),
        ('PERSONA_JURIDICA', 'Persona Jurídica'),
        ('NO_DOMICILIADO', 'No Domiciliado'),
    ]
    
    # Identificación
    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='DNI',
        verbose_name='Tipo de Documento'
    )
    
    numero_documento = models.CharField(
        max_length=20,
        verbose_name='Número de Documento'
    )
    
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        default='PERSONA_NATURAL',
        verbose_name='Tipo de Cliente'
    )
    
    # Datos personales/empresariales
    razon_social = models.CharField(
        max_length=200,
        verbose_name='Razón Social / Nombres'
    )
    
    nombres = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nombres'
    )
    
    apellido_paterno = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Apellido Paterno'
    )
    
    apellido_materno = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Apellido Materno'
    )
    
    # Dirección
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
    
    provincia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Provincia'
    )
    
    departamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Departamento'
    )
    
    # Contacto
    telefono = models.CharField(
        max_length=20,
        blank=True,
        validators=[validador_telefono],
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    # Configuración comercial
    limite_credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Límite de Crédito'
    )
    
    dias_credito = models.PositiveIntegerField(
        default=0,
        verbose_name='Días de Crédito'
    )
    
    descuento_maximo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name='Descuento Máximo (%)'
    )
    
    # Estado
    bloqueado = models.BooleanField(
        default=False,
        verbose_name='Cliente Bloqueado'
    )
    
    fecha_bloqueo = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Bloqueo'
    )
    
    motivo_bloqueo = models.TextField(
        blank=True,
        verbose_name='Motivo de Bloqueo'
    )
    
    class Meta:
        db_table = 'core_cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ['tipo_documento', 'numero_documento']
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['razon_social']),
            models.Index(fields=['tipo_cliente']),
        ]
    
    def __str__(self):
        return f"{self.numero_documento} - {self.razon_social}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        if self.tipo_cliente == 'PERSONA_NATURAL':
            return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()
        return self.razon_social
    
    def validar_documento(self):
        """Validar número de documento según tipo"""
        if self.tipo_documento == 'DNI':
            return len(self.numero_documento) == 8 and self.numero_documento.isdigit()
        elif self.tipo_documento == 'RUC':
            return len(self.numero_documento) == 11 and self.numero_documento.isdigit()
        return True

# =============================================================================
# MODELO PROVEEDOR
# =============================================================================
class Proveedor(ModeloBase):
    """
    Modelo para proveedores del sistema
    """
    
    # Identificación
    ruc = models.CharField(
        max_length=11,
        unique=True,
        validators=[validador_ruc],
        verbose_name='RUC'
    )
    
    razon_social = models.CharField(
        max_length=200,
        verbose_name='Razón Social'
    )
    
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre Comercial'
    )
    
    # Dirección
    direccion = models.TextField(
        verbose_name='Dirección'
    )
    
    ubigeo = models.CharField(
        max_length=6,
        blank=True,
        verbose_name='Ubigeo'
    )
    
    # Contacto
    telefono = models.CharField(
        max_length=20,
        blank=True,
        validators=[validador_telefono],
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    contacto_principal = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Contacto Principal'
    )
    
    # Configuración comercial
    dias_pago = models.PositiveIntegerField(
        default=30,
        verbose_name='Días de Pago'
    )
    
    descuento_obtenido = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name='Descuento Obtenido (%)'
    )
    
    # Estado
    activo_comercial = models.BooleanField(
        default=True,
        verbose_name='Activo Comercialmente'
    )
    
    class Meta:
        db_table = 'core_proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        indexes = [
            models.Index(fields=['ruc']),
            models.Index(fields=['razon_social']),
        ]
    
    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"

# =============================================================================
# MODELO CATEGORÍA PRODUCTO
# =============================================================================
class CategoriaProducto(ModeloBase):
    """
    Categorías para organizar productos
    """
    
    codigo = models.CharField(
        max_length=10,
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
    
    categoria_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcategorias',
        verbose_name='Categoría Padre'
    )
    
    class Meta:
        db_table = 'core_categoria_producto'
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# =============================================================================
# MODELO PRODUCTO
# =============================================================================
class Producto(ModeloBase):
    """
    Modelo para productos del sistema
    """
    
    TIPO_PRODUCTO_CHOICES = [
        ('BIEN', 'Bien'),
        ('SERVICIO', 'Servicio'),
    ]
    
    TIPO_AFECTACION_IGV_CHOICES = [
        ('10', 'Gravado - Operación Onerosa'),
        ('11', 'Gravado - Retiro por premio'),
        ('12', 'Gravado - Retiro por donación'),
        ('13', 'Gravado - Retiro'),
        ('14', 'Gravado - Retiro por publicidad'),
        ('15', 'Gravado - Bonificaciones'),
        ('16', 'Gravado - Retiro por entrega a trabajadores'),
        ('17', 'Gravado - IVAP'),
        ('20', 'Exonerado - Operación Onerosa'),
        ('21', 'Exonerado - Transferencia Gratuita'),
        ('30', 'Inafecto - Operación Onerosa'),
        ('31', 'Inafecto - Retiro por Bonificación'),
        ('32', 'Inafecto - Retiro'),
        ('33', 'Inafecto - Retiro por Muestras Médicas'),
        ('34', 'Inafecto - Retiro por Convenio Colectivo'),
        ('35', 'Inafecto - Retiro por premio'),
        ('36', 'Inafecto - Retiro por publicidad'),
        ('40', 'Exportación de Bienes o Servicios'),
    ]
    
    # Identificación
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código'
    )
    
    codigo_barras = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        null=True,
        verbose_name='Código de Barras'
    )
    
    codigo_sunat = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Código SUNAT',
        help_text='Código de producto según catálogo SUNAT'
    )
    
    # Descripción
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_producto = models.CharField(
        max_length=10,
        choices=TIPO_PRODUCTO_CHOICES,
        default='BIEN',
        verbose_name='Tipo de Producto'
    )
    
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        verbose_name='Categoría'
    )
    
    # Unidades de medida
    unidad_medida = models.CharField(
        max_length=10,
        default='NIU',
        verbose_name='Unidad de Medida',
        help_text='Código según catálogo SUNAT (NIU=Unidad)'
    )
    
    # Precios
    precio_compra = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Precio de Compra'
    )
    
    precio_venta = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Precio de Venta'
    )
    
    precio_venta_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Precio de Venta Mínimo'
    )
    
    # Configuración tributaria
    tipo_afectacion_igv = models.CharField(
        max_length=2,
        choices=TIPO_AFECTACION_IGV_CHOICES,
        default='10',
        verbose_name='Tipo de Afectación IGV'
    )
    
    incluye_igv = models.BooleanField(
        default=True,
        verbose_name='Precio incluye IGV'
    )
    
    controla_stock = models.BooleanField(
        default=True,
        verbose_name='Controla Stock'
    )
    
    stock_actual = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Stock Actual'
    )
    
    stock_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Stock Mínimo'
    )
    
    stock_maximo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Stock Máximo'
    )
    # Información adicional
    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Marca'
    )
    
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Modelo'
    )
    
    peso = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name='Peso (kg)'
    )
    
    imagen = models.ImageField(
        upload_to='productos/imagenes/',
        blank=True,
        null=True,
        verbose_name='Imagen'
    )
    
    # Estado
    activo_venta = models.BooleanField(
        default=True,
        verbose_name='Activo para Venta'
    )
    
    activo_compra = models.BooleanField(
        default=True,
        verbose_name='Activo para Compra'
    )
    
    class Meta:
        db_table = 'core_producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['nombre']),
            models.Index(fields=['categoria']),
            models.Index(fields=['activo_venta']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def get_precio_con_igv(self):
        """Retorna el precio de venta con IGV incluido"""
        if self.incluye_igv:
            return self.precio_venta
        return self.precio_venta * Decimal('1.18')
    
    def get_precio_sin_igv(self):
        """Retorna el precio de venta sin IGV"""
        if not self.incluye_igv:
            return self.precio_venta
        return self.precio_venta / Decimal('1.18')

# =============================================================================
# MODELO CONFIGURACIÓN SISTEMA
# =============================================================================
class ConfiguracionSistema(models.Model):
    """
    Configuraciones globales del sistema
    """
    
    clave = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Clave'
    )
    
    valor = models.TextField(
        verbose_name='Valor'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_dato = models.CharField(
        max_length=20,
        choices=[
            ('string', 'Texto'),
            ('integer', 'Número Entero'),
            ('decimal', 'Número Decimal'),
            ('boolean', 'Verdadero/Falso'),
            ('json', 'JSON'),
        ],
        default='string',
        verbose_name='Tipo de Dato'
    )
    
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name='Actualizado en'
    )
    
    class Meta:
        db_table = 'core_configuracion_sistema'
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return f"{self.clave}: {self.valor}"
    
    @classmethod
    def obtener_valor(cls, clave, valor_defecto=None):
        """Obtiene un valor de configuración"""
        try:
            config = cls.objects.get(clave=clave)
            if config.tipo_dato == 'integer':
                return int(config.valor)
            elif config.tipo_dato == 'decimal':
                return Decimal(config.valor)
            elif config.tipo_dato == 'boolean':
                return config.valor.lower() in ['true', '1', 'yes', 'on']
            elif config.tipo_dato == 'json':
                import json
                return json.loads(config.valor)
            return config.valor
        except cls.DoesNotExist:
            return valor_defecto

# =============================================================================
# MODELOS ADICIONALES PARA COMPATIBILIDAD
# =============================================================================

class Sucursal(ModeloBase):
    """Sucursales de la empresa"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='sucursales')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    es_principal = models.BooleanField(default=False)
    distrito = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    ubigeo = models.CharField(max_length=6, blank=True)
    
    class Meta:
        db_table = 'core_sucursal'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
    
    def __str__(self):
        return f"{self.empresa.razon_social} - {self.nombre}"

# Alias para compatibilidad
Categoria = CategoriaProducto

class UnidadMedida(ModeloBase):
    """Unidades de medida"""
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'core_unidad_medida'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Moneda(ModeloBase):
    """Monedas del sistema"""
    codigo = models.CharField(max_length=3, unique=True)
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=5)
    
    class Meta:
        db_table = 'core_moneda'
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class TipoCambio(ModeloBase):
    """Tipos de cambio"""
    moneda_origen = models.ForeignKey(Moneda, on_delete=models.CASCADE, related_name='cambios_origen')
    moneda_destino = models.ForeignKey(Moneda, on_delete=models.CASCADE, related_name='cambios_destino')
    fecha = models.DateField()
    valor_compra = models.DecimalField(max_digits=10, decimal_places=4)
    valor_venta = models.DecimalField(max_digits=10, decimal_places=4)
    fuente = models.CharField(max_length=50, default='SUNAT')
    
    class Meta:
        db_table = 'core_tipo_cambio'
        verbose_name = 'Tipo de Cambio'
        verbose_name_plural = 'Tipos de Cambio'
        unique_together = ['moneda_origen', 'moneda_destino', 'fecha']
    
    def __str__(self):
        return f"{self.moneda_origen.codigo}/{self.moneda_destino.codigo} - {self.fecha}"