"""
WSGI config for FELICITA project.
Sistema de Facturación Electrónica para Perú

Expone la aplicación WSGI como una variable a nivel de módulo llamada 'application'.

Para más información sobre este archivo, ver:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Configurar el settings module por defecto para FELICITA
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felicita.settings.local')

# Crear la aplicación WSGI para FELICITA
application = get_wsgi_application()