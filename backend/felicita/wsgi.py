"""
WSGI config for FELICITA project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar el módulo de settings por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

try:
    # Obtener la aplicación WSGI
    application = get_wsgi_application()
    
    # Log de inicialización en producción
    if not os.environ.get('DEBUG', False):
        import logging
        logger = logging.getLogger('felicita')
        logger.info("🚀 FELICITA WSGI application initialized successfully")
        
except Exception as e:
    # Log del error
    import logging
    logging.error(f"❌ Error initializing FELICITA WSGI application: {e}")
    raise