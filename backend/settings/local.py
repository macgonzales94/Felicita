"""
Configuración Django para desarrollo local - FELICITA
Sistema de Facturación Electrónica para Perú
"""

from .base import *
import os
from decouple import config

# ==============================================
# CONFIGURACIÓN DE DEBUG Y DESARROLLO
# ==============================================

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ==============================================
# BASE DE DATOS POSTGRESQL LOCAL
# ==============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME', default='felicita_db'),
        'USER': config('DATABASE_USER', default='felicita_user'),
        'PASSWORD': config('DATABASE_PASSWORD', default='felicita_password_2024'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
        'OPTIONS': {
            'charset': 'utf8',
        },
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
    }
}

# ==============================================
# CACHE CON REDIS LOCAL
# ==============================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache para sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ==============================================
# CORS PARA FRONTEND LOCAL
# ==============================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ==============================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
# ==============================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================
# LOGGING PARA DESARROLLO
# ==============================================

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
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/felicita_local.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'felicita': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'nubefact': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# ==============================================
# DEBUG TOOLBAR PARA DESARROLLO
# ==============================================

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'SHOW_COLLAPSED': True,
    }
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# ==============================================
# CONFIGURACIÓN ESPECÍFICA PERÚ - DESARROLLO
# ==============================================

# Nubefact en modo DEMO
NUBEFACT_CONFIG = {
    'TOKEN': config('NUBEFACT_TOKEN', default='demo-token'),
    'RUC': config('NUBEFACT_RUC', default='20123456789'),
    'USUARIO_SOL': config('NUBEFACT_USUARIO_SOL', default='MODDATOS'),
    'CLAVE_SOL': config('NUBEFACT_CLAVE_SOL', default='MODDATOS'),
    'MODE': config('NUBEFACT_MODE', default='demo'),
    'BASE_URL': config('NUBEFACT_BASE_URL', default='https://demo-ose.nubefact.com/ol-ti-itcpe/billService'),
}

# Configuración empresa por defecto
EMPRESA_CONFIG = {
    'RUC': config('EMPRESA_RUC', default='20123456789'),
    'RAZON_SOCIAL': config('EMPRESA_RAZON_SOCIAL', default='EMPRESA DEMO FELICITA S.A.C.'),
    'DIRECCION': config('EMPRESA_DIRECCION', default='Av. Lima 123, Lima, Lima, Perú'),
    'TELEFONO': config('EMPRESA_TELEFONO', default='+51 1 234-5678'),
    'EMAIL': config('EMPRESA_EMAIL', default='demo@felicita.pe'),
}

# IGV Perú
IGV_RATE = 0.18
MONEDA_NACIONAL = 'PEN'

# ==============================================
# EMAIL PARA DESARROLLO (CONSOLE)
# ==============================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=1025, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)

# ==============================================
# CONFIGURACIÓN DE TIMEZONE PERÚ
# ==============================================

TIME_ZONE = 'America/Lima'
USE_TZ = True

# ==============================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ==============================================

# JWT para desarrollo
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # Token más largo para desarrollo
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
})

# ==============================================
# CONFIGURACIÓN API DOCUMENTATION
# ==============================================

SPECTACULAR_SETTINGS['SERVE_INCLUDE_SCHEMA'] = True
SPECTACULAR_SETTINGS['SWAGGER_UI_SETTINGS'] = {
    'deepLinking': True,
    'displayOperationId': True,
    'defaultModelsExpandDepth': 2,
    'defaultModelExpandDepth': 2,
    'displayRequestDuration': True,
}

# ==============================================
# CONFIGURACIÓN DE SEGURIDAD RELAJADA PARA DEV
# ==============================================

SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_SSL_REDIRECT = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Rate limiting más permisivo para desarrollo
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=False, cast=bool)

# ==============================================
# CONFIGURACIÓN DE FIXTURES Y SEED DATA
# ==============================================

FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
]

# Crear directorio de logs si no existe
import os
log_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

print("🔧 Configuración Django LOCAL cargada para FELICITA")