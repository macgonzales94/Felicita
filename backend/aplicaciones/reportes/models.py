"""
MODELOS REPORTES - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Modelos para el módulo de reportes y analytics:
- ReportePersonalizado
- EjecucionReporte
- Dashboard
- KPI
- AlertaAutomatica
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from aplicaciones.core.models import ModeloBase, Empresa
from aplicaciones.usuarios.models import Usuario
import uuid

# =============================================================================
# MODELO REPORTE PERSONALIZADO
# =============================================================================
class ReportePersonalizado(ModeloBase):
    """
    Reportes personalizados del sistema
    """
    
    TIPO_REPORTE_CHOICES = [
        ('ventas', 'Reporte de Ventas'),
        ('compras', 'Reporte de Compras'),
        ('inventario', 'Reporte de Inventario'),
        ('financiero', 'Reporte Financiero'),
        ('contable', 'Reporte Contable'),
        ('fiscal', 'Reporte Fiscal'),
        ('clientes', 'Reporte de Clientes'),
        ('productos', 'Reporte de Productos'),
        ('usuarios', 'Reporte de Usuarios'),
        ('personalizado', 'Reporte Personalizado'),
    ]
    
    FORMATO_SALIDA_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    FRECUENCIA_CHOICES = [
        ('manual', 'Manual'),
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='reportes_personalizados',
        verbose_name='Empresa'
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código del Reporte'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Reporte'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_reporte = models.CharField(
        max_length=20,
        choices=TIPO_REPORTE_CHOICES,
        verbose_name='Tipo de Reporte'
    )
    
    # Configuración de consulta
    consulta_sql = models.TextField(
        blank=True,
        verbose_name='Consulta SQL',
        help_text='Consulta SQL personalizada para el reporte'
    )
    
    tablas_origen = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Tablas de Origen',
        help_text='Lista de tablas que utiliza el reporte'
    )
    
    parametros = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Parámetros',
        help_text='Parámetros configurables del reporte'
    )
    
    filtros_predeterminados = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Filtros Predeterminados'
    )
    
    # Configuración de salida
    formato_salida = models.CharField(
        max_length=10,
        choices=FORMATO_SALIDA_CHOICES,
        default='pdf',
        verbose_name='Formato de Salida'
    )
    
    incluir_graficos = models.BooleanField(
        default=False,
        verbose_name='Incluir Gráficos'
    )
    
    configuracion_graficos = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuración de Gráficos'
    )
    
    # Programación automática
    frecuencia_ejecucion = models.CharField(
        max_length=15,
        choices=FRECUENCIA_CHOICES,
        default='manual',
        verbose_name='Frecuencia de Ejecución'
    )
    
    hora_ejecucion = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Hora de Ejecución'
    )
    
    dia_ejecucion = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name='Día de Ejecución'
    )
    
    # Destinatarios automáticos
    enviar_por_email = models.BooleanField(
        default=False,
        verbose_name='Enviar por Email'
    )
    
    emails_destinatarios = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Emails Destinatarios'
    )
    
    # Usuario creador
    usuario_creador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='reportes_creados',
        verbose_name='Usuario Creador'
    )
    
    # Control de acceso
    es_publico = models.BooleanField(
        default=False,
        verbose_name='Es Público',
        help_text='Puede ser visto por todos los usuarios'
    )
    
    usuarios_autorizados = models.ManyToManyField(
        Usuario,
        blank=True,
        related_name='reportes_autorizados',
        verbose_name='Usuarios Autorizados'
    )
    
    # Estadísticas
    cantidad_ejecuciones = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad de Ejecuciones'
    )
    
    ultima_ejecucion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Ejecución'
    )
    
    class Meta:
        db_table = 'reportes_reporte_personalizado'
        verbose_name = 'Reporte Personalizado'
        verbose_name_plural = 'Reportes Personalizados'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo_reporte']),
            models.Index(fields=['frecuencia_ejecucion']),
            models.Index(fields=['usuario_creador']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def puede_ejecutar_usuario(self, usuario):
        """Verifica si un usuario puede ejecutar este reporte"""
        return (
            self.es_publico or
            self.usuario_creador == usuario or
            usuario in self.usuarios_autorizados.all() or
            usuario.is_superuser
        )

# =============================================================================
# MODELO EJECUCIÓN REPORTE
# =============================================================================
class EjecucionReporte(ModeloBase):
    """
    Registro de ejecuciones de reportes
    """
    
    ESTADO_CHOICES = [
        ('ejecutando', 'Ejecutando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
        ('cancelado', 'Cancelado'),
    ]
    
    reporte = models.ForeignKey(
        ReportePersonalizado,
        on_delete=models.CASCADE,
        related_name='ejecuciones',
        verbose_name='Reporte'
    )
    
    usuario_ejecutor = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='reportes_ejecutados',
        verbose_name='Usuario Ejecutor'
    )
    
    # Tiempo de ejecución
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Fin'
    )
    
    tiempo_ejecucion = models.DurationField(
        blank=True,
        null=True,
        verbose_name='Tiempo de Ejecución'
    )
    
    # Parámetros utilizados
    parametros_utilizados = models.JSONField(
        default=dict,
        verbose_name='Parámetros Utilizados'
    )
    
    filtros_aplicados = models.JSONField(
        default=dict,
        verbose_name='Filtros Aplicados'
    )
    
    # Resultados
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='ejecutando',
        verbose_name='Estado'
    )
    
    cantidad_registros = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad de Registros'
    )
    
    tamaño_archivo = models.PositiveIntegerField(
        default=0,
        verbose_name='Tamaño del Archivo (bytes)'
    )
    
    archivo_resultado = models.FileField(
        upload_to='reportes/resultados/',
        blank=True,
        null=True,
        verbose_name='Archivo Resultado'
    )
    
    # Error (si aplica)
    mensaje_error = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    # Configuración de envío
    enviado_por_email = models.BooleanField(
        default=False,
        verbose_name='Enviado por Email'
    )
    
    fecha_envio_email = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Envío por Email'
    )
    
    class Meta:
        db_table = 'reportes_ejecucion_reporte'
        verbose_name = 'Ejecución de Reporte'
        verbose_name_plural = 'Ejecuciones de Reportes'
        indexes = [
            models.Index(fields=['reporte']),
            models.Index(fields=['usuario_ejecutor']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['estado']),
        ]
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.reporte.nombre} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_tiempo_ejecucion(self):
        """Calcula el tiempo de ejecución"""
        if self.fecha_fin and self.fecha_inicio:
            self.tiempo_ejecucion = self.fecha_fin - self.fecha_inicio
            self.save(update_fields=['tiempo_ejecucion'])

# =============================================================================
# MODELO DASHBOARD
# =============================================================================
class Dashboard(ModeloBase):
    """
    Dashboards personalizados para visualización de datos
    """
    
    TIPO_DASHBOARD_CHOICES = [
        ('ejecutivo', 'Dashboard Ejecutivo'),
        ('ventas', 'Dashboard de Ventas'),
        ('inventario', 'Dashboard de Inventario'),
        ('financiero', 'Dashboard Financiero'),
        ('operativo', 'Dashboard Operativo'),
        ('personalizado', 'Dashboard Personalizado'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='dashboards',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código del Dashboard'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Dashboard'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_dashboard = models.CharField(
        max_length=20,
        choices=TIPO_DASHBOARD_CHOICES,
        verbose_name='Tipo de Dashboard'
    )
    
    # Configuración visual
    configuracion_layout = models.JSONField(
        default=dict,
        verbose_name='Configuración de Layout',
        help_text='Configuración de la disposición de widgets'
    )
    
    configuracion_widgets = models.JSONField(
        default=list,
        verbose_name='Configuración de Widgets',
        help_text='Lista de widgets y su configuración'
    )
    
    # Actualización automática
    auto_actualizar = models.BooleanField(
        default=True,
        verbose_name='Auto Actualizar'
    )
    
    intervalo_actualizacion = models.PositiveIntegerField(
        default=300,
        verbose_name='Intervalo de Actualización (segundos)'
    )
    
    # Usuario propietario
    usuario_propietario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='dashboards_propios',
        verbose_name='Usuario Propietario'
    )
    
    # Control de acceso
    es_publico = models.BooleanField(
        default=False,
        verbose_name='Es Público'
    )
    
    usuarios_autorizados = models.ManyToManyField(
        Usuario,
        blank=True,
        related_name='dashboards_autorizados',
        verbose_name='Usuarios Autorizados'
    )
    
    # Estadísticas
    cantidad_vistas = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad de Vistas'
    )
    
    ultima_vista = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Vista'
    )
    
    class Meta:
        db_table = 'reportes_dashboard'
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo_dashboard']),
            models.Index(fields=['usuario_propietario']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# =============================================================================
# MODELO KPI
# =============================================================================
class KPI(ModeloBase):
    """
    Indicadores clave de rendimiento (KPIs)
    """
    
    TIPO_KPI_CHOICES = [
        ('ventas', 'Ventas'),
        ('financiero', 'Financiero'),
        ('inventario', 'Inventario'),
        ('clientes', 'Clientes'),
        ('operativo', 'Operativo'),
        ('calidad', 'Calidad'),
    ]
    
    TIPO_CALCULO_CHOICES = [
        ('suma', 'Suma'),
        ('promedio', 'Promedio'),
        ('conteo', 'Conteo'),
        ('porcentaje', 'Porcentaje'),
        ('ratio', 'Ratio'),
        ('personalizado', 'Personalizado'),
    ]
    
    FRECUENCIA_CALCULO_CHOICES = [
        ('tiempo_real', 'Tiempo Real'),
        ('horario', 'Horario'),
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='kpis',
        verbose_name='Empresa'
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código del KPI'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del KPI'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_kpi = models.CharField(
        max_length=15,
        choices=TIPO_KPI_CHOICES,
        verbose_name='Tipo de KPI'
    )
    
    # Configuración de cálculo
    tipo_calculo = models.CharField(
        max_length=15,
        choices=TIPO_CALCULO_CHOICES,
        verbose_name='Tipo de Cálculo'
    )
    
    consulta_calculo = models.TextField(
        verbose_name='Consulta para Cálculo',
        help_text='SQL o configuración para calcular el KPI'
    )
    
    frecuencia_calculo = models.CharField(
        max_length=15,
        choices=FRECUENCIA_CALCULO_CHOICES,
        default='diario',
        verbose_name='Frecuencia de Cálculo'
    )
    
    # Valores y metas
    valor_actual = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Valor Actual'
    )
    
    valor_anterior = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name='Valor Anterior'
    )
    
    meta_minima = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name='Meta Mínima'
    )
    
    meta_optima = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name='Meta Óptima'
    )
    
    # Unidad de medida
    unidad_medida = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Unidad de Medida'
    )
    
    formato_numero = models.CharField(
        max_length=20,
        choices=[
            ('entero', 'Número Entero'),
            ('decimal', 'Número Decimal'),
            ('porcentaje', 'Porcentaje'),
            ('moneda', 'Moneda'),
        ],
        default='decimal',
        verbose_name='Formato de Número'
    )
    
    # Estado y tendencia
    tendencia = models.CharField(
        max_length=10,
        choices=[
            ('subida', 'Subida'),
            ('bajada', 'Bajada'),
            ('estable', 'Estable'),
        ],
        blank=True,
        verbose_name='Tendencia'
    )
    
    estado_semaforo = models.CharField(
        max_length=10,
        choices=[
            ('verde', 'Verde'),
            ('amarillo', 'Amarillo'),
            ('rojo', 'Rojo'),
        ],
        blank=True,
        verbose_name='Estado Semáforo'
    )
    
    # Fechas de cálculo
    fecha_ultimo_calculo = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha Último Cálculo'
    )
    
    fecha_proximo_calculo = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha Próximo Cálculo'
    )
    
    # Usuario responsable
    usuario_responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='kpis_responsable',
        verbose_name='Usuario Responsable'
    )
    
    class Meta:
        db_table = 'reportes_kpi'
        verbose_name = 'KPI'
        verbose_name_plural = 'KPIs'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo_kpi']),
            models.Index(fields=['frecuencia_calculo']),
            models.Index(fields=['fecha_proximo_calculo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def calcular_tendencia(self):
        """Calcula la tendencia comparando valor actual vs anterior"""
        if self.valor_anterior == 0:
            self.tendencia = 'estable'
        elif self.valor_actual > self.valor_anterior:
            self.tendencia = 'subida'
        elif self.valor_actual < self.valor_anterior:
            self.tendencia = 'bajada'
        else:
            self.tendencia = 'estable'
    
    def calcular_estado_semaforo(self):
        """Calcula el estado del semáforo basado en las metas"""
        if self.meta_optima and self.valor_actual >= self.meta_optima:
            self.estado_semaforo = 'verde'
        elif self.meta_minima and self.valor_actual >= self.meta_minima:
            self.estado_semaforo = 'amarillo'
        else:
            self.estado_semaforo = 'rojo'

# =============================================================================
# MODELO ALERTA AUTOMÁTICA
# =============================================================================
class AlertaAutomatica(ModeloBase):
    """
    Alertas automáticas basadas en condiciones
    """
    
    TIPO_ALERTA_CHOICES = [
        ('stock_bajo', 'Stock Bajo'),
        ('vencimiento', 'Próximo a Vencer'),
        ('meta_no_cumplida', 'Meta No Cumplida'),
        ('factura_vencida', 'Factura Vencida'),
        ('limite_credito', 'Límite de Crédito'),
        ('error_sistema', 'Error del Sistema'),
        ('personalizada', 'Personalizada'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='alertas_automaticas',
        verbose_name='Empresa'
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código de la Alerta'
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Alerta'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    tipo_alerta = models.CharField(
        max_length=20,
        choices=TIPO_ALERTA_CHOICES,
        verbose_name='Tipo de Alerta'
    )
    
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name='Prioridad'
    )
    
    # Condiciones
    condicion_sql = models.TextField(
        verbose_name='Condición SQL',
        help_text='Consulta SQL que determina cuándo se activa la alerta'
    )
    
    parametros_condicion = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Parámetros de la Condición'
    )
    
    # Configuración de ejecución
    es_activa = models.BooleanField(
        default=True,
        verbose_name='Es Activa'
    )
    
    frecuencia_verificacion = models.CharField(
        max_length=15,
        choices=[
            ('minutos', 'Cada 5 minutos'),
            ('horario', 'Cada hora'),
            ('diario', 'Diario'),
            ('semanal', 'Semanal'),
        ],
        default='horario',
        verbose_name='Frecuencia de Verificación'
    )
    
    # Acciones
    enviar_email = models.BooleanField(
        default=True,
        verbose_name='Enviar Email'
    )
    
    emails_notificacion = models.JSONField(
        default=list,
        verbose_name='Emails de Notificación'
    )
    
    mostrar_dashboard = models.BooleanField(
        default=True,
        verbose_name='Mostrar en Dashboard'
    )
    
    crear_tarea = models.BooleanField(
        default=False,
        verbose_name='Crear Tarea'
    )
    
    # Plantilla de mensaje
    plantilla_mensaje = models.TextField(
        verbose_name='Plantilla de Mensaje',
        help_text='Plantilla del mensaje de la alerta'
    )
    
    # Control de spam
    tiempo_silencio = models.PositiveIntegerField(
        default=60,
        verbose_name='Tiempo de Silencio (minutos)',
        help_text='Tiempo mínimo entre alertas del mismo tipo'
    )
    
    # Estadísticas
    cantidad_activaciones = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad de Activaciones'
    )
    
    ultima_activacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Activación'
    )
    
    proxima_verificacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Próxima Verificación'
    )
    
    # Usuario responsable
    usuario_creador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='alertas_creadas',
        verbose_name='Usuario Creador'
    )
    
    class Meta:
        db_table = 'reportes_alerta_automatica'
        verbose_name = 'Alerta Automática'
        verbose_name_plural = 'Alertas Automáticas'
        unique_together = ['empresa', 'codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo_alerta']),
            models.Index(fields=['es_activa']),
            models.Index(fields=['proxima_verificacion']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"