"""
FELICITA - Modelos Usuarios
Sistema de Facturación Electrónica para Perú

Modelos para autenticación y autorización con JWT
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import Permission
import logging

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
                regex=r'^[+]?[0-9\s\-\(\)]{7,20}$',
                message='Formato de teléfono inválido'
            )
        ]
    )
    
    documento_identidad = models.CharField(
        max_length=11,
        blank=True,
        verbose_name='Documento de Identidad',
        help_text='DNI o Carnet de Extranjería'
    )
    
    # Configuraciones de usuario
    preferencias = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Preferencias',
        help_text='Configuraciones personalizadas del usuario'
    )
    
    # Control de acceso
    ultimo_acceso_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Última IP de Acceso'
    )
    
    intentos_fallidos = models.PositiveIntegerField(
        default=0,
        verbose_name='Intentos de Login Fallidos',
        help_text='Contador de intentos de login fallidos'
    )
    
    bloqueado_hasta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Bloqueado Hasta',
        help_text='Fecha hasta cuando está bloqueado el usuario'
    )
    
    # Configuración de notificaciones
    notificaciones_email = models.BooleanField(
        default=True,
        verbose_name='Notificaciones por Email',
        help_text='Recibir notificaciones por correo electrónico'
    )
    
    notificaciones_sistema = models.BooleanField(
        default=True,
        verbose_name='Notificaciones del Sistema',
        help_text='Recibir notificaciones en el sistema'
    )
    
    # Sucursales asignadas (para vendedores)
    sucursales = models.ManyToManyField(
        'core.Sucursal',
        blank=True,
        related_name='usuarios_asignados',
        verbose_name='Sucursales Asignadas',
        help_text='Sucursales donde puede trabajar este usuario'
    )
    
    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        permissions = [
            ('puede_ver_todas_empresas', 'Puede ver todas las empresas'),
            ('puede_cambiar_roles', 'Puede cambiar roles de usuarios'),
            ('puede_reiniciar_passwords', 'Puede reiniciar contraseñas'),
            ('puede_bloquear_usuarios', 'Puede bloquear/desbloquear usuarios'),
            ('puede_ver_auditoria', 'Puede ver logs de auditoría'),
        ]
    
    def __str__(self):
        nombre_completo = self.get_full_name()
        if nombre_completo:
            return f"{self.username} - {nombre_completo}"
        return self.username
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que cliente no tenga empresa asignada
        if self.rol == 'cliente' and self.empresa:
            raise ValidationError({
                'empresa': 'Los usuarios con rol Cliente no pueden tener empresa asignada'
            })
        
        # Validar que otros roles sí tengan empresa
        if self.rol != 'cliente' and not self.empresa and not self.is_superuser:
            raise ValidationError({
                'empresa': f'Los usuarios con rol {self.get_rol_display()} deben tener empresa asignada'
            })
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones"""
        self.full_clean()
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
        return '*' in permisos_rol or permiso in permisos_rol
    
    def obtener_permisos_rol(self) -> list:
        """Obtener permisos según el rol"""
        permisos_por_rol = {
            'administrador': [
                'core.view_empresa',
                'core.change_empresa',
                'core.add_sucursal',
                'core.change_sucursal',
                'core.view_sucursal',
                'core.add_cliente',
                'core.change_cliente',
                'core.view_cliente',
                'core.delete_cliente',
                'core.change_configuracion',
                'core.view_configuracion',
                'usuarios.view_usuario',
                'usuarios.change_usuario',
                'usuarios.add_usuario',
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
        logger.info(f"Usuario desbloqueado manualmente: {self.username}")
    
    def cambiar_rol(self, nuevo_rol, cambiado_por=None):
        """Cambiar rol del usuario con auditoría"""
        rol_anterior = self.rol
        self.rol = nuevo_rol
        self.save(update_fields=['rol'])
        
        # Log de auditoría
        logger.info(
            f"Rol cambiado: {self.username} de {rol_anterior} a {nuevo_rol} "
            f"por {cambiado_por.username if cambiado_por else 'sistema'}"
        )

# ===========================================
# MODELO SESIÓN USUARIO
# ===========================================

class SesionUsuario(models.Model):
    """Registro de sesiones de usuario para auditoría"""
    
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
        help_text='JWT Token Identifier'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent',
        help_text='Información del navegador/dispositivo'
    )
    
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_ultimo_uso = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Último Uso'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Sesión Activa'
    )
    
    # Información adicional
    dispositivo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Dispositivo'
    )
    
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ubicación'
    )
    
    class Meta:
        db_table = 'usuarios_sesion'
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'
        ordering = ['-fecha_ultimo_uso']
        indexes = [
            models.Index(fields=['usuario', 'activa']),
            models.Index(fields=['token_jti']),
            models.Index(fields=['fecha_ultimo_uso']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.ip_address} - {self.fecha_inicio}"
    
    def cerrar_sesion(self):
        """Cerrar sesión manualmente"""
        self.activa = False
        self.save(update_fields=['activa'])
        logger.info(f"Sesión cerrada: {self.usuario.username} - {self.ip_address}")
    
    @property
    def duracion(self):
        """Obtener duración de la sesión"""
        if self.activa:
            return timezone.now() - self.fecha_inicio
        return self.fecha_ultimo_uso - self.fecha_inicio
    
    @property
    def es_dispositivo_movil(self):
        """Detectar si es dispositivo móvil"""
        if self.user_agent:
            user_agent_lower = self.user_agent.lower()
            return any(mobile in user_agent_lower for mobile in 
                      ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
        return False

# ===========================================
# MODELO LOG AUDITORÍA
# ===========================================

class LogAuditoria(models.Model):
    """Log de auditoría para acciones del sistema"""
    
    ACCIONES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('login_fallido', 'Intento de Login Fallido'),
        ('cambio_password', 'Cambio de Contraseña'),
        ('cambio_rol', 'Cambio de Rol'),
        ('bloqueo', 'Bloqueo de Usuario'),
        ('desbloqueo', 'Desbloqueo de Usuario'),
        ('creacion', 'Creación de Registro'),
        ('modificacion', 'Modificación de Registro'),
        ('eliminacion', 'Eliminación de Registro'),
        ('facturacion', 'Acción de Facturación'),
        ('anulacion', 'Anulación de Comprobante'),
        ('configuracion', 'Cambio de Configuración'),
        ('exportacion', 'Exportación de Datos'),
        ('importacion', 'Importación de Datos'),
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
        max_length=20,
        choices=ACCIONES,
        verbose_name='Acción'
    )
    
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Modelo',
        help_text='Modelo Django afectado'
    )
    
    objeto_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='ID del Objeto',
        help_text='ID del objeto afectado'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada de la acción'
    )
    
    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Anteriores',
        help_text='Estado anterior del objeto (para modificaciones)'
    )
    
    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Nuevos',
        help_text='Estado nuevo del objeto'
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
    
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha',
        help_text='Fecha y hora de la acción'
    )
    
    empresa = models.ForeignKey(
        'core.Empresa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Empresa',
        help_text='Empresa en la que se realizó la acción'
    )
    
    class Meta:
        db_table = 'usuarios_log_auditoria'
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['usuario', 'fecha']),
            models.Index(fields=['accion', 'fecha']),
            models.Index(fields=['modelo', 'objeto_id']),
            models.Index(fields=['empresa', 'fecha']),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else 'Sistema'
        return f"{usuario_str} - {self.get_accion_display()} - {self.fecha}"
    
    @classmethod
    def crear_log(cls, usuario=None, accion=None, descripcion=None, 
                  modelo=None, objeto_id=None, datos_anteriores=None, 
                  datos_nuevos=None, ip_address=None, user_agent=None, empresa=None):
        """Método helper para crear logs de auditoría"""
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            descripcion=descripcion,
            modelo=modelo,
            objeto_id=str(objeto_id) if objeto_id else None,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent,
            empresa=empresa
        )

# ===========================================
# SIGNALS PARA AUDITORÍA
# ===========================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Usuario)
def log_usuario_cambio(sender, instance, created, **kwargs):
    """Log cuando se crea o modifica un usuario"""
    accion = 'creacion' if created else 'modificacion'
    descripcion = f"Usuario {'creado' if created else 'modificado'}: {instance.username}"
    
    LogAuditoria.crear_log(
        accion=accion,
        descripcion=descripcion,
        modelo='Usuario',
        objeto_id=instance.id,
        datos_nuevos={
            'username': instance.username,
            'email': instance.email,
            'rol': instance.rol,
            'activo': instance.is_active,
        },
        empresa=instance.empresa
    )