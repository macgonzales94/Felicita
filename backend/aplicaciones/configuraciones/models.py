"""
Modelos de configuraciones para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class TipoConfiguracion(models.TextChoices):
    """Tipos de configuración"""
    TEXT = 'TEXT', 'Texto'
    NUMBER = 'NUMBER', 'Número'
    BOOLEAN = 'BOOLEAN', 'Booleano'
    JSON = 'JSON', 'JSON'
    EMAIL = 'EMAIL', 'Email'
    URL = 'URL', 'URL'
    DATE = 'DATE', 'Fecha'
    TIME = 'TIME', 'Hora'
    DATETIME = 'DATETIME', 'Fecha y Hora'


class CategoriaConfiguracion(models.TextChoices):
    """Categorías de configuración"""
    GENERAL = 'GENERAL', 'General'
    FACTURACION = 'FACTURACION', 'Facturación'
    INVENTARIO = 'INVENTARIO', 'Inventario'
    CONTABILIDAD = 'CONTABILIDAD', 'Contabilidad'
    IMPUESTOS = 'IMPUESTOS', 'Impuestos'
    SISTEMA = 'SISTEMA', 'Sistema'
    SUNAT = 'SUNAT', 'SUNAT'
    NUBEFACT = 'NUBEFACT', 'Nubefact'
    EMAIL = 'EMAIL', 'Email'
    REPORTES = 'REPORTES', 'Reportes'
    SEGURIDAD = 'SEGURIDAD', 'Seguridad'


class Configuracion(models.Model):
    """
    Modelo para configuraciones del sistema
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='configuraciones_relacionadas',
        null=True,
        blank=True,
        verbose_name='Empresa',
        help_text='Si es null, es una configuración global'
    )
    
    clave = models.CharField(
        max_length=100,
        verbose_name='Clave',
        help_text='Identificador único de la configuración'
    )
    
    valor = models.TextField(
        blank=True,
        verbose_name='Valor',
        help_text='Valor de la configuración'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción de qué hace esta configuración'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoConfiguracion.choices,
        default=TipoConfiguracion.TEXT,
        verbose_name='Tipo de Configuración'
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaConfiguracion.choices,
        default=CategoriaConfiguracion.GENERAL,
        verbose_name='Categoría'
    )
    
    editable = models.BooleanField(
        default=True,
        verbose_name='Editable',
        help_text='Si el usuario puede modificar esta configuración'
    )
    
    requerido = models.BooleanField(
        default=False,
        verbose_name='Requerido',
        help_text='Si esta configuración es obligatoria'
    )
    
    valor_por_defecto = models.TextField(
        blank=True,
        verbose_name='Valor por Defecto'
    )
    
    opciones_validas = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Opciones Válidas',
        help_text='Lista de valores válidos para esta configuración'
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de visualización'
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
        db_table = 'configuraciones'
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
        unique_together = ['empresa', 'clave']
        ordering = ['categoria', 'orden', 'clave']
        indexes = [
            models.Index(fields=['empresa', 'categoria']),
            models.Index(fields=['clave']),
            models.Index(fields=['editable']),
        ]
    
    def __str__(self):
        empresa_str = f" ({self.empresa.razon_social})" if self.empresa else " (Global)"
        return f"{self.clave}{empresa_str}"
    
    def get_valor_convertido(self):
        """Obtener valor convertido al tipo correcto"""
        if not self.valor:
            return self.get_valor_por_defecto_convertido()
        
        try:
            if self.tipo == TipoConfiguracion.BOOLEAN:
                return self.valor.lower() in ['true', '1', 'yes', 'si', 'verdadero']
            elif self.tipo == TipoConfiguracion.NUMBER:
                if '.' in self.valor:
                    return float(self.valor)
                return int(self.valor)
            elif self.tipo == TipoConfiguracion.JSON:
                return json.loads(self.valor)
            else:
                return self.valor
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.get_valor_por_defecto_convertido()
    
    def get_valor_por_defecto_convertido(self):
        """Obtener valor por defecto convertido"""
        if not self.valor_por_defecto:
            return None
        
        try:
            if self.tipo == TipoConfiguracion.BOOLEAN:
                return self.valor_por_defecto.lower() in ['true', '1', 'yes', 'si', 'verdadero']
            elif self.tipo == TipoConfiguracion.NUMBER:
                if '.' in self.valor_por_defecto:
                    return float(self.valor_por_defecto)
                return int(self.valor_por_defecto)
            elif self.tipo == TipoConfiguracion.JSON:
                return json.loads(self.valor_por_defecto)
            else:
                return self.valor_por_defecto
        except (ValueError, TypeError, json.JSONDecodeError):
            return None
    
    def establecer_valor(self, nuevo_valor):
        """Establecer nuevo valor con conversión automática"""
        if self.tipo == TipoConfiguracion.JSON:
            if isinstance(nuevo_valor, (dict, list)):
                self.valor = json.dumps(nuevo_valor)
            else:
                self.valor = str(nuevo_valor)
        elif self.tipo == TipoConfiguracion.BOOLEAN:
            self.valor = 'true' if nuevo_valor else 'false'
        else:
            self.valor = str(nuevo_valor)
        
        self.save()
    
    def validar_valor(self, valor_a_validar=None):
        """Validar que el valor sea correcto"""
        valor = valor_a_validar if valor_a_validar is not None else self.valor
        
        # Validar si es requerido
        if self.requerido and not valor:
            raise ValueError(f"La configuración {self.clave} es requerida")
        
        # Validar opciones válidas
        if self.opciones_validas and valor not in self.opciones_validas:
            raise ValueError(f"Valor inválido para {self.clave}. Opciones: {self.opciones_validas}")
        
        # Validar tipo
        try:
            if self.tipo == TipoConfiguracion.NUMBER:
                float(valor)
            elif self.tipo == TipoConfiguracion.JSON:
                json.loads(valor)
            elif self.tipo == TipoConfiguracion.EMAIL:
                from django.core.validators import validate_email
                validate_email(valor)
            elif self.tipo == TipoConfiguracion.URL:
                from django.core.validators import URLValidator
                URLValidator()(valor)
        except Exception as e:
            raise ValueError(f"Valor inválido para {self.clave}: {str(e)}")
        
        return True
    
    def save(self, *args, **kwargs):
        """Guardar con validación"""
        if self.valor:
            self.validar_valor()
        super().save(*args, **kwargs)
    
    @classmethod
    def obtener_valor(cls, clave, empresa=None, valor_por_defecto=None):
        """Obtener valor de configuración"""
        try:
            # Buscar configuración específica de empresa
            if empresa:
                config = cls.objects.get(empresa=empresa, clave=clave)
            else:
                config = cls.objects.get(empresa__isnull=True, clave=clave)
            
            return config.get_valor_convertido()
        except cls.DoesNotExist:
            return valor_por_defecto
    
    @classmethod
    def establecer_valor(cls, clave, valor, empresa=None, crear_si_no_existe=True):
        """Establecer valor de configuración"""
        try:
            if empresa:
                config = cls.objects.get(empresa=empresa, clave=clave)
            else:
                config = cls.objects.get(empresa__isnull=True, clave=clave)
            
            config.establecer_valor(valor)
            return config
        except cls.DoesNotExist:
            if crear_si_no_existe:
                config = cls.objects.create(
                    empresa=empresa,
                    clave=clave,
                    valor=str(valor),
                )
                return config
            raise
    
    @classmethod
    def obtener_configuraciones_por_categoria(cls, categoria, empresa=None):
        """Obtener todas las configuraciones de una categoría"""
        filtros = {'categoria': categoria}
        if empresa:
            filtros['empresa'] = empresa
        else:
            filtros['empresa__isnull'] = True
        
        return cls.objects.filter(**filtros)
    
    @classmethod
    def crear_configuraciones_por_defecto(cls, empresa):
        """Crear configuraciones por defecto para una empresa"""
        configuraciones_defecto = [
            # GENERAL
            {
                'clave': 'empresa_nombre',
                'valor': empresa.razon_social,
                'descripcion': 'Nombre de la empresa',
                'categoria': CategoriaConfiguracion.GENERAL,
                'tipo': TipoConfiguracion.TEXT,
                'requerido': True,
            },
            {
                'clave': 'moneda_principal',
                'valor': 'PEN',
                'descripcion': 'Moneda principal del sistema',
                'categoria': CategoriaConfiguracion.GENERAL,
                'tipo': TipoConfiguracion.TEXT,
                'opciones_validas': ['PEN', 'USD', 'EUR'],
                'requerido': True,
            },
            {
                'clave': 'zona_horaria',
                'valor': 'America/Lima',
                'descripcion': 'Zona horaria de la empresa',
                'categoria': CategoriaConfiguracion.GENERAL,
                'tipo': TipoConfiguracion.TEXT,
                'requerido': True,
            },
            
            # FACTURACIÓN
            {
                'clave': 'numeracion_automatica',
                'valor': 'true',
                'descripcion': 'Numeración automática de comprobantes',
                'categoria': CategoriaConfiguracion.FACTURACION,
                'tipo': TipoConfiguracion.BOOLEAN,
                'requerido': True,
            },
            {
                'clave': 'facturacion_electronica',
                'valor': 'true',
                'descripcion': 'Facturación electrónica habilitada',
                'categoria': CategoriaConfiguracion.FACTURACION,
                'tipo': TipoConfiguracion.BOOLEAN,
                'requerido': True,
            },
            {
                'clave': 'envio_automatico_sunat',
                'valor': 'false',
                'descripcion': 'Envío automático a SUNAT al guardar',
                'categoria': CategoriaConfiguracion.FACTURACION,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            
            # IMPUESTOS
            {
                'clave': 'igv_rate',
                'valor': '0.18',
                'descripcion': 'Tasa de IGV en Perú',
                'categoria': CategoriaConfiguracion.IMPUESTOS,
                'tipo': TipoConfiguracion.NUMBER,
                'requerido': True,
            },
            {
                'clave': 'calculo_igv_automatico',
                'valor': 'true',
                'descripcion': 'Cálculo automático de IGV',
                'categoria': CategoriaConfiguracion.IMPUESTOS,
                'tipo': TipoConfiguracion.BOOLEAN,
                'requerido': True,
            },
            {
                'clave': 'igv_incluido_precios',
                'valor': 'false',
                'descripcion': 'Precios incluyen IGV por defecto',
                'categoria': CategoriaConfiguracion.IMPUESTOS,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            
            # INVENTARIO
            {
                'clave': 'metodo_costeo',
                'valor': 'PEPS',
                'descripcion': 'Método de costeo de inventarios',
                'categoria': CategoriaConfiguracion.INVENTARIO,
                'tipo': TipoConfiguracion.TEXT,
                'opciones_validas': ['PEPS', 'UEPS', 'PROMEDIO'],
                'requerido': True,
            },
            {
                'clave': 'stock_negativo_permitido',
                'valor': 'false',
                'descripcion': 'Permitir stock negativo',
                'categoria': CategoriaConfiguracion.INVENTARIO,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            {
                'clave': 'alertas_stock_minimo',
                'valor': 'true',
                'descripcion': 'Alertas cuando stock está bajo mínimo',
                'categoria': CategoriaConfiguracion.INVENTARIO,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            {
                'clave': 'redondeo_decimales',
                'valor': '2',
                'descripcion': 'Decimales para redondeo de montos',
                'categoria': CategoriaConfiguracion.INVENTARIO,
                'tipo': TipoConfiguracion.NUMBER,
                'requerido': True,
            },
            
            # CONTABILIDAD
            {
                'clave': 'asientos_automaticos',
                'valor': 'true',
                'descripcion': 'Generar asientos contables automáticamente',
                'categoria': CategoriaConfiguracion.CONTABILIDAD,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            {
                'clave': 'ejercicio_fiscal_inicio',
                'valor': '01/01',
                'descripcion': 'Fecha de inicio del ejercicio fiscal (DD/MM)',
                'categoria': CategoriaConfiguracion.CONTABILIDAD,
                'tipo': TipoConfiguracion.TEXT,
                'requerido': True,
            },
            
            # NUBEFACT
            {
                'clave': 'nubefact_mode',
                'valor': 'demo',
                'descripcion': 'Modo de Nubefact (demo/produccion)',
                'categoria': CategoriaConfiguracion.NUBEFACT,
                'tipo': TipoConfiguracion.TEXT,
                'opciones_validas': ['demo', 'produccion'],
                'requerido': True,
            },
            {
                'clave': 'nubefact_token',
                'valor': '',
                'descripcion': 'Token de API de Nubefact',
                'categoria': CategoriaConfiguracion.NUBEFACT,
                'tipo': TipoConfiguracion.TEXT,
                'editable': True,
            },
            
            # REPORTES
            {
                'clave': 'formato_fecha_reportes',
                'valor': 'dd/mm/yyyy',
                'descripcion': 'Formato de fecha en reportes',
                'categoria': CategoriaConfiguracion.REPORTES,
                'tipo': TipoConfiguracion.TEXT,
                'opciones_validas': ['dd/mm/yyyy', 'mm/dd/yyyy', 'yyyy-mm-dd'],
            },
            {
                'clave': 'exportar_excel_permitido',
                'valor': 'true',
                'descripcion': 'Permitir exportación a Excel',
                'categoria': CategoriaConfiguracion.REPORTES,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            {
                'clave': 'limite_registros_excel',
                'valor': '10000',
                'descripcion': 'Límite de registros para exportar a Excel',
                'categoria': CategoriaConfiguracion.REPORTES,
                'tipo': TipoConfiguracion.NUMBER,
            },
            
            # SISTEMA
            {
                'clave': 'backup_automatico',
                'valor': 'true',
                'descripcion': 'Backup automático de base de datos',
                'categoria': CategoriaConfiguracion.SISTEMA,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            {
                'clave': 'logs_detallados',
                'valor': 'true',
                'descripcion': 'Logs detallados de actividades',
                'categoria': CategoriaConfiguracion.SISTEMA,
                'tipo': TipoConfiguracion.BOOLEAN,
            },
            {
                'clave': 'session_timeout_minutos',
                'valor': '120',
                'descripcion': 'Timeout de sesión en minutos',
                'categoria': CategoriaConfiguracion.SISTEMA,
                'tipo': TipoConfiguracion.NUMBER,
            },
        ]
        
        configuraciones_creadas = []
        for config_data in configuraciones_defecto:
            config, created = cls.objects.get_or_create(
                empresa=empresa,
                clave=config_data['clave'],
                defaults=config_data
            )
            if created:
                configuraciones_creadas.append(config)
        
        return configuraciones_creadas


class ParametroSistema(models.Model):
    """
    Modelo para parámetros del sistema (configuraciones globales)
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
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoConfiguracion.choices,
        default=TipoConfiguracion.TEXT,
        verbose_name='Tipo'
    )
    
    editable_usuario = models.BooleanField(
        default=False,
        verbose_name='Editable por Usuario',
        help_text='Si los usuarios pueden modificar este parámetro'
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
        db_table = 'parametros_sistema'
        verbose_name = 'Parámetro del Sistema'
        verbose_name_plural = 'Parámetros del Sistema'
        ordering = ['clave']
    
    def __str__(self):
        return f"{self.clave}: {self.valor}"
    
    def get_valor_convertido(self):
        """Obtener valor convertido al tipo correcto"""
        try:
            if self.tipo == TipoConfiguracion.BOOLEAN:
                return self.valor.lower() in ['true', '1', 'yes', 'si']
            elif self.tipo == TipoConfiguracion.NUMBER:
                if '.' in self.valor:
                    return float(self.valor)
                return int(self.valor)
            elif self.tipo == TipoConfiguracion.JSON:
                return json.loads(self.valor)
            else:
                return self.valor
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.valor
    
    @classmethod
    def obtener(cls, clave, valor_por_defecto=None):
        """Obtener valor de parámetro del sistema"""
        try:
            parametro = cls.objects.get(clave=clave)
            return parametro.get_valor_convertido()
        except cls.DoesNotExist:
            return valor_por_defecto
    
    @classmethod
    def establecer(cls, clave, valor, descripcion="", tipo=TipoConfiguracion.TEXT):
        """Establecer valor de parámetro del sistema"""
        parametro, created = cls.objects.get_or_create(
            clave=clave,
            defaults={
                'valor': str(valor),
                'descripcion': descripcion,
                'tipo': tipo,
            }
        )
        
        if not created:
            parametro.valor = str(valor)
            parametro.save()
        
        return parametro
    
    @classmethod
    def crear_parametros_por_defecto(cls):
        """Crear parámetros por defecto del sistema"""
        parametros_defecto = [
            {
                'clave': 'version_sistema',
                'valor': '1.0.0',
                'descripcion': 'Versión actual del sistema FELICITA',
                'tipo': TipoConfiguracion.TEXT,
                'editable_usuario': False,
            },
            {
                'clave': 'mantenimiento_activo',
                'valor': 'false',
                'descripcion': 'Modo mantenimiento activado',
                'tipo': TipoConfiguracion.BOOLEAN,
                'editable_usuario': False,
            },
            {
                'clave': 'registros_nuevos_permitidos',
                'valor': 'true',
                'descripcion': 'Permitir registro de nuevas empresas',
                'tipo': TipoConfiguracion.BOOLEAN,
                'editable_usuario': False,
            },
            {
                'clave': 'limite_empresas',
                'valor': '100',
                'descripcion': 'Límite de empresas en el sistema',
                'tipo': TipoConfiguracion.NUMBER,
                'editable_usuario': False,
            },
            {
                'clave': 'backup_frecuencia_horas',
                'valor': '24',
                'descripcion': 'Frecuencia de backup automático en horas',
                'tipo': TipoConfiguracion.NUMBER,
                'editable_usuario': True,
            },
            {
                'clave': 'log_nivel',
                'valor': 'INFO',
                'descripcion': 'Nivel de logging del sistema',
                'tipo': TipoConfiguracion.TEXT,
                'editable_usuario': True,
            },
        ]
        
        for param_data in parametros_defecto:
            cls.objects.get_or_create(
                clave=param_data['clave'],
                defaults=param_data
            )