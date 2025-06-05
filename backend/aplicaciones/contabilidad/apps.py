from django.apps import AppConfig


class ContabilidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.contabilidad'
    verbose_name = 'Contabilidad'
    
    def ready(self):
        import aplicaciones.contabilidad.signals