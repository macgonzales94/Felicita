"""
FELICITA - Modelos Core
Sistema de Facturación Electrónica para Perú

Modelos base del sistema: Empresa, Cliente, Configuración, etc.
"""

from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

logger = logging.getLogger('felicita.core')

# ===========================================
# VALIDADORES PERSONALIZADOS PERÚ
# ===========================================

def validar_ruc_peruano(ruc):
    """Validador para RUC peruano con dígito verificador"""
    if not ruc or len(ruc) != 11 or not ruc.isdigit():
        raise ValidationError('RUC debe tener exactamente 11 dígitos numéricos')
    
    # Algoritmo verificador RUC SUNAT
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc[i]) * factores[i] for i in range(10))
    resto = suma % 11
    digito_verificador = 11 - resto if resto >= 2 else resto
    
    if int(ruc[10]) != digito_verificador:
        raise ValidationError('RUC no tiene un dígito verificador válido')

def validar_dni_peruano(dni):
    """Validador para DNI peruano"""
    if not dni or len(dni) != 8 or not dni.isdigit():
        raise ValidationError('DNI debe tener exactamente 8 dígitos numéricos')

def validar_ubigeo_peruano(ubigeo):
    """Validador para ubigeo peruano"""
    if ubigeo and (len(ubigeo) != 6 or not ubigeo.isdigit()):
        raise ValidationError('Ubigeo debe tener exactamente 6 dígitos')

# ===========================================
# MODELO BASE ABSTRACTO
# ===========================================

class ModeloBase(models.Model):
    """Modelo base con campos comunes para auditoría"""
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
        help_text='Fecha y hora de creación del registro'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización',
        help_text='Fecha y hora de última actualización'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el registro está activo'
    )
    
    class Meta:
        abstract = True
        
    def soft_delete(self):
        """Eliminación lógica"""
        self.activo = False
        self.save(update_fields=['activo', 'fecha_actualizacion'])
        
    def restore(self):
        """Restaurar registro eliminado lógicamente"""
        self.activo = True
        self.save(update_fields=['activo', 'fecha_actualizacion'])

# ===========================================
# MODELO EMPRESA
# ===========================================

class Empresa(ModeloBase):
    """Modelo para empresas emisoras de comprobantes"""
    
    ruc = models.CharField(
        max_length=11,
        unique=True,
        validators=[validar_ruc_peruano],
        verbose_name='RUC',
        help_text='Registro Único de Contribuyente (11 dígitos)'
    )
    razon_social = models.CharField(
        max_length=255,
        verbose_name='Razón Social',
        help_text='Razón social de la empresa'
    )
    nombre_comercial = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre Comercial',
        help_text='Nombre comercial de la empresa (opcional)'
    )
    direccion_fiscal = models.TextField(
        verbose_name='Dirección Fiscal',
        help_text='Dirección fiscal registrada en SUNAT'
    )
    ubigeo = models.CharField(
        max_length=6,
        validators=[validar_ubigeo_peruano],
        blank=True,
        verbose_name='Ubigeo',
        help_text='Código de ubigeo INEI (6 dígitos)'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono',
        help_text='Teléfono principal de contacto'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email',
        help_text='Correo electrónico principal'
    )
    representante_legal = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Representante Legal',
        help_text='Nombre del representante legal'
    )
    
    # Configuración específica SUNAT
    usuario_sol = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Usuario SOL',
        help_text='Usuario SOL para SUNAT'
    )
    clave_sol = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Clave SOL',
        help_text='Clave SOL para SUNAT (encriptada)'
    )
    
    # Certificado digital
    certificado_digital = models.FileField(
        upload_to='certificados/',
        blank=True,
        null=True,
        verbose_name='Certificado Digital',
        help_text='Archivo del certificado digital (.pfx)'
    )
    clave_certificado = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Clave Certificado',
        help_text='Clave del certificado digital (encriptada)'
    )
    
    # Metadatos
    metadatos = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadatos',
        help_text='Información adicional en formato JSON'
    )
    
    class Meta:
        db_table = 'core_empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['razon_social']
        
    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"
        
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar RUC
        validar_ruc_peruano(self.ruc)
        
        # Normalizar datos
        if self.razon_social:
            self.razon_social = self.razon_social.strip().upper()
        if self.nombre_comercial:
            self.nombre_comercial = self.nombre_comercial.strip()
            
    def save(self, *args, **kwargs):
        """Guardar con validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
        logger.info(f"Empresa guardada: {self.ruc} - {self.razon_social}")
        
    @property
    def nombre_completo(self):
        """Nombre comercial o razón social"""
        return self.nombre_comercial or self.razon_social
        
    def esta_configurada_para_facturacion(self):
        """Verificar si está configurada para facturación electrónica"""
        return bool(self.usuario_sol and self.clave_sol)

# ===========================================
# MODELO SUCURSAL
# ===========================================

class Sucursal(ModeloBase):
    """Modelo para sucursales de empresa"""
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='sucursales',
        verbose_name='Empresa'
    )
    codigo = models.CharField(
        max_length=10,
        verbose_name='Código',
        help_text='Código único de la sucursal'
    )
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre',
        help_text='Nombre de la sucursal'
    )
    direccion = models.TextField(
        verbose_name='Dirección',
        help_text='Dirección de la sucursal'
    )
    ubigeo = models.CharField(
        max_length=6,
        validators=[validar_ubigeo_peruano],
        blank=True,
        verbose_name='Ubigeo'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    es_principal = models.BooleanField(
        default=False,
        verbose_name='Es Principal',
        help_text='Indica si es la sucursal principal'
    )
    
    class Meta:
        db_table = 'core_sucursal'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        unique_together = ['empresa', 'codigo']
        ordering = ['empresa', 'nombre']
        
    def __str__(self):
        return f"{self.empresa.razon_social} - {self.nombre}"
        
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Solo puede haber una sucursal principal por empresa
        if self.es_principal:
            principales = Sucursal.objects.filter(
                empresa=self.empresa,
                es_principal=True,
                activo=True
            ).exclude(pk=self.pk)
            
            if principales.exists():
                raise ValidationError('Ya existe una sucursal principal para esta empresa')

# ===========================================
# MODELO CLIENTE
# ===========================================

class Cliente(ModeloBase):
    """Modelo para clientes"""
    
    TIPOS_DOCUMENTO = [
        ('dni', 'DNI'),
        ('ruc', 'RUC'),
        ('pasaporte', 'Pasaporte'),
        ('carnet_extranjeria', 'Carnet de Extranjería'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='clientes',
        verbose_name='Empresa'
    )
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPOS_DOCUMENTO,
        verbose_name='Tipo de Documento'
    )
    numero_documento = models.CharField(
        max_length=11,
        verbose_name='Número de Documento',
        help_text='DNI (8 dígitos), RUC (11 dígitos), etc.'
    )
    razon_social = models.CharField(
        max_length=255,
        verbose_name='Razón Social / Nombres',
        help_text='Razón social para empresas o nombres completos para personas'
    )
    nombre_comercial = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre Comercial',
        help_text='Nombre comercial (opcional)'
    )
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección',
        help_text='Dirección completa'
    )
    ubigeo = models.CharField(
        max_length=6,
        validators=[validar_ubigeo_peruano],
        blank=True,
        verbose_name='Ubigeo'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    # Información adicional
    contacto_principal = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Contacto Principal',
        help_text='Nombre del contacto principal'
    )
    limite_credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Límite de Crédito',
        help_text='Límite de crédito para ventas al crédito'
    )
    dias_credito = models.PositiveIntegerField(
        default=0,
        verbose_name='Días de Crédito',
        help_text='Días de crédito permitidos'
    )
    
    # Metadatos
    metadatos = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadatos'
    )
    
    class Meta:
        db_table = 'core_cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ['empresa', 'numero_documento']
        ordering = ['razon_social']
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['razon_social']),
            models.Index(fields=['empresa', 'activo']),
        ]
        
    def __str__(self):
        return f"{self.numero_documento} - {self.razon_social}"
        
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar documento según tipo
        if self.tipo_documento == 'dni':
            validar_dni_peruano(self.numero_documento)
        elif self.tipo_documento == 'ruc':
            validar_ruc_peruano(self.numero_documento)
        
        # Normalizar datos
        if self.razon_social:
            self.razon_social = self.razon_social.strip().upper()
            
    @property
    def nombre_completo(self):
        """Nombre comercial o razón social"""
        return self.nombre_comercial or self.razon_social
        
    @property
    def es_empresa(self):
        """Determinar si es empresa (RUC) o persona (DNI)"""
        return self.tipo_documento == 'ruc'
        
    def obtener_saldo_pendiente(self):
        """Obtener saldo pendiente del cliente"""
        # TODO: Implementar cuando tengamos el módulo de cuentas por cobrar
        return 0

# ===========================================
# MODELO CONFIGURACIÓN
# ===========================================

class Configuracion(ModeloBase):
    """Modelo para configuraciones del sistema"""
    
    empresa = models.OneToOneField(
        Empresa,
        on_delete=models.CASCADE,
        related_name='configuracion',
        verbose_name='Empresa'
    )
    
    # Configuración fiscal
    igv_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18.0,
        verbose_name='IGV %',
        help_text='Porcentaje de IGV (18.0 por defecto)'
    )
    moneda_defecto = models.CharField(
        max_length=3,
        default='PEN',
        choices=[
            ('PEN', 'Soles Peruanos'),
            ('USD', 'Dólares Americanos'),
            ('EUR', 'Euros'),
        ],
        verbose_name='Moneda por Defecto'
    )
    
    # Configuración de facturación
    numeracion_automatica = models.BooleanField(
        default=True,
        verbose_name='Numeración Automática',
        help_text='Generar numeración automáticamente'
    )
    envio_automatico_sunat = models.BooleanField(
        default=True,
        verbose_name='Envío Automático SUNAT',
        help_text='Enviar automáticamente comprobantes a SUNAT'
    )
    envio_email_cliente = models.BooleanField(
        default=False,
        verbose_name='Envío Email Cliente',
        help_text='Enviar comprobante por email al cliente'
    )
    
    # Configuración de inventario
    metodo_valuacion = models.CharField(
        max_length=10,
        default='PEPS',
        choices=[
            ('PEPS', 'PEPS (Primeras Entradas, Primeras Salidas)'),
            ('UEPS', 'UEPS (Últimas Entradas, Primeras Salidas)'),
            ('PROMEDIO', 'Promedio Ponderado'),
        ],
        verbose_name='Método de Valuación'
    )
    control_stock = models.BooleanField(
        default=True,
        verbose_name='Control de Stock',
        help_text='Activar control de stock en tiempo real'
    )
    
    # Configuración de reportes
    formato_fecha = models.CharField(
        max_length=20,
        default='DD/MM/YYYY',
        choices=[
            ('DD/MM/YYYY', 'DD/MM/YYYY'),
            ('MM/DD/YYYY', 'MM/DD/YYYY'),
            ('YYYY-MM-DD', 'YYYY-MM-DD'),
        ],
        verbose_name='Formato de Fecha'
    )
    
    # Configuraciones adicionales
    parametros = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Parámetros',
        help_text='Configuraciones adicionales en formato JSON'
    )
    
    class Meta:
        db_table = 'core_configuracion'
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
        
    def __str__(self):
        return f"Configuración - {self.empresa.razon_social}"
        
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar porcentaje IGV
        if self.igv_porcentaje < 0 or self.igv_porcentaje > 100:
            raise ValidationError('El porcentaje de IGV debe estar entre 0 y 100')

# ===========================================
# MODELO TIPO COMPROBANTE
# ===========================================

class TipoComprobante(ModeloBase):
    """Catálogo de tipos de comprobante SUNAT"""
    
    codigo = models.CharField(
        max_length=2,
        unique=True,
        verbose_name='Código SUNAT',
        help_text='Código SUNAT del tipo de comprobante'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre del tipo de comprobante'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada'
    )
    requiere_serie = models.BooleanField(
        default=True,
        verbose_name='Requiere Serie',
        help_text='Indica si requiere serie para numeración'
    )
    formato_serie = models.CharField(
        max_length=10,
        default='F###',
        verbose_name='Formato Serie',
        help_text='Formato de la serie (ej: F###, B###)'
    )
    
    class Meta:
        db_table = 'core_tipo_comprobante'
        verbose_name = 'Tipo de Comprobante'
        verbose_name_plural = 'Tipos de Comprobante'
        ordering = ['codigo']
        
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# ===========================================
# MODELO SERIE COMPROBANTE
# ===========================================

class SerieComprobante(ModeloBase):
    """Modelo para series de comprobantes por empresa"""
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='series',
        verbose_name='Empresa'
    )
    tipo_comprobante = models.ForeignKey(
        TipoComprobante,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Comprobante'
    )
    serie = models.CharField(
        max_length=4,
        verbose_name='Serie',
        help_text='Serie del comprobante (ej: F001, B001)'
    )
    numero_actual = models.PositiveIntegerField(
        default=0,
        verbose_name='Número Actual',
        help_text='Último número utilizado'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Sucursal',
        help_text='Sucursal que usa esta serie (opcional)'
    )
    
    class Meta:
        db_table = 'core_serie_comprobante'
        verbose_name = 'Serie de Comprobante'
        verbose_name_plural = 'Series de Comprobante'
        unique_together = ['empresa', 'tipo_comprobante', 'serie']
        ordering = ['empresa', 'tipo_comprobante', 'serie']
        
    def __str__(self):
        return f"{self.empresa.ruc} - {self.tipo_comprobante.codigo} - {self.serie}"
        
    def obtener_siguiente_numero(self):
        """Obtener el siguiente número correlativo"""
        self.numero_actual += 1
        self.save(update_fields=['numero_actual'])
        return self.numero_actual
        
    def reiniciar_numeracion(self):
        """Reiniciar numeración (usar con cuidado)"""
        self.numero_actual = 0
        self.save(update_fields=['numero_actual'])
        logger.warning(f"Numeración reiniciada para serie {self}")

# ===========================================
# SIGNALS
# ===========================================

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Empresa)
def crear_configuracion_empresa(sender, instance, created, **kwargs):
    """Crear configuración automáticamente al crear empresa"""
    if created:
        Configuracion.objects.create(empresa=instance)
        logger.info(f"Configuración creada para empresa {instance.ruc}")

@receiver(post_save, sender=Empresa)
def crear_series_iniciales(sender, instance, created, **kwargs):
    """Crear series iniciales al crear empresa"""
    if created:
        # Obtener tipos de comprobante principales
        tipos_principales = ['01', '03', '07', '08']  # Factura, Boleta, NC, ND
        
        for codigo_tipo in tipos_principales:
            try:
                tipo = TipoComprobante.objects.get(codigo=codigo_tipo)
                
                # Determinar serie inicial según tipo
                serie_inicial = {
                    '01': 'F001',  # Factura
                    '03': 'B001',  # Boleta
                    '07': 'FC01',  # Nota Crédito
                    '08': 'FD01',  # Nota Débito
                }.get(codigo_tipo, 'X001')
                
                SerieComprobante.objects.create(
                    empresa=instance,
                    tipo_comprobante=tipo,
                    serie=serie_inicial
                )
                
            except TipoComprobante.DoesNotExist:
                logger.warning(f"Tipo de comprobante {codigo_tipo} no encontrado")
        
        logger.info(f"Series iniciales creadas para empresa {instance.ruc}")