"""
FELICITA - Modelos Usuarios Completos
Sistema de Facturación Electrónica para Perú

Modelos completos para autenticación, sesiones y auditoría
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import Permission
import logging
import json

logger = logging.getLogger('felicita.usuarios')

# ===========================================
# MODELO USUARIO PERSONALIZADO
# ===========================================

class Usuario(AbstractUser):
    """Usuario personalizado con campos adicionales para FELICITA"""
    
    ROLES = [
        ('administrador', 'Administrador'),
        ('contador', 'Contador'),
        ('vendedor', 'Vendedor'),
        ('supervisor', 'Supervisor'),
        ('cliente', 'Cliente'),
    ]
    
    # Campos adicionales
    empresa = models.ForeignKey(
        'core.Empresa',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Empresa',
        help_text='Empresa a la que pertenece el usuario'
    )
    
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='vendedor',
        verbose_name='Rol',
        help_text='Rol del usuario en el sistema'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono',
        help_text='Número de teléfono de contacto',
        validators=[
            RegexValidator(
                regex=r'^[+]?[\d\s\-\(\)]+$',
                message='Ingrese un número de teléfono válido'
            )
        ]
    )
    
    documento_identidad = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Documento de Identidad',
        help_text='DNI, CE o RUC del usuario'
    )
    
    sucursales = models.ManyToManyField(
        'core.Sucursal',
        blank=True,
        related_name='usuarios_asignados',
        verbose_name='Sucursales',
        help_text='Sucursales a las que tiene acceso'
    )
    
    # Campos de seguridad
    bloqueado_hasta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Bloqueado hasta',
        help_text='Fecha hasta la cual el usuario está bloqueado'
    )
    
    intentos_fallidos = models.PositiveIntegerField(
        default=0,
        verbose_name='Intentos fallidos',
        help_text='Número de intentos de login fallidos'
    )
    
    ultimo_acceso_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Última IP de acceso'
    )
    
    # Campos de preferencias
    preferencias = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Preferencias',
        help_text='Preferencias personalizadas del usuario'
    )
    
    notificaciones_email = models.BooleanField(
        default=True,
        verbose_name='Notificaciones por email'
    )
    
    notificaciones_sistema = models.BooleanField(
        default=True,
        verbose_name='Notificaciones del sistema'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        indexes = [
            models.Index(fields=['empresa', 'rol']),
            models.Index(fields=['documento_identidad']),
            models.Index(fields=['email']),
        ]
    
    def clean(self):
        """Validaciones del modelo"""
        super().clean()
        
        # Validar que roles específicos tengan empresa
        if self.rol in ['administrador', 'contador', 'vendedor', 'supervisor'] and not self.empresa:
            raise ValidationError({
                'empresa': 'Este rol requiere estar asignado a una empresa'
            })
        
        # Validar documento de identidad único
        if self.documento_identidad:
            existing = Usuario.objects.filter(
                documento_identidad=self.documento_identidad
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    'documento_identidad': 'Este documento de identidad ya existe'
                })
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones"""
        self.clean()
        super().save(*args, **kwargs)
        logger.info(f"Usuario guardado: {self.username} - Rol: {self.rol}")
    
    @property
    def nombre_completo(self):
        """Obtener nombre completo"""
        return self.get_full_name() or self.username
    
    @property
    def esta_bloqueado(self):
        """Verificar si el usuario está bloqueado"""
        if self.bloqueado_hasta:
            return timezone.now() < self.bloqueado_hasta
        return False
    
    @property
    def puede_acceder(self):
        """Verificar si puede acceder al sistema"""
        return self.is_active and not self.esta_bloqueado
    
    def tiene_permiso(self, permiso: str) -> bool:
        """Verificar si el usuario tiene un permiso específico"""
        # Superusuario tiene todos los permisos
        if self.is_superuser:
            return True
        
        # Verificar permisos del rol
        permisos_rol = self.obtener_permisos_rol()
        
        # Verificar wildcard
        if '*' in permisos_rol:
            return True
        
        # Verificar permiso exacto
        if permiso in permisos_rol:
            return True
        
        # Verificar wildcards de módulo (ej: 'core.*')
        modulo = permiso.split('.')[0]
        if f"{modulo}.*" in permisos_rol:
            return True
        
        return False
    
    def obtener_permisos_rol(self) -> list:
        """Obtener permisos según el rol"""
        permisos_por_rol = {
            'administrador': [
                'core.*',
                'usuarios.*',
                'facturacion.*',
                'inventario.*',
                'reportes.*',
                'contabilidad.*',
                'punto_venta.*',
            ],
            'contador': [
                'core.view_empresa',
                'core.view_sucursal',
                'core.view_cliente',
                'core.change_configuracion',
                'core.view_configuracion',
                'facturacion.view_factura',
                'facturacion.add_factura',
                'facturacion.change_factura',
                'inventario.view_producto',
                'inventario.view_movimiento',
                'contabilidad.*',
                'reportes.*',
            ],
            'vendedor': [
                'core.view_cliente',
                'core.add_cliente',
                'core.change_cliente',
                'facturacion.view_factura',
                'facturacion.add_factura',
                'inventario.view_producto',
                'punto_venta.*',
            ],
            'supervisor': [
                'core.view_empresa',
                'core.view_sucursal',
                'core.view_cliente',
                'core.add_cliente',
                'core.change_cliente',
                'usuarios.view_usuario',
                'facturacion.*',
                'inventario.view_producto',
                'inventario.view_movimiento',
                'punto_venta.*',
                'reportes.view_reporte',
            ],
            'cliente': [
                'facturacion.view_own_factura',
                'reportes.view_own_reporte',
            ],
        }
        
        return permisos_por_rol.get(self.rol, [])
    
    def puede_acceder_sucursal(self, sucursal) -> bool:
        """Verificar si puede acceder a una sucursal específica"""
        # Administrador y contador pueden acceder a todas las sucursales de su empresa
        if self.rol in ['administrador', 'contador']:
            return sucursal.empresa == self.empresa
        
        # Otros roles solo a sucursales asignadas
        return sucursal in self.sucursales.all()
    
    def registrar_acceso(self, ip_address=None):
        """Registrar acceso exitoso"""
        self.last_login = timezone.now()
        if ip_address:
            self.ultimo_acceso_ip = ip_address
        self.intentos_fallidos = 0
        self.save(update_fields=['last_login', 'ultimo_acceso_ip', 'intentos_fallidos'])
        
        # Log de auditoría
        logger.info(f"Acceso exitoso: {self.username} desde IP {ip_address}")
    
    def registrar_intento_fallido(self, ip_address=None):
        """Registrar intento de acceso fallido"""
        self.intentos_fallidos += 1
        
        # Bloquear después de 5 intentos fallidos
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timezone.timedelta(minutes=30)
            logger.warning(f"Usuario bloqueado por intentos fallidos: {self.username}")
        
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])
        
        # Log de auditoría
        logger.warning(f"Intento fallido #{self.intentos_fallidos}: {self.username} desde IP {ip_address}")
    
    def desbloquear(self):
        """Desbloquear usuario manualmente"""
        self.bloqueado_hasta = None
        self.intentos_fallidos = 0
        self.save(update_fields=['bloqueado_hasta', 'intentos_fallidos'])
        logger.info(f"Usuario desbloqueado: {self.username}")

# ===========================================
# MODELO SESIÓN USUARIO
# ===========================================

class SesionUsuario(models.Model):
    """Registro de sesiones activas de usuarios"""
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='sesiones',
        verbose_name='Usuario'
    )
    
    token_jti = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Token JTI',
        help_text='Identificador único del refresh token'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP',
        help_text='IP desde donde se inició la sesión'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent',
        help_text='Información del navegador/dispositivo'
    )
    
    ubicacion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ubicación',
        help_text='Ubicación geográfica aproximada'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Sesión activa'
    )
    
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de inicio'
    )
    
    fecha_expiracion = models.DateTimeField(
        verbose_name='Fecha de expiración'
    )
    
    ultima_actividad = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actividad'
    )
    
    class Meta:
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['usuario', 'activa']),
            models.Index(fields=['token_jti']),
            models.Index(fields=['fecha_expiracion']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.ip_address} ({self.fecha_inicio})"
    
    @property
    def esta_expirada(self):
        """Verificar si la sesión está expirada"""
        return timezone.now() > self.fecha_expiracion
    
    @property
    def es_valida(self):
        """Verificar si la sesión es válida"""
        return self.activa and not self.esta_expirada
    
    def cerrar(self):
        """Cerrar la sesión"""
        self.activa = False
        self.save(update_fields=['activa'])

# ===========================================
# MODELO LOG AUDITORÍA
# ===========================================

class LogAuditoria(models.Model):
    """Log de auditoría para seguimiento de acciones"""
    
    ACCIONES = [
        ('LOGIN', 'Inicio de sesión'),
        ('LOGIN_FALLIDO', 'Intento de login fallido'),
        ('LOGOUT', 'Cierre de sesión'),
        ('REGISTRO', 'Registro de usuario'),
        ('CREAR_USUARIO', 'Crear usuario'),
        ('ACTUALIZAR_USUARIO', 'Actualizar usuario'),
        ('ELIMINAR_USUARIO', 'Eliminar usuario'),
        ('ACTIVAR_USUARIO', 'Activar usuario'),
        ('DESACTIVAR_USUARIO', 'Desactivar usuario'),
        ('DESBLOQUEAR_USUARIO', 'Desbloquear usuario'),
        ('CAMBIAR_PASSWORD', 'Cambiar contraseña'),
        ('CERRAR_SESION', 'Cerrar sesión específica'),
        ('CERRAR_TODAS_SESIONES', 'Cerrar todas las sesiones'),
        ('CREAR_FACTURA', 'Crear factura'),
        ('ANULAR_FACTURA', 'Anular factura'),
        ('CREAR_PRODUCTO', 'Crear producto'),
        ('ACTUALIZAR_PRODUCTO', 'Actualizar producto'),
        ('MOVIMIENTO_INVENTARIO', 'Movimiento de inventario'),
        ('GENERAR_REPORTE', 'Generar reporte'),
        ('MODIFICAR_CONFIGURACION', 'Modificar configuración'),
    ]
    
    RESULTADOS = [
        ('EXITOSO', 'Exitoso'),
        ('FALLIDO', 'Fallido'),
        ('ERROR', 'Error'),
    ]
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_auditoria',
        verbose_name='Usuario'
    )
    
    accion = models.CharField(
        max_length=50,
        choices=ACCIONES,
        verbose_name='Acción'
    )
    
    recurso = models.CharField(
        max_length=100,
        verbose_name='Recurso',
        help_text='Recurso o módulo afectado'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    datos_adicionales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos adicionales',
        help_text='Información adicional sobre la acción'
    )
    
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADOS,
        default='EXITOSO',
        verbose_name='Resultado'
    )
    
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora'
    )
    
    class Meta:
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['usuario', 'fecha_hora']),
            models.Index(fields=['accion', 'fecha_hora']),
            models.Index(fields=['recurso', 'fecha_hora']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else 'SISTEMA'
        return f"{usuario_str} - {self.accion} - {self.resultado} ({self.fecha_hora})"
    
    @classmethod
    def registrar(cls, usuario=None, accion=None, recurso=None, ip_address=None, 
                  user_agent=None, datos_adicionales=None, resultado='EXITOSO'):
        """Método para registrar logs de auditoría fácilmente"""
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            recurso=recurso,
            ip_address=ip_address,
            user_agent=user_agent,
            datos_adicionales=datos_adicionales or {},
            resultado=resultado
        )

# ===========================================
# SIGNALS
# ===========================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Usuario)
def usuario_post_save(sender, instance, created, **kwargs):
    """Signal post-save para Usuario"""
    if created:
        LogAuditoria.registrar(
            accion='CREAR_USUARIO',
            recurso='USUARIO',
            datos_adicionales={
                'usuario_creado': instance.username,
                'rol': instance.rol,
                'empresa': instance.empresa.razon_social if instance.empresa else None
            }
        )

@receiver(post_delete, sender=Usuario)
def usuario_post_delete(sender, instance, **kwargs):
    """Signal post-delete para Usuario"""
    LogAuditoria.registrar(
        accion='ELIMINAR_USUARIO',
        recurso='USUARIO',
        datos_adicionales={
            'usuario_eliminado': instance.username,
            'rol': instance.rol
        }
    )