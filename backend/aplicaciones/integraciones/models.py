"""
MODELOS INTEGRACIONES - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Modelos para integraciones con APIs externas:
- ConfiguracionIntegracion
- LogIntegracion
- ConsultaRUC
- ConsultaDNI
- WebhookNubefact
"""

from django.db import models
from django.utils import timezone
from aplicaciones.core.models import ModeloBase, Empresa
from aplicaciones.usuarios.models import Usuario
import uuid

# =============================================================================
# MODELO CONFIGURACIÓN INTEGRACIÓN
# =============================================================================
class ConfiguracionIntegracion(ModeloBase):
    """
    Configuraciones para integraciones con servicios externos
    """
    
    TIPO_INTEGRACION_CHOICES = [
        ('nubefact', 'Nubefact (OSE)'),
        ('sunat_consultas', 'SUNAT Consultas'),
        ('reniec', 'RENIEC'),
        ('apis_peru', 'APIs Perú'),
        ('webhook', 'Webhook'),
        ('ftp', 'FTP'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('error', 'Con Error'),
        ('prueba', 'En Pruebas'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='integraciones',
        verbose_name='Empresa'
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código de Integración'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Integración'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_integracion = models.CharField(
        max_length=20,
        choices=TIPO_INTEGRACION_CHOICES,
        verbose_name='Tipo de Integración'
    )
    
    # Configuración de conexión
    url_endpoint = models.URLField(
        blank=True,
        verbose_name='URL del Endpoint'
    )
    
    url_sandbox = models.URLField(
        blank=True,
        verbose_name='URL de Sandbox'
    )
    
    usuario_api = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Usuario API'
    )
    
    password_api = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Password API'
    )
    
    token_api = models.TextField(
        blank=True,
        verbose_name='Token API'
    )
    
    api_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='API Key'
    )
    
    # Configuraciones adicionales
    configuracion_adicional = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuración Adicional',
        help_text='Configuraciones específicas de la integración'
    )
    
    headers_personalizados = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Headers Personalizados'
    )
    
    # Configuración de ambiente
    es_produccion = models.BooleanField(
        default=False,
        verbose_name='Es Producción'
    )
    
    # Configuración de reintentos
    max_reintentos = models.PositiveIntegerField(
        default=3,
        verbose_name='Máximo Reintentos'
    )
    
    timeout_conexion = models.PositiveIntegerField(
        default=30,
        verbose_name='Timeout Conexión (segundos)'
    )
    
    # Estado
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='inactiva',
        verbose_name='Estado'
    )
    
    fecha_ultima_conexion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha Última Conexión'
    )
    
    mensaje_ultimo_error = models.TextField(
        blank=True,
        verbose_name='Mensaje Último Error'
    )
    
    # Estadísticas
    total_consultas = models.PositiveIntegerField(
        default=0,
        verbose_name='Total Consultas'
    )
    
    consultas_exitosas = models.PositiveIntegerField(
        default=0,
        verbose_name='Consultas Exitosas'
    )
    
    consultas_fallidas = models.PositiveIntegerField(
        default=0,
        verbose_name='Consultas Fallidas'
    )
    
    class Meta:
        db_table = 'integraciones_configuracion'
        verbose_name = 'Configuración de Integración'
        verbose_name_plural = 'Configuraciones de Integraciones'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo_integracion']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def get_url_efectiva(self):
        """Retorna la URL efectiva según el ambiente"""
        if self.es_produccion:
            return self.url_endpoint
        return self.url_sandbox or self.url_endpoint
    
    def incrementar_estadisticas(self, exitosa=True):
        """Incrementa las estadísticas de uso"""
        self.total_consultas += 1
        if exitosa:
            self.consultas_exitosas += 1
        else:
            self.consultas_fallidas += 1
        self.fecha_ultima_conexion = timezone.now()
        self.save(update_fields=[
            'total_consultas', 'consultas_exitosas', 
            'consultas_fallidas', 'fecha_ultima_conexion'
        ])

# =============================================================================
# MODELO LOG INTEGRACIÓN
# =============================================================================
class LogIntegracion(models.Model):
    """
    Log de todas las interacciones con servicios externos
    """
    
    TIPO_OPERACION_CHOICES = [
        ('consulta', 'Consulta'),
        ('envio', 'Envío'),
        ('webhook', 'Webhook'),
        ('notificacion', 'Notificación'),
        ('sincronizacion', 'Sincronización'),
    ]
    
    ESTADO_CHOICES = [
        ('exitoso', 'Exitoso'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
        ('cancelado', 'Cancelado'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    configuracion = models.ForeignKey(
        ConfiguracionIntegracion,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Configuración'
    )
    
    # Identificación de la operación
    tipo_operacion = models.CharField(
        max_length=20,
        choices=TIPO_OPERACION_CHOICES,
        verbose_name='Tipo de Operación'
    )
    
    metodo_http = models.CharField(
        max_length=10,
        choices=[
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('DELETE', 'DELETE'),
            ('PATCH', 'PATCH'),
        ],
        verbose_name='Método HTTP'
    )
    
    url_llamada = models.URLField(
        verbose_name='URL Llamada'
    )
    
    # Datos de la petición
    headers_peticion = models.JSONField(
        default=dict,
        verbose_name='Headers de Petición'
    )
    
    payload_peticion = models.TextField(
        blank=True,
        verbose_name='Payload de Petición'
    )
    
    # Datos de la respuesta
    codigo_respuesta = models.PositiveIntegerField(
        verbose_name='Código de Respuesta HTTP'
    )
    
    headers_respuesta = models.JSONField(
        default=dict,
        verbose_name='Headers de Respuesta'
    )
    
    payload_respuesta = models.TextField(
        blank=True,
        verbose_name='Payload de Respuesta'
    )
    
    # Timing
    fecha_peticion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Petición'
    )
    
    tiempo_respuesta = models.PositiveIntegerField(
        verbose_name='Tiempo de Respuesta (ms)'
    )
    
    # Estado y resultado
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        verbose_name='Estado'
    )
    
    mensaje_error = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    # Usuario asociado
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='logs_integracion',
        verbose_name='Usuario'
    )
    
    # IP y información adicional
    ip_origen = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='IP de Origen'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    # Contexto adicional
    contexto_adicional = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Contexto Adicional'
    )
    
    class Meta:
        db_table = 'integraciones_log'
        verbose_name = 'Log de Integración'
        verbose_name_plural = 'Logs de Integraciones'
        indexes = [
            models.Index(fields=['configuracion', 'fecha_peticion']),
            models.Index(fields=['tipo_operacion']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_peticion']),
            models.Index(fields=['codigo_respuesta']),
        ]
        ordering = ['-fecha_peticion']
    
    def __str__(self):
        return f"{self.configuracion.codigo} - {self.tipo_operacion} - {self.fecha_peticion}"

# =============================================================================
# MODELO CONSULTA RUC
# =============================================================================
class ConsultaRUC(ModeloBase):
    """
    Consultas de RUC realizadas a SUNAT
    """
    
    ESTADO_CHOICES = [
        ('exitosa', 'Exitosa'),
        ('no_encontrado', 'No Encontrado'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
    ]
    
    ruc = models.CharField(
        max_length=11,
        verbose_name='RUC Consultado'
    )
    
    usuario_consulta = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='consultas_ruc',
        verbose_name='Usuario que Consulta'
    )
    
    fecha_consulta = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Consulta'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        verbose_name='Estado'
    )
    
    # Datos obtenidos de SUNAT
    razon_social = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Razón Social'
    )
    
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre Comercial'
    )
    
    estado_contribuyente = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Estado del Contribuyente'
    )
    
    condicion_contribuyente = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Condición del Contribuyente'
    )
    
    direccion_fiscal = models.TextField(
        blank=True,
        verbose_name='Dirección Fiscal'
    )
    
    ubigeo = models.CharField(
        max_length=6,
        blank=True,
        verbose_name='Ubigeo'
    )
    
    tipo_contribuyente = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo de Contribuyente'
    )
    
    fecha_inscripcion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Inscripción'
    )
    
    fecha_inicio_actividades = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Inicio de Actividades'
    )
    
    actividades_economicas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Actividades Económicas'
    )
    
    comprobantes_pago = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Comprobantes de Pago'
    )
    
    # Información adicional del servicio
    fuente_consulta = models.CharField(
        max_length=50,
        verbose_name='Fuente de Consulta'
    )
    
    respuesta_completa = models.JSONField(
        default=dict,
        verbose_name='Respuesta Completa del Servicio'
    )
    
    tiempo_respuesta = models.PositiveIntegerField(
        default=0,
        verbose_name='Tiempo de Respuesta (ms)'
    )
    
    mensaje_error = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    class Meta:
        db_table = 'integraciones_consulta_ruc'
        verbose_name = 'Consulta RUC'
        verbose_name_plural = 'Consultas RUC'
        indexes = [
            models.Index(fields=['ruc']),
            models.Index(fields=['fecha_consulta']),
            models.Index(fields=['estado']),
            models.Index(fields=['usuario_consulta']),
        ]
        ordering = ['-fecha_consulta']
    
    def __str__(self):
        return f"RUC {self.ruc} - {self.razon_social} ({self.fecha_consulta.strftime('%d/%m/%Y')})"

# =============================================================================
# MODELO CONSULTA DNI
# =============================================================================
class ConsultaDNI(ModeloBase):
    """
    Consultas de DNI realizadas a RENIEC
    """
    
    ESTADO_CHOICES = [
        ('exitosa', 'Exitosa'),
        ('no_encontrado', 'No Encontrado'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
    ]
    
    dni = models.CharField(
        max_length=8,
        verbose_name='DNI Consultado'
    )
    
    usuario_consulta = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='consultas_dni',
        verbose_name='Usuario que Consulta'
    )
    
    fecha_consulta = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Consulta'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        verbose_name='Estado'
    )
    
    # Datos obtenidos de RENIEC
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
    
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Nacimiento'
    )
    
    sexo = models.CharField(
        max_length=1,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
        ],
        blank=True,
        verbose_name='Sexo'
    )
    
    estado_civil = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Estado Civil'
    )
    
    # Información adicional del servicio
    fuente_consulta = models.CharField(
        max_length=50,
        verbose_name='Fuente de Consulta'
    )
    
    respuesta_completa = models.JSONField(
        default=dict,
        verbose_name='Respuesta Completa del Servicio'
    )
    
    tiempo_respuesta = models.PositiveIntegerField(
        default=0,
        verbose_name='Tiempo de Respuesta (ms)'
    )
    
    mensaje_error = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    class Meta:
        db_table = 'integraciones_consulta_dni'
        verbose_name = 'Consulta DNI'
        verbose_name_plural = 'Consultas DNI'
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['fecha_consulta']),
            models.Index(fields=['estado']),
            models.Index(fields=['usuario_consulta']),
        ]
        ordering = ['-fecha_consulta']
    
    def __str__(self):
        nombre_completo = f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()
        return f"DNI {self.dni} - {nombre_completo} ({self.fecha_consulta.strftime('%d/%m/%Y')})"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo"""
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()

# =============================================================================
# MODELO WEBHOOK NUBEFACT
# =============================================================================
class WebhookNubefact(models.Model):
    """
    Webhooks recibidos de Nubefact para actualización de estados
    """
    
    TIPO_EVENTO_CHOICES = [
        ('documento_aceptado', 'Documento Aceptado'),
        ('documento_rechazado', 'Documento Rechazado'),
        ('comunicacion_baja', 'Comunicación de Baja'),
        ('resumen_diario', 'Resumen Diario'),
        ('error_proceso', 'Error en Proceso'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Información del webhook
    fecha_recepcion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Recepción'
    )
    
    tipo_evento = models.CharField(
        max_length=30,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name='Tipo de Evento'
    )
    
    # Datos del documento
    numero_documento = models.CharField(
        max_length=50,
        verbose_name='Número de Documento'
    )
    
    tipo_documento = models.CharField(
        max_length=2,
        verbose_name='Tipo de Documento'
    )
    
    ruc_emisor = models.CharField(
        max_length=11,
        verbose_name='RUC Emisor'
    )
    
    # Estado SUNAT
    estado_sunat = models.CharField(
        max_length=20,
        verbose_name='Estado SUNAT'
    )
    
    codigo_respuesta_sunat = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Código Respuesta SUNAT'
    )
    
    mensaje_sunat = models.TextField(
        blank=True,
        verbose_name='Mensaje SUNAT'
    )
    
    # URLs de descarga
    url_xml = models.URLField(
        blank=True,
        verbose_name='URL del XML'
    )
    
    url_pdf = models.URLField(
        blank=True,
        verbose_name='URL del PDF'
    )
    
    url_cdr = models.URLField(
        blank=True,
        verbose_name='URL del CDR'
    )
    
    # Hash y firma
    hash_documento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Hash del Documento'
    )
    
    # Payload completo
    payload_completo = models.JSONField(
        default=dict,
        verbose_name='Payload Completo'
    )
    
    # Procesamiento
    procesado = models.BooleanField(
        default=False,
        verbose_name='Procesado'
    )
    
    fecha_procesamiento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Procesamiento'
    )
    
    error_procesamiento = models.TextField(
        blank=True,
        verbose_name='Error en Procesamiento'
    )
    
    # IP y headers
    ip_origen = models.GenericIPAddressField(
        verbose_name='IP de Origen'
    )
    
    headers_http = models.JSONField(
        default=dict,
        verbose_name='Headers HTTP'
    )
    
    class Meta:
        db_table = 'integraciones_webhook_nubefact'
        verbose_name = 'Webhook Nubefact'
        verbose_name_plural = 'Webhooks Nubefact'
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['fecha_recepcion']),
            models.Index(fields=['tipo_evento']),
            models.Index(fields=['procesado']),
            models.Index(fields=['ruc_emisor']),
        ]
        ordering = ['-fecha_recepcion']
    
    def __str__(self):
        return f"Webhook {self.tipo_evento} - {self.numero_documento} ({self.fecha_recepcion})"
    
    def marcar_como_procesado(self):
        """Marca el webhook como procesado"""
        self.procesado = True
        self.fecha_procesamiento = timezone.now()
        self.save(update_fields=['procesado', 'fecha_procesamiento'])

# =============================================================================
# MODELO CONFIGURACIÓN WEBHOOK
# =============================================================================
class ConfiguracionWebhook(ModeloBase):
    """
    Configuración de webhooks entrantes
    """
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='configuraciones_webhook',
        verbose_name='Empresa'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Webhook'
    )
    
    url_webhook = models.URLField(
        verbose_name='URL del Webhook'
    )
    
    token_validacion = models.CharField(
        max_length=200,
        verbose_name='Token de Validación'
    )
    
    secreto_firma = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Secreto para Firma'
    )
    
    es_activo = models.BooleanField(
        default=True,
        verbose_name='Es Activo'
    )
    
    eventos_suscritos = models.JSONField(
        default=list,
        verbose_name='Eventos Suscritos'
    )
    
    # Estadísticas
    total_webhooks_recibidos = models.PositiveIntegerField(
        default=0,
        verbose_name='Total Webhooks Recibidos'
    )
    
    ultimo_webhook_recibido = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Último Webhook Recibido'
    )
    
    class Meta:
        db_table = 'integraciones_configuracion_webhook'
        verbose_name = 'Configuración de Webhook'
        verbose_name_plural = 'Configuraciones de Webhooks'
        unique_together = ['empresa', 'url_webhook']
    
    def __str__(self):
        return f"{self.nombre} - {self.empresa.razon_social}"