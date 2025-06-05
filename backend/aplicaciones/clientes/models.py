"""
Modelos de clientes para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.db import models
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator
from django.utils import timezone
from decimal import Decimal


class TipoDocumento(models.TextChoices):
    """Tipos de documento de identidad según SUNAT"""
    DNI = '1', 'DNI'
    CARNET_EXTRANJERIA = '4', 'Carnet de Extranjería'
    RUC = '6', 'RUC'
    PASAPORTE = '7', 'Pasaporte'
    OTROS = '0', 'Otros'


class CondicionPago(models.TextChoices):
    """Condiciones de pago disponibles"""
    CONTADO = 'CONTADO', 'Contado'
    CREDITO_7 = 'CREDITO_7', 'Crédito 7 días'
    CREDITO_15 = 'CREDITO_15', 'Crédito 15 días'
    CREDITO_30 = 'CREDITO_30', 'Crédito 30 días'
    CREDITO_45 = 'CREDITO_45', 'Crédito 45 días'
    CREDITO_60 = 'CREDITO_60', 'Crédito 60 días'
    CREDITO_90 = 'CREDITO_90', 'Crédito 90 días'


class Cliente(models.Model):
    """
    Modelo para clientes y proveedores de la empresa
    """
    
    # Relación con empresa
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='clientes',
        verbose_name='Empresa'
    )
    
    # Identificación del cliente
    numero_documento = models.CharField(
        max_length=20,
        verbose_name='Número de Documento',
        help_text='DNI, RUC o documento de identidad'
    )
    
    tipo_documento = models.CharField(
        max_length=1,
        choices=TipoDocumento.choices,
        verbose_name='Tipo de Documento'
    )
    
    razon_social = models.CharField(
        max_length=255,
        verbose_name='Razón Social',
        help_text='Nombre completo o razón social'
    )
    
    nombre_comercial = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre Comercial',
        help_text='Nombre comercial o alias'
    )
    
    # Información de contacto
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    
    ubigeo = models.CharField(
        max_length=6,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\d{6}$',
            message='El ubigeo debe tener 6 dígitos'
        )],
        verbose_name='Ubigeo',
        help_text='Código de ubicación geográfica INEI'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?[\d\s\-\(\)]+$',
            message='Formato de teléfono inválido'
        )],
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        blank=True,
        validators=[EmailValidator()],
        verbose_name='Email'
    )
    
    pagina_web = models.URLField(
        blank=True,
        verbose_name='Página Web'
    )
    
    # Información comercial
    condicion_pago = models.CharField(
        max_length=20,
        choices=CondicionPago.choices,
        default=CondicionPago.CONTADO,
        verbose_name='Condición de Pago'
    )
    
    limite_credito = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Límite de Crédito',
        help_text='Límite máximo de crédito en soles'
    )
    
    vendedor_asignado = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_asignados',
        verbose_name='Vendedor Asignado'
    )
    
    # Configuración fiscal
    exonerado_igv = models.BooleanField(
        default=False,
        verbose_name='Exonerado de IGV',
        help_text='Cliente exonerado del pago de IGV'
    )
    
    retencion_agente = models.BooleanField(
        default=False,
        verbose_name='Agente de Retención',
        help_text='Cliente es agente de retención'
    )
    
    percepcion_agente = models.BooleanField(
        default=False,
        verbose_name='Agente de Percepción',
        help_text='Cliente es agente de percepción'
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones',
        help_text='Notas adicionales sobre el cliente'
    )
    
    datos_adicionales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos Adicionales',
        help_text='Información adicional en formato JSON'
    )
    
    # Estado y auditoria
    estado = models.BooleanField(
        default=True,
        verbose_name='Estado',
        help_text='Si el cliente está activo'
    )
    
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
        related_name='clientes_creados',
        verbose_name='Usuario que Creó'
    )
    
    usuario_actualizacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_actualizados',
        verbose_name='Usuario que Actualizó'
    )
    
    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['razon_social']
        unique_together = ['empresa', 'numero_documento']
        indexes = [
            models.Index(fields=['empresa', 'numero_documento']),
            models.Index(fields=['numero_documento']),
            models.Index(fields=['estado']),
            models.Index(fields=['vendedor_asignado']),
        ]
    
    def __str__(self):
        return f"{self.razon_social} ({self.numero_documento})"
    
    def save(self, *args, **kwargs):
        """Guardar cliente con validaciones"""
        # Validar documento según tipo
        if self.tipo_documento == TipoDocumento.DNI:
            if not self.validar_dni(self.numero_documento):
                raise ValueError('DNI inválido')
        elif self.tipo_documento == TipoDocumento.RUC:
            if not self.validar_ruc(self.numero_documento):
                raise ValueError('RUC inválido')
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def validar_dni(dni):
        """Validar formato de DNI peruano"""
        if not dni or len(dni) != 8:
            return False
        return dni.isdigit()
    
    @staticmethod
    def validar_ruc(ruc):
        """Validar RUC peruano con algoritmo verificador"""
        if not ruc or len(ruc) != 11:
            return False
        
        if not ruc.isdigit():
            return False
        
        # Algoritmo de validación RUC
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * factores[i] for i in range(10))
        resto = suma % 11
        digito_verificador = 11 - resto if resto >= 2 else resto
        
        return int(ruc[10]) == digito_verificador
    
    def get_nombre_para_mostrar(self):
        """Obtener el nombre más apropiado para mostrar"""
        return self.nombre_comercial if self.nombre_comercial else self.razon_social
    
    def get_tipo_documento_descripcion(self):
        """Obtener descripción del tipo de documento"""
        return self.get_tipo_documento_display()
    
    def es_persona_natural(self):
        """Verificar si es persona natural (DNI)"""
        return self.tipo_documento == TipoDocumento.DNI
    
    def es_empresa(self):
        """Verificar si es empresa (RUC)"""
        return self.tipo_documento == TipoDocumento.RUC
    
    def get_dias_credito(self):
        """Obtener días de crédito según condición de pago"""
        dias_credito = {
            CondicionPago.CONTADO: 0,
            CondicionPago.CREDITO_7: 7,
            CondicionPago.CREDITO_15: 15,
            CondicionPago.CREDITO_30: 30,
            CondicionPago.CREDITO_45: 45,
            CondicionPago.CREDITO_60: 60,
            CondicionPago.CREDITO_90: 90,
        }
        return dias_credito.get(self.condicion_pago, 0)
    
    def puede_comprar_a_credito(self):
        """Verificar si el cliente puede comprar a crédito"""
        return (
            self.condicion_pago != CondicionPago.CONTADO and
            self.limite_credito > 0 and
            self.estado
        )
    
    def get_credito_disponible(self):
        """Obtener crédito disponible del cliente"""
        if not self.puede_comprar_a_credito():
            return Decimal('0.00')
        
        # Calcular deuda pendiente
        deuda_pendiente = self.get_deuda_pendiente()
        credito_disponible = self.limite_credito - deuda_pendiente
        
        return max(credito_disponible, Decimal('0.00'))
    
    def get_deuda_pendiente(self):
        """Obtener total de deuda pendiente"""
        # Aquí se calcularía la deuda pendiente desde cuentas por cobrar
        # Por ahora retornamos 0
        return Decimal('0.00')
    
    def get_compras_ultimos_meses(self, meses=12):
        """Obtener total de compras en los últimos meses"""
        desde = timezone.now() - timezone.timedelta(days=30 * meses)
        
        # Aquí se calcularían las compras desde comprobantes
        # Por ahora retornamos 0
        return Decimal('0.00')
    
    def get_ultima_compra(self):
        """Obtener fecha de última compra"""
        # Aquí se buscaría el último comprobante
        # Por ahora retornamos None
        return None
    
    def get_datos_para_comprobante(self):
        """Obtener datos formateados para uso en comprobantes"""
        return {
            'numero_documento': self.numero_documento,
            'tipo_documento': self.tipo_documento,
            'razon_social': self.razon_social,
            'nombre_comercial': self.nombre_comercial,
            'direccion': self.direccion,
            'email': self.email,
            'telefono': self.telefono,
            'ubigeo': self.ubigeo,
            'exonerado_igv': self.exonerado_igv,
            'retencion_agente': self.retencion_agente,
            'percepcion_agente': self.percepcion_agente,
        }
    
    def activar(self):
        """Activar cliente"""
        self.estado = True
        self.save(update_fields=['estado'])
    
    def desactivar(self):
        """Desactivar cliente"""
        self.estado = False
        self.save(update_fields=['estado'])
    
    def asignar_vendedor(self, vendedor):
        """Asignar vendedor al cliente"""
        self.vendedor_asignado = vendedor
        self.save(update_fields=['vendedor_asignado'])
    
    def actualizar_limite_credito(self, nuevo_limite):
        """Actualizar límite de crédito"""
        self.limite_credito = nuevo_limite
        self.save(update_fields=['limite_credito'])
    
    def cambiar_condicion_pago(self, nueva_condicion):
        """Cambiar condición de pago"""
        self.condicion_pago = nueva_condicion
        self.save(update_fields=['condicion_pago'])
    
    @classmethod
    def buscar_por_documento(cls, empresa, numero_documento):
        """Buscar cliente por número de documento"""
        return cls.objects.filter(
            empresa=empresa,
            numero_documento=numero_documento,
            estado=True
        ).first()
    
    @classmethod
    def buscar_por_nombre(cls, empresa, nombre, limite=10):
        """Buscar clientes por nombre o razón social"""
        return cls.objects.filter(
            empresa=empresa,
            razon_social__icontains=nombre,
            estado=True
        )[:limite]
    
    @classmethod
    def obtener_morosos(cls, empresa):
        """Obtener clientes con deudas vencidas"""
        # Aquí se implementaría la lógica para obtener morosos
        # basado en cuentas por cobrar vencidas
        return cls.objects.none()
    
    @classmethod
    def obtener_mejores_clientes(cls, empresa, limite=10):
        """Obtener mejores clientes por volumen de compras"""
        # Aquí se implementaría la lógica para obtener mejores clientes
        # basado en histórico de compras
        return cls.objects.filter(empresa=empresa, estado=True)[:limite]


class ContactoCliente(models.Model):
    """
    Modelo para contactos adicionales de clientes
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='contactos',
        verbose_name='Cliente'
    )
    
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre del Contacto'
    )
    
    cargo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Cargo'
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
        verbose_name='Contacto Principal'
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        db_table = 'contactos_cliente'
        verbose_name = 'Contacto de Cliente'
        verbose_name_plural = 'Contactos de Cliente'
        ordering = ['-es_principal', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.cliente.razon_social}"
    
    def save(self, *args, **kwargs):
        """Asegurar que solo hay un contacto principal por cliente"""
        if self.es_principal:
            ContactoCliente.objects.filter(
                cliente=self.cliente,
                es_principal=True
            ).exclude(id=self.id).update(es_principal=False)
        
        super().save(*args, **kwargs)