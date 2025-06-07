"""
CONFIGURACIÓN APP CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    """
    Configuración de la aplicación Core
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.core'
    verbose_name = 'FELICITA - Módulo Core'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista
        """
        # Importar signals
        try:
            from . import signals
        except ImportError:
            pass
        
        # Conectar signal para crear datos iniciales después de migrate
        post_migrate.connect(self.crear_configuraciones_iniciales, sender=self)
    
    def crear_configuraciones_iniciales(self, sender, **kwargs):
        """
        Crear configuraciones iniciales del sistema después de las migraciones
        """
        from .models import ConfiguracionSistema
        
        # Configuraciones por defecto
        configuraciones_default = [
            {
                'clave': 'SISTEMA_NOMBRE',
                'valor': 'FELICITA',
                'descripcion': 'Nombre del sistema',
                'tipo_dato': 'string'
            },
            {
                'clave': 'SISTEMA_VERSION',
                'valor': '1.0.0',
                'descripcion': 'Versión del sistema',
                'tipo_dato': 'string'
            },
            {
                'clave': 'IGV_PORCENTAJE',
                'valor': '18',
                'descripcion': 'Porcentaje de IGV en Perú',
                'tipo_dato': 'integer'
            },
            {
                'clave': 'MONEDA_BASE',
                'valor': 'PEN',
                'descripcion': 'Moneda base del sistema',
                'tipo_dato': 'string'
            },
            {
                'clave': 'METODO_INVENTARIO',
                'valor': 'PEPS',
                'descripcion': 'Método de valuación de inventarios',
                'tipo_dato': 'string'
            },
            {
                'clave': 'FORMATO_FECHA',
                'valor': 'dd/mm/yyyy',
                'descripcion': 'Formato de fecha del sistema',
                'tipo_dato': 'string'
            },
            {
                'clave': 'DECIMALES_CANTIDAD',
                'valor': '4',
                'descripcion': 'Decimales para cantidades',
                'tipo_dato': 'integer'
            },
            {
                'clave': 'DECIMALES_PRECIO',
                'valor': '4',
                'descripcion': 'Decimales para precios',
                'tipo_dato': 'integer'
            },
            {
                'clave': 'DECIMALES_TOTAL',
                'valor': '2',
                'descripcion': 'Decimales para totales',
                'tipo_dato': 'integer'
            },
            {
                'clave': 'LIMITE_STOCK_BAJO',
                'valor': '10',
                'descripcion': 'Límite para alertas de stock bajo',
                'tipo_dato': 'integer'
            },
        ]
        
        try:
            # Crear configuraciones que no existen
            for config_data in configuraciones_default:
                ConfiguracionSistema.objects.get_or_create(
                    clave=config_data['clave'],
                    defaults=config_data
                )
        except Exception as e:
            # En caso de error, no interrumpir el proceso de migración
            print(f"Warning: No se pudieron crear configuraciones iniciales: {e}")
    
    def get_version(self):
        """
        Obtener versión de la aplicación
        """
        return "1.0.0"
    
    def get_description(self):
        """
        Obtener descripción de la aplicación
        """
        return "Módulo core de FELICITA - Gestión de empresas, clientes, productos y configuraciones generales"