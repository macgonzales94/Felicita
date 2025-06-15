"""
FELICITA - Apps Core
Sistema de Facturación Electrónica para Perú

Configuración de la aplicación Core
"""

from django.apps import AppConfig
import logging

logger = logging.getLogger('felicita.core')

class CoreConfig(AppConfig):
    """Configuración de la aplicación Core"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.core'
    verbose_name = 'Core - Entidades Base'
    
    def ready(self):
        """Configuración cuando la app está lista"""
        # Importar signals para que se registren
        try:
            from . import signals
            logger.info("✅ Signals Core cargados correctamente")
        except ImportError as e:
            logger.warning(f"⚠️  No se pudieron cargar signals Core: {e}")
        
        # Registrar validadores personalizados
        try:
            self.registrar_validadores()
            logger.info("✅ Validadores Core registrados correctamente")
        except Exception as e:
            logger.error(f"❌ Error registrando validadores Core: {e}")
        
        # Configurar permisos personalizados
        try:
            self.configurar_permisos()
            logger.info("✅ Permisos Core configurados correctamente")
        except Exception as e:
            logger.error(f"❌ Error configurando permisos Core: {e}")
        
        logger.info("🔧 Aplicación Core inicializada correctamente")
    
    def registrar_validadores(self):
        """Registrar validadores personalizados"""
        from django.core import validators
        from .models import validar_ruc_peruano, validar_dni_peruano
        
        # Los validadores ya están definidos en models.py
        # Aquí se podrían registrar validadores adicionales si es necesario
        pass
    
    def configurar_permisos(self):
        """Configurar permisos personalizados"""
        # Los permisos se definen en los Meta de los modelos
        # Aquí se pueden configurar permisos adicionales si es necesario
        pass