from django.apps import AppConfig


class InventariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.inventarios'
    verbose_name = 'Inventarios y Almacenes'
    
    def ready(self):
        import aplicaciones.inventarios.signals