from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.usuarios'
    verbose_name = 'Usuarios y Autenticación'
    
    def ready(self):
        import aplicaciones.usuarios.signals