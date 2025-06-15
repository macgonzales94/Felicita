"""
FELICITA - Settings Init
Sistema de Facturación Electrónica para Perú

Configuración automática del ambiente basado en variables de entorno
"""

import os
from decouple import config

# Determinar el ambiente basado en variables de entorno
ENVIRONMENT = config('ENVIRONMENT', default='local').lower()

# Mapeo de ambientes a módulos de configuración
ENVIRONMENT_SETTINGS = {
    'local': 'config.settings.local',
    'development': 'config.settings.local',
    'dev': 'config.settings.local',
    'testing': 'config.settings.testing',
    'test': 'config.settings.testing',
    'production': 'config.settings.produccion',
    'prod': 'config.settings.produccion',
    'staging': 'config.settings.produccion',
}

# Obtener el módulo de configuración apropiado
settings_module = ENVIRONMENT_SETTINGS.get(
    ENVIRONMENT, 
    'config.settings.local'
)

# Configurar Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

print(f"🔧 FELICITA - Ambiente detectado: {ENVIRONMENT.upper()}")
print(f"📁 Módulo de configuración: {settings_module}")

# Exportar el ambiente para uso en otros módulos
__all__ = ['ENVIRONMENT', 'settings_module']