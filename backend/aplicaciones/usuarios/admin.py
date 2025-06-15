from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, SesionUsuario, LogAuditoria

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'rol', 'empresa', 'is_active', 'date_joined']
    list_filter = ['rol', 'empresa', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información FELICITA', {
            'fields': ('empresa', 'rol', 'telefono', 'documento_identidad', 'sucursales')
        }),
        ('Configuraciones', {
            'fields': ('preferencias', 'notificaciones_email', 'notificaciones_sistema')
        }),
        ('Control de Acceso', {
            'fields': ('ultimo_acceso_ip', 'intentos_fallidos', 'bloqueado_hasta')
        }),
    )

@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'ip_address', 'fecha_inicio', 'fecha_ultimo_uso', 'activa']
    list_filter = ['activa', 'fecha_inicio']
    search_fields = ['usuario__username', 'ip_address']
    readonly_fields = ['fecha_inicio', 'fecha_ultimo_uso']

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'modelo', 'fecha', 'ip_address']
    list_filter = ['accion', 'modelo', 'fecha']
    search_fields = ['usuario__username', 'descripcion']
    readonly_fields = ['fecha']