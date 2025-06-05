from django.apps import AppConfig


class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.clientes'
    verbose_name = 'Clientes y Proveedores'
    
    def ready(self):
        import aplicaciones.clientes.signals