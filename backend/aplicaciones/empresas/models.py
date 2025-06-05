"""
Modelos de empresas para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from decimal import Decimal
import json


class Empresa(models.Model):
    """
    Modelo principal de empresas que usan el sistema FELICITA
    """
    
    # Información básica de identificación
    ruc = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{11}$',
            message='El RUC debe tener exactamente 11 dígitos'
        )],
        verbose_name='RUC',
        help_text='Registro Único de Contribuyentes'
    )
    
    razon_social = models.CharField(
        max_length=255,
        verbose_name='Razón Social',
        help_text='Denominación legal de la empresa'
    )
    
    nombre_comercial = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre Comercial',
        help_text='Nombre con el que se conoce comercialmente'
    )
    
    # Información de contacto
    direccion = models.TextField(
        verbose_name='Dirección',
        help_text='Dirección fiscal completa'
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
    
    representante_legal = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Representante Legal'
    )
    
    # Configuración SUNAT y facturación electrónica
    usuario_sol = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Usuario SOL',
        help_text='Usuario para portal SUNAT'
    )
    
    clave_sol = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Clave SOL',
        help_text='Contraseña para portal SUNAT'
    )
    
    certificado_digital = models.TextField(
        blank=True,
        verbose_name='Certificado Digital',
        help_text='Certificado digital para firma electrónica'
    )
    
    # Configuración contable
    plan_cuentas_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID Plan de Cuentas',
        help_text='Referencia al plan de cuentas PCGE'
    )
    
    ejercicio_fiscal_inicio = models.DateField(
        default='2024-01-01',
        verbose_name='Inicio Ejercicio Fiscal',
        help_text='Fecha de inicio del ejercicio fiscal'
    )
    
    # Estado y configuración
    estado = models.BooleanField(
        default=True,
        verbose_name='Estado',
        help_text='Si la empresa está activa en el sistema'
    )
    
    configuraciones = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuraciones',
        help_text='Configuraciones específicas de la empresa'
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
        related_name='empresas_creadas',
        verbose_name='Usuario que Creó'
    )
    
    usuario_actualizacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empresas_actualizadas',
        verbose_name='Usuario que Actualizó'
    )
    
    class Meta:
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['razon_social']
        indexes = [
            models.Index(fields=['ruc']),
            models.Index(fields=['estado']),
            models.Index(fields=['razon_social']),
        ]
    
    def __str__(self):
        return f"{self.razon_social} ({self.ruc})"
    
    def save(self, *args, **kwargs):
        """Guardar empresa con validaciones"""
        # Validar RUC
        if not self.validar_ruc(self.ruc):
            raise ValueError('RUC inválido')
        
        # Configuraciones por defecto
        if not self.configuraciones:
            self.configuraciones = self.obtener_configuraciones_por_defecto()
        
        super().save(*args, **kwargs)
    
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
    
    def obtener_configuraciones_por_defecto(self):
        """Obtener configuraciones por defecto para nueva empresa"""
        return {
            'igv_rate': 0.18,
            'moneda_principal': 'PEN',
            'metodo_costeo': 'PEPS',
            'numeracion_automatica': True,
            'facturacion_electronica': True,
            'nubefact_mode': 'demo',
            'permitir_stock_negativo': False,
            'calculo_igv_automatico': True,
            'redondeo_decimales': 2,
            'formato_fecha': 'dd/mm/yyyy',
            'backup_automatico': True,
            'envio_email_automatico': False,
            'limite_credito_por_defecto': 0.00,
            'dias_vencimiento_por_defecto': 30,
            'almacen_principal_id': None,
        }
    
    def obtener_configuracion(self, clave, valor_por_defecto=None):
        """Obtener una configuración específica de la empresa"""
        if not self.configuraciones:
            return valor_por_defecto
        
        return self.configuraciones.get(clave, valor_por_defecto)
    
    def actualizar_configuracion(self, clave, valor):
        """Actualizar una configuración específica de la empresa"""
        if not self.configuraciones:
            self.configuraciones = {}
        
        self.configuraciones[clave] = valor
        self.save(update_fields=['configuraciones'])
    
    def get_nombre_para_mostrar(self):
        """Obtener el nombre más apropiado para mostrar"""
        return self.nombre_comercial if self.nombre_comercial else self.razon_social
    
    def get_direccion_completa(self):
        """Obtener dirección completa formateada"""
        direccion = self.direccion
        if self.ubigeo:
            # Aquí se podría hacer lookup del ubigeo para obtener distrito/provincia/departamento
            direccion += f" (Ubigeo: {self.ubigeo})"
        return direccion
    
    def get_datos_para_comprobante(self):
        """Obtener datos formateados para uso en comprobantes"""
        return {
            'ruc': self.ruc,
            'razon_social': self.razon_social,
            'nombre_comercial': self.nombre_comercial,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'ubigeo': self.ubigeo,
        }
    
    def tiene_facturacion_electronica_activa(self):
        """Verificar si la facturación electrónica está activa"""
        return (
            self.obtener_configuracion('facturacion_electronica', True) and
            self.usuario_sol and 
            self.clave_sol
        )
    
    def get_tasa_igv(self):
        """Obtener tasa de IGV configurada"""
        return Decimal(str(self.obtener_configuracion('igv_rate', 0.18)))
    
    def get_moneda_principal(self):
        """Obtener moneda principal configurada"""
        return self.obtener_configuracion('moneda_principal', 'PEN')
    
    def get_metodo_costeo(self):
        """Obtener método de costeo configurado"""
        return self.obtener_configuracion('metodo_costeo', 'PEPS')
    
    def puede_tener_stock_negativo(self):
        """Verificar si se permite stock negativo"""
        return self.obtener_configuracion('permitir_stock_negativo', False)
    
    def get_decimales_redondeo(self):
        """Obtener cantidad de decimales para redondeo"""
        return self.obtener_configuracion('redondeo_decimales', 2)
    
    def get_series_activas(self):
        """Obtener series de comprobantes activas"""
        return self.series_comprobantes.filter(activo=True)
    
    def get_almacenes_activos(self):
        """Obtener almacenes activos de la empresa"""
        return self.almacenes.filter(estado=True)
    
    def get_almacen_principal(self):
        """Obtener almacén principal de la empresa"""
        almacen_principal_id = self.obtener_configuracion('almacen_principal_id')
        
        if almacen_principal_id:
            try:
                return self.almacenes.get(id=almacen_principal_id, estado=True)
            except:
                pass
        
        # Buscar almacén marcado como principal
        almacen_principal = self.almacenes.filter(
            es_principal=True, 
            estado=True
        ).first()
        
        if almacen_principal:
            return almacen_principal
        
        # Retornar el primer almacén activo
        return self.almacenes.filter(estado=True).first()
    
    def get_usuarios_activos(self):
        """Obtener usuarios activos de la empresa"""
        return self.usuarios.filter(is_active=True)
    
    def get_estadisticas_basicas(self):
        """Obtener estadísticas básicas de la empresa"""
        return {
            'total_usuarios': self.usuarios.filter(is_active=True).count(),
            'total_clientes': getattr(self, 'clientes', None).filter(estado=True).count() if hasattr(self, 'clientes') else 0,
            'total_productos': getattr(self, 'productos', None).filter(estado=True).count() if hasattr(self, 'productos') else 0,
            'total_almacenes': self.almacenes.filter(estado=True).count() if hasattr(self, 'almacenes') else 0,
            'facturacion_electronica': self.tiene_facturacion_electronica_activa(),
            'ultimo_ejercicio_fiscal': self.ejercicio_fiscal_inicio.year,
        }
    
    def validar_configuraciones(self):
        """Validar que las configuraciones de la empresa son correctas"""
        errores = []
        
        if not self.tiene_facturacion_electronica_activa():
            errores.append('Facturación electrónica no configurada correctamente')
        
        if not self.get_almacen_principal():
            errores.append('No hay almacén principal configurado')
        
        if not self.get_series_activas().exists():
            errores.append('No hay series de comprobantes configuradas')
        
        return errores
    
    def activar(self):
        """Activar empresa"""
        self.estado = True
        self.save(update_fields=['estado'])
    
    def desactivar(self):
        """Desactivar empresa"""
        self.estado = False
        self.save(update_fields=['estado'])
    
    def clonar_configuraciones_desde(self, otra_empresa):
        """Clonar configuraciones desde otra empresa"""
        if isinstance(otra_empresa, Empresa):
            self.configuraciones = otra_empresa.configuraciones.copy()
            self.save(update_fields=['configuraciones'])