"""
CONFIGURACIÓN DESARROLLO LOCAL - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú
"""

from .base import *
from decouple import config

# =============================================================================
# CONFIGURACIÓN DE DESARROLLO
# =============================================================================
DEBUG = True
ENVIRONMENT = 'development'

# Hosts permitidos en desarrollo
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'felicita-backend',  # Para Docker
]

# =============================================================================
# APPS ADICIONALES PARA DESARROLLO
# =============================================================================
DEVELOPMENT_APPS = [
    'debug_toolbar',
    'django_extensions',
]

INSTALLED_APPS += DEVELOPMENT_APPS

# =============================================================================
# MIDDLEWARE ADICIONAL PARA DESARROLLO
# =============================================================================
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# =============================================================================
# CONFIGURACIÓN DEBUG TOOLBAR
# =============================================================================
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'SHOW_COLLAPSED': True,
    'PROFILER_MAX_DEPTH': 10,
}

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
]

# Para Docker
import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + '1' for ip in ips if ip.endswith('.1')]

# =============================================================================
# BASE DE DATOS DESARROLLO
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='felicita_db'),
        'USER': config('DB_USER', default='felicita_user'),
        'PASSWORD': config('DB_PASSWORD', default='felicita_2024_dev'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'charset': 'utf8',
        },
        'CONN_MAX_AGE': 0,  # Sin pooling en desarrollo
        'ATOMIC_REQUESTS': True,
    }
}

# =============================================================================
# CONFIGURACIÓN CORS PARA DESARROLLO
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
]

# =============================================================================
# CONFIGURACIÓN CACHE DESARROLLO
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
        },
        'KEY_PREFIX': 'felicita_dev',
        'TIMEOUT': 300,  # 5 minutos en desarrollo
    }
}

# Cache dummy para desarrollo si no hay Redis
if config('USE_DUMMY_CACHE', default=False, cast=bool):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# =============================================================================
# EMAIL DESARROLLO (CONSOLE)
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# LOGGING DESARROLLO
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'colored': {
            'format': '\033[92m{levelname}\033[0m {asctime} \033[94m{module}\033[0m {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'felicita_dev.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if config('SQL_DEBUG', default=False, cast=bool) else 'INFO',
            'propagate': False,
        },
        'felicita': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'aplicaciones': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# =============================================================================
# CONFIGURACIÓN DJANGO REST FRAMEWORK DESARROLLO
# =============================================================================
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # API navegable en desarrollo
    ],
    'PAGE_SIZE': 10,  # Páginas más pequeñas en desarrollo
})

# =============================================================================
# CONFIGURACIÓN ESPECÍFICA DESARROLLO
# =============================================================================

# Nubefact en modo demo para desarrollo
NUBEFACT_CONFIGURACION.update({
    'MODO': 'demo',
    'API_URL': 'https://demo.nubefact.com/api/v1',
    'TOKEN': 'demo_token_nubefact_2024',
})

# Deshabilitar APIs externas en desarrollo si no hay tokens
if not config('RENIEC_API_TOKEN', default=''):
    APIS_PERU['RENIEC_URL'] = None
    
if not config('SUNAT_API_TOKEN', default=''):
    APIS_PERU['SUNAT_URL'] = None

# =============================================================================
# CONFIGURACIÓN ARCHIVOS ESTÁTICOS DESARROLLO
# =============================================================================
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =============================================================================
# CONFIGURACIÓN SEGURIDAD DESARROLLO
# =============================================================================
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# =============================================================================
# CONFIGURACIÓN DJANGO EXTENSIONS
# =============================================================================
SHELL_PLUS_PRINT_SQL = config('SQL_DEBUG', default=False, cast=bool)
SHELL_PLUS_IMPORTS = [
    'from aplicaciones.core.models import *',
    'from aplicaciones.usuarios.models import *',
    'from aplicaciones.facturacion.models import *',
    'from aplicaciones.inventario.models import *',
    'from aplicaciones.contabilidad.models import *',
    'from decimal import Decimal',
    'from datetime import datetime, date, timedelta',
    'import json',
    'import requests',
]

# =============================================================================
# CONFIGURACIÓN PROFILING DESARROLLO
# =============================================================================
if config('PROFILING_ENABLED', default=False, cast=bool):
    MIDDLEWARE.append('silk.middleware.SilkyMiddleware')
    INSTALLED_APPS.append('silk')

# =============================================================================
# CONFIGURACIÓN TEMPLATES DESARROLLO
# =============================================================================
TEMPLATES[0]['OPTIONS']['debug'] = True

# =============================================================================
# CONFIGURACIÓN TESTING
# =============================================================================
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    
    # Cache en memoria para tests
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    
    # Email en memoria para tests
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# =============================================================================
# CONFIGURACIÓN DESARROLLO HOT RELOAD
# =============================================================================
USE_TZ = True
AUTO_RELOAD = True

# Configuración para development server
RUNSERVER_DEFAULT_ADDR = '0.0.0.0'
RUNSERVER_DEFAULT_PORT = '8000'

print("🚀 FELICITA - Configuración de desarrollo cargada")
print(f"📊 Debug: {DEBUG}")
print(f"🗄️  Base de datos: {DATABASES['default']['NAME']}")
print(f"🔄 Cache: {CACHES['default']['BACKEND']}")
print(f"📧 Email: {EMAIL_BACKEND}")

import sys