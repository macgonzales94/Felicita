"""
Configuración de settings para FELICITA
Sistema de Facturación Electrónica para Perú

Este archivo determina qué configuración usar según el entorno.
"""

import os
from decouple import config

# Determinar entorno
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='local')

print(f"🔧 Cargando configuración para entorno: {ENVIRONMENT}")

# Importar configuración según entorno
if ENVIRONMENT == 'local':
    from .local import *
    print("✅ Configuración LOCAL cargada")
elif ENVIRONMENT == 'development':
    from .development import *
    print("✅ Configuración DEVELOPMENT cargada")
elif ENVIRONMENT == 'staging':
    from .staging import *
    print("✅ Configuración STAGING cargada")
elif ENVIRONMENT == 'production':
    from .production import *
    print("✅ Configuración PRODUCTION cargada")
else:
    # Por defecto usar local
    from .local import *
    print(f"⚠️  Entorno '{ENVIRONMENT}' no reconocido, usando LOCAL por defecto")

# Validaciones post-carga
if DEBUG and ENVIRONMENT in ['staging', 'production']:
    raise ValueError(f"❌ DEBUG no debe estar activado en entorno {ENVIRONMENT}")

print("🚀 Settings de FELICITA cargados correctamente")