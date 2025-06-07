"""
MODELOS USUARIOS - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Gestión de usuarios, roles y permisos del sistema
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from aplicaciones.core.models import ModeloBase, Empresa
import uuid

# =============================================================================
# MANAGER PERSONALIZADO PARA USUARIOS
# =============================================================================
class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Crear y guardar un usuario con email y password"""
        if not email:
            raise ValueError('El usuario debe tener un email')
        
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crear y guardar un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

# =============================================================================
# MODELO USUARIO PERSONALIZADO
# =============================================================================
class Usuario(AbstractBaseUser, PermissionsMixin, ModeloBase):
    """
    Modelo de usuario personalizado para FELICITA
    """
    
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'DNI - Documento Nacional de Identidad'),
        ('CE', 'CE - Carnet de Extranjería'),
        ('PASSPORT', 'Pasaporte'),
    ]
    
    # Autenticación
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Dirección de correo electrónico para login'
    )
    
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nombre de Usuario',
        help_text='Nombre único de usuario'
    )
    
    # Datos personales
    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='DNI',
        verbose_name='Tipo de Documento'
    )
    
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Documento'
    )
    
    nombres = models.CharField(
        max_length=100,
        verbose_name='Nombres'
    )
    
    apellido_paterno = models.CharField(
        max_length=50,
        verbose_name='Apellido Paterno'
    )
    
    apellido_materno = models.CharField(
        max_length=50,
        verbose_name='Apellido Materno'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    
    # Configuración de trabajo
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name='Empresa'
    )
    
    cargo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Cargo'
    )
    
    area = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Área'
    )
    
    fecha_ingreso = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Ingreso'
    )
    
    # Configuración de sistema
    es_admin_empresa = models.BooleanField(
        default=False,
        verbose_name='Administrador de Empresa',
        help_text='Puede gestionar configuraciones de la empresa'
    )
    
    puede_aprobar_facturas = models.BooleanField(
        default=False,
        verbose_name='Puede Aprobar Facturas'
    )
    
    limite_descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Límite de Descuento (%)',
        help_text='Descuento máximo que puede aplicar'
    )
    
    # Estado del usuario
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Es Staff',
        help_text='Puede acceder al admin de Django'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_ultimo_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Último Login'
    )
    
    requiere_cambio_password = models.BooleanField(
        default=True,
        verbose_name='Requiere Cambio de Password'
    )
    
    fecha_expiracion_password = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Expiración de Password'
    )
    
    intentos_login_fallidos = models.PositiveIntegerField(
        default=0,
        verbose_name='Intentos de Login Fallidos'
    )
    
    bloqueado_hasta = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Bloqueado Hasta'
    )
    
    # Preferencias de usuario
    tema_interfaz = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Claro'),
            ('dark', 'Oscuro'),
            ('auto', 'Automático'),
        ],
        default='auto',
        verbose_name='Tema de Interfaz'
    )
    
    idioma = models.CharField(
        max_length=5,
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
        ],
        default='es',
        verbose_name='Idioma'
    )
    
    zona_horaria = models.CharField(
        max_length=50,
        default='America/Lima',
        verbose_name='Zona Horaria'
    )
    
    # Foto de perfil
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombres', 'apellido_paterno', 'numero_documento']
    
    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['numero_documento']),
            models.Index(fields=['empresa']),
        ]
    
    def __str__(self):
        return f"{self.get_nombre_completo()} ({self.email})"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()
    
    def get_nombre_corto(self):
        """Retorna el nombre corto del usuario"""
        return f"{self.nombres} {self.apellido_paterno}"
    
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado"""
        return (
            self.bloqueado_hasta and 
            self.bloqueado_hasta > timezone.now()
        )
    
    def password_expirado(self):
        """Verifica si el password ha expirado"""
        return (
            self.fecha_expiracion_password and 
            self.fecha_expiracion_password < timezone.now()
        )
    
    def bloquear_usuario(self, minutos=30):
        """Bloquea el usuario por X minutos"""
        from datetime import timedelta
        self.bloqueado_hasta = timezone.now() + timedelta(minutes=minutos)
        self.save(update_fields=['bloqueado_hasta'])
    
    def desbloquear_usuario(self):
        """Desbloquea el usuario"""
        self.bloqueado_hasta = None
        self.intentos_login_fallidos = 0
        self.save(update_fields=['bloqueado_hasta', 'intentos_login_fallidos'])

# =============================================================================
# MODELO ROL
# =============================================================================
class Rol(ModeloBase):
    """
    Roles del sistema para agrupar permisos
    """
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Rol'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    es_rol_sistema = models.BooleanField(
        default=False,
        verbose_name='Es Rol del Sistema',
        help_text='Los roles del sistema no pueden ser eliminados'
    )
    
    permisos_especiales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Permisos Especiales',
        help_text='Permisos específicos del sistema FELICITA'
    )
    
    class Meta:
        db_table = 'usuarios_rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre

# =============================================================================
# MODELO USUARIO-ROL (RELACIÓN MUCHOS A MUCHOS)
# =============================================================================
class UsuarioRol(ModeloBase):
    """
    Relación entre usuarios y roles con fecha de asignación
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='roles_asignados',
        verbose_name='Usuario'
    )
    
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name='usuarios_asignados',
        verbose_name='Rol'
    )
    
    fecha_asignacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Asignación'
    )
    
    fecha_vencimiento = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Vencimiento'
    )
    
    asignado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='roles_asignados_por_mi',
        verbose_name='Asignado Por'
    )
    
    class Meta:
        db_table = 'usuarios_usuario_rol'
        verbose_name = 'Usuario-Rol'
        verbose_name_plural = 'Usuarios-Roles'
        unique_together = ['usuario', 'rol']
    
    def __str__(self):
        return f"{self.usuario.get_nombre_completo()} - {self.rol.nombre}"
    
    def esta_vigente(self):
        """Verifica si la asignación del rol está vigente"""
        return (
            not self.fecha_vencimiento or 
            self.fecha_vencimiento > timezone.now()
        )

# =============================================================================
# MODELO PERMISO PERSONALIZADO
# =============================================================================
class PermisoPersonalizado(ModeloBase):
    """
    Permisos específicos del sistema FELICITA
    """
    
    MODULO_CHOICES = [
        ('facturacion', 'Facturación'),
        ('inventario', 'Inventario'),
        ('contabilidad', 'Contabilidad'),
        ('punto_venta', 'Punto de Venta'),
        ('reportes', 'Reportes'),
        ('configuracion', 'Configuración'),
        ('usuarios', 'Usuarios'),
        ('clientes', 'Clientes'),
        ('productos', 'Productos'),
    ]
    
    ACCION_CHOICES = [
        ('crear', 'Crear'),
        ('leer', 'Leer'),
        ('actualizar', 'Actualizar'),
        ('eliminar', 'Eliminar'),
        ('aprobar', 'Aprobar'),
        ('anular', 'Anular'),
        ('imprimir', 'Imprimir'),
        ('exportar', 'Exportar'),
        ('configurar', 'Configurar'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Permiso'
    )
    
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código del Permiso'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    modulo = models.CharField(
        max_length=20,
        choices=MODULO_CHOICES,
        verbose_name='Módulo'
    )
    
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name='Acción'
    )
    
    es_critico = models.BooleanField(
        default=False,
        verbose_name='Es Crítico',
        help_text='Permisos críticos requieren doble confirmación'
    )
    
    class Meta:
        db_table = 'usuarios_permiso_personalizado'
        verbose_name = 'Permiso Personalizado'
        verbose_name_plural = 'Permisos Personalizados'
        unique_together = ['modulo', 'accion']
    
    def __str__(self):
        return f"{self.modulo}.{self.accion} - {self.nombre}"

# =============================================================================
# MODELO SESIÓN USUARIO
# =============================================================================
class SesionUsuario(models.Model):
    """
    Registro de sesiones de usuarios para auditoría
    """
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='sesiones',
        verbose_name='Usuario'
    )
    
    token_sesion = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Token de Sesión'
    )
    
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_ultimo_acceso = models.DateTimeField(
        auto_now=True,
        verbose_name='Último Acceso'
    )
    
    fecha_cierre = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Cierre'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        verbose_name='User Agent'
    )
    
    dispositivo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Dispositivo'
    )
    
    navegador = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Navegador'
    )
    
    ubicacion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ubicación Aproximada'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Sesión Activa'
    )
    
    class Meta:
        db_table = 'usuarios_sesion_usuario'
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuarios'
        indexes = [
            models.Index(fields=['usuario', 'activa']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.usuario.email} - {self.fecha_inicio}"
    
    def cerrar_sesion(self):
        """Cierra la sesión"""
        self.fecha_cierre = timezone.now()
        self.activa = False
        self.save(update_fields=['fecha_cierre', 'activa'])
    
    def tiempo_activa(self):
        """Calcula el tiempo que la sesión ha estado activa"""
        if self.fecha_cierre:
            return self.fecha_cierre - self.fecha_inicio
        return timezone.now() - self.fecha_inicio

# =============================================================================
# MODELO LOG DE ACTIVIDAD USUARIO
# =============================================================================
class LogActividadUsuario(models.Model):
    """
    Registro de actividades de usuarios para auditoría
    """
    
    ACCION_CHOICES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('crear', 'Crear Registro'),
        ('actualizar', 'Actualizar Registro'),
        ('eliminar', 'Eliminar Registro'),
        ('ver', 'Ver Registro'),
        ('exportar', 'Exportar Datos'),
        ('imprimir', 'Imprimir'),
        ('configurar', 'Configurar Sistema'),
        ('aprobar', 'Aprobar Documento'),
        ('anular', 'Anular Documento'),
    ]
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='actividades',
        verbose_name='Usuario'
    )
    
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name='Acción'
    )
    
    modulo = models.CharField(
        max_length=50,
        verbose_name='Módulo'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    
    objeto_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID del Objeto'
    )
    
    objeto_tipo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo de Objeto'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    datos_adicionales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos Adicionales'
    )
    
    class Meta:
        db_table = 'usuarios_log_actividad_usuario'
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividades'
        indexes = [
            models.Index(fields=['usuario', 'fecha']),
            models.Index(fields=['accion']),
            models.Index(fields=['modulo']),
            models.Index(fields=['fecha']),
        ]
    
    def __str__(self):
        return f"{self.usuario.email} - {self.accion} - {self.fecha}"