"""
Modelos de usuarios para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone
import json


class TipoDocumento(models.TextChoices):
    """Tipos de documento de identidad según SUNAT"""
    DNI = '1', 'DNI'
    CARNET_EXTRANJERIA = '4', 'Carnet de Extranjería'
    RUC = '6', 'RUC'
    PASAPORTE = '7', 'Pasaporte'
    OTROS = '0', 'Otros'


class RolUsuario(models.TextChoices):
    """Roles de usuario en el sistema"""
    ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
    CONTADOR = 'CONTADOR', 'Contador'
    VENDEDOR = 'VENDEDOR', 'Vendedor'
    CLIENTE = 'CLIENTE', 'Cliente'


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para FELICITA
    Extiende el usuario base de Django con campos específicos del negocio
    """
    
    # Relación con empresa
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='usuarios',
        null=True,
        blank=True,
        verbose_name='Empresa'
    )
    
    # Información personal adicional
    numero_documento = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(8)],
        verbose_name='Número de Documento',
        help_text='DNI, RUC o documento de identidad'
    )
    
    tipo_documento = models.CharField(
        max_length=1,
        choices=TipoDocumento.choices,
        default=TipoDocumento.DNI,
        verbose_name='Tipo de Documento'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Formato de teléfono inválido'
        )],
        verbose_name='Teléfono'
    )
    
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    # Configuración de rol y permisos
    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.VENDEDOR,
        verbose_name='Rol'
    )
    
    permisos_especiales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Permisos Especiales',
        help_text='Configuración específica de permisos por módulo'
    )
    
    # Configuraciones de usuario
    configuraciones = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuraciones',
        help_text='Preferencias personales del usuario'
    )
    
    tema_preferido = models.CharField(
        max_length=20,
        choices=[
            ('claro', 'Claro'),
            ('oscuro', 'Oscuro'),
            ('automatico', 'Automático')
        ],
        default='claro',
        verbose_name='Tema Preferido'
    )
    
    idioma = models.CharField(
        max_length=5,
        choices=[
            ('es-pe', 'Español (Perú)'),
            ('es', 'Español'),
            ('en', 'English')
        ],
        default='es-pe',
        verbose_name='Idioma'
    )
    
    # Auditoria
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['empresa']),
            models.Index(fields=['numero_documento']),
            models.Index(fields=['is_active']),
            models.Index(fields=['rol']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def save(self, *args, **kwargs):
        """Guardar usuario con validaciones específicas"""
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
    
    def get_full_name(self):
        """Obtener nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_short_name(self):
        """Obtener nombre corto del usuario"""
        return self.first_name if self.first_name else self.username
    
    def tiene_permiso(self, modulo, accion='ver'):
        """Verificar si el usuario tiene permiso para una acción específica"""
        if self.is_superuser or self.rol == RolUsuario.ADMINISTRADOR:
            return True
        
        # Verificar permisos específicos
        if modulo in self.permisos_especiales:
            return self.permisos_especiales[modulo].get(accion, False)
        
        # Permisos por defecto según rol
        permisos_por_rol = {
            RolUsuario.CONTADOR: {
                'facturacion': ['ver', 'crear', 'editar'],
                'contabilidad': ['ver', 'crear', 'editar'],
                'reportes': ['ver', 'exportar'],
                'clientes': ['ver', 'crear', 'editar'],
                'productos': ['ver'],
                'inventarios': ['ver'],
            },
            RolUsuario.VENDEDOR: {
                'pos': ['ver', 'crear'],
                'facturacion': ['ver', 'crear'],
                'clientes': ['ver', 'crear', 'editar'],
                'productos': ['ver'],
                'inventarios': ['ver'],
                'reportes': ['ver'],
            },
            RolUsuario.CLIENTE: {
                'consultas': ['ver'],
                'reportes': ['ver_propios'],
            }
        }
        
        if self.rol in permisos_por_rol:
            modulo_permisos = permisos_por_rol[self.rol].get(modulo, [])
            return accion in modulo_permisos
        
        return False
    
    def actualizar_configuracion(self, clave, valor):
        """Actualizar una configuración específica del usuario"""
        if not self.configuraciones:
            self.configuraciones = {}
        
        self.configuraciones[clave] = valor
        self.save(update_fields=['configuraciones'])
    
    def obtener_configuracion(self, clave, valor_por_defecto=None):
        """Obtener una configuración específica del usuario"""
        if not self.configuraciones:
            return valor_por_defecto
        
        return self.configuraciones.get(clave, valor_por_defecto)
    
    def es_administrador(self):
        """Verificar si el usuario es administrador"""
        return self.rol == RolUsuario.ADMINISTRADOR or self.is_superuser
    
    def es_contador(self):
        """Verificar si el usuario es contador"""
        return self.rol == RolUsuario.CONTADOR
    
    def es_vendedor(self):
        """Verificar si el usuario es vendedor"""
        return self.rol == RolUsuario.VENDEDOR
    
    def puede_modificar_precios(self):
        """Verificar si el usuario puede modificar precios"""
        return (
            self.es_administrador() or 
            self.es_contador() or 
            self.tiene_permiso('productos', 'editar_precios')
        )
    
    def puede_aprobar_descuentos(self):
        """Verificar si el usuario puede aprobar descuentos"""
        return (
            self.es_administrador() or 
            self.tiene_permiso('ventas', 'aprobar_descuentos')
        )
    
    def obtener_almacenes_permitidos(self):
        """Obtener almacenes a los que tiene acceso el usuario"""
        if self.es_administrador():
            return self.empresa.almacenes.filter(estado=True)
        
        # Filtrar según configuración de permisos
        almacenes_permitidos = self.obtener_configuracion('almacenes_permitidos', [])
        if almacenes_permitidos:
            return self.empresa.almacenes.filter(
                id__in=almacenes_permitidos,
                estado=True
            )
        
        # Por defecto, acceso al almacén principal
        return self.empresa.almacenes.filter(es_principal=True, estado=True)


class SesionUsuario(models.Model):
    """
    Modelo para rastrear sesiones de usuario y actividad
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='sesiones',
        verbose_name='Usuario'
    )
    
    token_session = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Token de Sesión'
    )
    
    direccion_ip = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_ultimo_acceso = models.DateTimeField(
        default=timezone.now,
        verbose_name='Último Acceso'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Sesión Activa'
    )
    
    class Meta:
        db_table = 'sesiones_usuario'
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'
        ordering = ['-fecha_ultimo_acceso']
        indexes = [
            models.Index(fields=['usuario', 'activa']),
            models.Index(fields=['fecha_ultimo_acceso']),
        ]
    
    def __str__(self):
        return f"Sesión de {self.usuario.username} - {self.fecha_inicio}"
    
    def cerrar_sesion(self):
        """Cerrar la sesión"""
        self.activa = False
        self.save(update_fields=['activa'])
    
    def actualizar_ultimo_acceso(self):
        """Actualizar la fecha del último acceso"""
        self.fecha_ultimo_acceso = timezone.now()
        self.save(update_fields=['fecha_ultimo_acceso'])


class LogActividad(models.Model):
    """
    Modelo para auditoría de actividades del usuario
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_actividad',
        verbose_name='Usuario'
    )
    
    accion = models.CharField(
        max_length=100,
        verbose_name='Acción'
    )
    
    modulo = models.CharField(
        max_length=50,
        verbose_name='Módulo'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    
    datos_adicionales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos Adicionales'
    )
    
    direccion_ip = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha'
    )
    
    class Meta:
        db_table = 'logs_actividad'
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'fecha_creacion']),
            models.Index(fields=['modulo', 'accion']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else 'Usuario eliminado'
        return f"{usuario_str} - {self.accion} - {self.fecha_creacion}"
    
    @classmethod
    def registrar_actividad(cls, usuario, accion, modulo, descripcion, 
                          datos_adicionales=None, direccion_ip=None):
        """Método de clase para registrar actividad fácilmente"""
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            datos_adicionales=datos_adicionales or {},
            direccion_ip=direccion_ip or '127.0.0.1'
        )