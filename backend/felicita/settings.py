"""
Configuración principal Django para FELICITA
Sistema de Facturación Electrónica para Perú

Por defecto importa configuración local para desarrollo.
En producción se debe configurar DJANGO_SETTINGS_MODULE apropiadamente.
"""

import os

# Determinar qué configuración usar
environment = os.environ.get('DJANGO_ENVIRONMENT', 'local')

if environment == 'production':
    from .settings.production import *
elif environment == 'staging':
    from .settings.staging import *
else:
    # Por defecto usar configuración local
    from .settings.local import *

print(f"🔧 FELICITA cargado con configuración: {environment.upper()}")