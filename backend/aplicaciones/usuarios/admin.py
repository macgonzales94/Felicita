"""
ADMIN USUARIOS - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Configuración del panel de administración para usuarios y roles
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django import forms

from .models import (
    Usuario, Rol, PermisoPersonalizado, UsuarioRol,
    SesionUsuario, LogActividadUsuario
)


# =============================================================================
# FORMULARIOS PERSONALIZADOS
# =============================================================================
class CrearUsuarioForm(forms.ModelForm):
    """Formulario para crear usuario en admin"""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        help_text='Mínimo 8 caracteres'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
        help_text='Ingrese la misma contraseña para verificación'
    )

    class Meta:
        model = Usuario
        fields = [
            'email', 'username', 'nombres', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'telefono', 'empresa',
            'cargo', 'area', 'es_admin_empresa', 'puede_aprobar_facturas',
            'limite_descuento'
        ]

    def clean_password2(self):
        """Verificar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        """Guardar usuario con contraseña encriptada"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CambiarUsuarioForm(forms.ModelForm):
    """Formulario para cambiar usuario en admin"""
    password = ReadOnlyPasswordHashField(
        label="Contraseña",
        help_text="Las contraseñas en texto plano no se almacenan, por lo que no hay "
                 "forma de ver la contraseña de este usuario, pero puedes cambiarla "
                 "usando <a href=\"../password/\">este formulario</a>."
    )

    class Meta:
        model = Usuario
        fields = [
            'email', 'username', 'nombres', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'telefono', 'empresa',
            'cargo', 'area', 'fecha_ingreso', 'es_admin_empresa',
            'puede_aprobar_facturas', 'limite_descuento', 'is_active',
            'is_staff', 'is_superuser', 'requiere_cambio_password',
            'tema_interfaz', 'idioma', 'zona_horaria'
        ]


# =============================================================================
# INLINES PARA RELACIONES
# =============================================================================
class UsuarioRolInline(admin.TabularInline):
    """Inline para roles del usuario"""
    model = UsuarioRol
    fk_name = 'usuario'  # Especificar cuál FK usar
    extra = 1
    fields = ['rol', 'fecha_asignacion', 'fecha_vencimiento', 'activo']
    readonly_fields = ['fecha_asignacion']


class SesionUsuarioInline(admin.TabularInline):
    """Inline para sesiones del usuario"""
    model = SesionUsuario
    extra = 0
    fields = [
        'fecha_inicio', 'ip_address', 'dispositivo', 
        'navegador', 'activa'
    ]
    readonly_fields = ['fecha_inicio', 'ip_address', 'dispositivo', 'navegador']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# =============================================================================
# ADMIN PRINCIPAL DE USUARIO
# =============================================================================
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Administración personalizada para usuarios de FELICITA
    """
    form = CambiarUsuarioForm
    add_form = CrearUsuarioForm
    
    # Campos mostrados en la lista
    list_display = [
        'email', 'get_nombre_completo', 'empresa', 'cargo',
        'is_active', 'es_admin_empresa', 'fecha_ultimo_login',
        'get_estado_bloqueo'
    ]
    
    # Filtros laterales
    list_filter = [
        'is_active', 'is_staff', 'es_admin_empresa', 'puede_aprobar_facturas',
        'empresa', 'tipo_documento', 'requiere_cambio_password',
        'tema_interfaz', 'fecha_ingreso'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'email', 'username', 'nombres', 'apellido_paterno',
        'numero_documento', 'telefono'
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'fecha_ultimo_login', 'intentos_login_fallidos',
        'bloqueado_hasta', 'creado_en', 'actualizado_en'
    ]
    
    # Ordenamiento por defecto
    ordering = ['nombres', 'apellido_paterno']
    
    # Inlines
    inlines = [UsuarioRolInline, SesionUsuarioInline]
    
    # Configuración de formularios
    fieldsets = (
        ('Autenticación', {
            'fields': ('email', 'username', 'password')
        }),
        ('Información Personal', {
            'fields': (
                'nombres', 'apellido_paterno', 'apellido_materno',
                'tipo_documento', 'numero_documento', 'telefono',
                'foto_perfil'
            )
        }),
        ('Información Laboral', {
            'fields': (
                'empresa', 'cargo', 'area', 'fecha_ingreso'
            )
        }),
        ('Permisos del Sistema', {
            'fields': (
                'es_admin_empresa', 'puede_aprobar_facturas',
                'limite_descuento', 'is_active', 'is_staff', 'is_superuser'
            )
        }),
        ('Seguridad', {
            'fields': (
                'requiere_cambio_password', 'fecha_expiracion_password',
                'intentos_login_fallidos', 'bloqueado_hasta'
            ),
            'classes': ['collapse']
        }),
        ('Preferencias', {
            'fields': (
                'tema_interfaz', 'idioma', 'zona_horaria'
            ),
            'classes': ['collapse']
        }),
        ('Metadatos', {
            'fields': (
                'fecha_ultimo_login', 'creado_en', 'actualizado_en'
            ),
            'classes': ['collapse']
        })
    )
    
    add_fieldsets = (
        ('Crear Usuario', {
            'fields': (
                'email', 'username', 'password1', 'password2'
            )
        }),
        ('Información Personal', {
            'fields': (
                'nombres', 'apellido_paterno', 'apellido_materno',
                'tipo_documento', 'numero_documento', 'telefono'
            )
        }),
        ('Configuración Inicial', {
            'fields': (
                'empresa', 'cargo', 'area', 'es_admin_empresa'
            )
        })
    )

    def get_nombre_completo(self, obj):
        """Mostrar nombre completo en la lista"""
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'

    def get_estado_bloqueo(self, obj):
        """Mostrar estado de bloqueo del usuario"""
        if obj.esta_bloqueado():
            return format_html(
                '<span style="color: red;">🔒 Bloqueado hasta {}</span>',
                obj.bloqueado_hasta.strftime('%d/%m/%Y %H:%M')
            )
        elif not obj.is_active:
            return format_html('<span style="color: orange;">⏸️ Inactivo</span>')
        else:
            return format_html('<span style="color: green;">✅ Activo</span>')
    get_estado_bloqueo.short_description = 'Estado'

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('empresa')

    # Acciones personalizadas
    actions = ['activar_usuarios', 'desactivar_usuarios', 'desbloquear_usuarios']

    def activar_usuarios(self, request, queryset):
        """Activar usuarios seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} usuario(s) activado(s) correctamente.'
        )
    activar_usuarios.short_description = "Activar usuarios seleccionados"

    def desactivar_usuarios(self, request, queryset):
        """Desactivar usuarios seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} usuario(s) desactivado(s) correctamente.'
        )
    desactivar_usuarios.short_description = "Desactivar usuarios seleccionados"

    def desbloquear_usuarios(self, request, queryset):
        """Desbloquear usuarios seleccionados"""
        for usuario in queryset:
            usuario.desbloquear_usuario()
        self.message_user(
            request,
            f'{queryset.count()} usuario(s) desbloqueado(s) correctamente.'
        )
    desbloquear_usuarios.short_description = "Desbloquear usuarios seleccionados"


# =============================================================================
# ADMIN PARA ROLES
# =============================================================================
class RolUsuarioInline(admin.TabularInline):
    """Inline para usuarios de un rol"""
    model = UsuarioRol
    extra = 0
    fields = ['usuario', 'fecha_asignacion', 'activo']
    readonly_fields = ['fecha_asignacion']


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """
    Administración de roles del sistema
    """
    list_display = [
        'nombre', 'descripcion', 'es_rol_sistema', 
        'get_cantidad_usuarios', 'activo'
    ]
    
    list_filter = ['es_rol_sistema', 'activo']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    inlines = [RolUsuarioInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'es_rol_sistema')
        }),
        ('Permisos Especiales', {
            'fields': ('permisos_especiales',),
            'description': 'Configuración JSON de permisos específicos del sistema'
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ['collapse']
        })
    )

    def get_cantidad_usuarios(self, obj):
        """Mostrar cantidad de usuarios con este rol"""
        count = obj.usuarios_asignados.filter(activo=True).count()
        return f"{count} usuario(s)"
    get_cantidad_usuarios.short_description = 'Usuarios Asignados'

    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar roles del sistema"""
        if obj and obj.es_rol_sistema:
            return False
        return super().has_delete_permission(request, obj)


# =============================================================================
# ADMIN PARA PERMISOS PERSONALIZADOS
# =============================================================================
@admin.register(PermisoPersonalizado)
class PermisoPersonalizadoAdmin(admin.ModelAdmin):
    """
    Administración de permisos personalizados
    """
    list_display = [
        'nombre', 'codigo', 'modulo', 'accion', 
        'es_critico', 'activo'
    ]
    
    list_filter = ['modulo', 'accion', 'es_critico', 'activo']
    search_fields = ['nombre', 'codigo', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('modulo', 'accion', 'es_critico')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ['collapse']
        })
    )


# =============================================================================
# ADMIN PARA SESIONES
# =============================================================================
@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    """
    Administración de sesiones de usuarios
    """
    list_display = [
        'usuario', 'fecha_inicio', 'ip_address', 
        'dispositivo', 'navegador', 'activa'
    ]
    
    list_filter = [
        'activa', 'dispositivo', 'navegador', 'fecha_inicio'
    ]
    
    search_fields = [
        'usuario__email', 'usuario__nombres', 'ip_address'
    ]
    
    readonly_fields = [
        'usuario', 'token_sesion', 'fecha_inicio', 
        'fecha_ultimo_acceso', 'fecha_cierre', 'ip_address',
        'user_agent', 'dispositivo', 'navegador', 'ubicacion'
    ]
    
    date_hierarchy = 'fecha_inicio'
    
    def has_add_permission(self, request):
        """No permitir crear sesiones manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir ver, no modificar"""
        return False


# =============================================================================
# ADMIN PARA LOG DE ACTIVIDAD
# =============================================================================
@admin.register(LogActividadUsuario)
class LogActividadUsuarioAdmin(admin.ModelAdmin):
    """
    Administración de logs de actividad
    """
    list_display = [
        'usuario', 'fecha', 'accion', 'modulo', 
        'descripcion_corta', 'ip_address'
    ]
    
    list_filter = [
        'accion', 'modulo', 'fecha'
    ]
    
    search_fields = [
        'usuario__email', 'usuario__nombres', 'descripcion',
        'ip_address'
    ]
    
    readonly_fields = [
        'usuario', 'fecha', 'accion', 'modulo', 'descripcion',
        'objeto_id', 'objeto_tipo', 'ip_address', 'datos_adicionales'
    ]
    
    date_hierarchy = 'fecha'
    
    def descripcion_corta(self, obj):
        """Mostrar descripción truncada"""
        if len(obj.descripcion) > 50:
            return f"{obj.descripcion[:50]}..."
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def has_add_permission(self, request):
        """No permitir crear logs manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir ver, no modificar"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar logs"""
        return False


# =============================================================================
# CONFIGURACIÓN GLOBAL DEL ADMIN
# =============================================================================
# Personalizar títulos del admin
admin.site.site_header = 'FELICITA - Panel de Administración'
admin.site.site_title = 'FELICITA Admin'
admin.site.index_title = 'Sistema de Facturación Electrónica - Administración'

# Cambiar el nombre de "Autenticación y Autorización" en el admin
from django.contrib.auth.models import Group
admin.site.unregister(Group)  # Remover grupos de Django por defecto