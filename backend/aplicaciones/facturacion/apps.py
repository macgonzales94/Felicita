from django.apps import AppConfig


class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.facturacion'
    verbose_name = 'Facturación Electrónica'
    
    def ready(self):
        import aplicaciones.facturacion.signals