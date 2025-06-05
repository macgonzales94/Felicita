from django.apps import AppConfig


class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.productos'
    verbose_name = 'Productos y Servicios'
    
    def ready(self):
        import aplicaciones.productos.signals