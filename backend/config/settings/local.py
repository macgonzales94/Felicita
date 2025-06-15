"""
FELICITA - Configuración Local Django
Sistema de Facturación Electrónica para Perú

Configuraciones específicas para desarrollo local
"""

from .base import *
from decouple import config

# ===========================================
# CONFIGURACIÓN DESARROLLO
# ===========================================

DEBUG = True
ENVIRONMENT = 'local'

# Hosts permitidos en desarrollo
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# ===========================================
# APLICACIONES DESARROLLO
# ===========================================

INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# ===========================================
# MIDDLEWARE DESARROLLO
# ===========================================

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# ===========================================
# BASE DE DATOS MYSQL LOCAL
# ===========================================

DATABASES = {
    'default': {
        'ENGINE': config('DB_LOCAL_ENGINE', default='django.db.backends.mysql'),
        'NAME': config('DB_LOCAL_NOMBRE', default='felicita_db'),
        'USER': config('DB_LOCAL_USUARIO', default='felicita_user'),
        'PASSWORD': config('DB_LOCAL_PASSWORD', default='dev_password_123'),
        'HOST': config('DB_LOCAL_HOST', default='localhost'),
        'PORT': config('DB_LOCAL_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
        'TEST': {
            'NAME': 'test_felicita_db',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# ===========================================
# CACHE REDIS LOCAL
# ===========================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default='felicita_redis_123'),
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'felicita_dev',
        'TIMEOUT': 300,  # 5 minutos en desarrollo
    }
}

# ===========================================
# CORS CONFIGURACIÓN DESARROLLO
# ===========================================

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
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

# ===========================================
# DEBUG TOOLBAR
# ===========================================

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'SHOW_COLLAPSED': True,
    'SHOW_TEMPLATE_CONTEXT': True,
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# ===========================================
# EMAIL DESARROLLO
# ===========================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===========================================
# NUBEFACT MODO DEMO
# ===========================================

NUBEFACT_CONFIG.update({
    'mode': 'demo',
    'base_url': 'https://demo-api.nubefact.com/api/v1',
    'token': config('NUBEFACT_TOKEN', default='demo_token_aqui'),
})

# ===========================================
# LOGGING DESARROLLO
# ===========================================

LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['felicita']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Agregar handler específico para desarrollo
LOGGING['handlers']['development'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
    'formatter': 'verbose',
}

LOGGING['loggers']['aplicaciones'] = {
    'handlers': ['development', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}

# ===========================================
# DJANGO EXTENSIONS
# ===========================================

SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = None

# ===========================================
# SEGURIDAD DESARROLLO
# ===========================================

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# ===========================================
# ARCHIVOS ESTÁTICOS DESARROLLO
# ===========================================

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# No usar WhiteNoise en desarrollo
MIDDLEWARE.remove('whitenoise.middleware.WhiteNoiseMiddleware')

# ===========================================
# CONFIGURACIÓN ESPECÍFICA DESARROLLO
# ===========================================

# Permitir comandos de management personalizados
MANAGEMENT_COMMANDS_ENABLED = True

# Mostrar queries SQL en shell
SHELL_PLUS_PRINT_SQL = True

# Configuración para datos de prueba
LOAD_SAMPLE_DATA = True

# Configuración para testing
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# ===========================================
# CONFIGURACIÓN CELERY DESARROLLO
# ===========================================

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# ===========================================
# API DOCUMENTATION DESARROLLO
# ===========================================

SPECTACULAR_SETTINGS.update({
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Servidor de Desarrollo'},
        {'url': 'http://127.0.0.1:8000', 'description': 'Servidor Local'},
    ],
    'SERVE_PERMISSIONS': [],  # Sin restricciones en desarrollo
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
})

# ===========================================
# CONFIGURACIÓN PERFORMANCE DESARROLLO
# ===========================================

# No comprimir archivos estáticos en desarrollo
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# No usar cache en templates en desarrollo
TEMPLATE_DEBUG = True

# ===========================================
# CONFIGURACIÓN MEDIA DESARROLLO
# ===========================================

# Crear directorios de media automáticamente
import os
media_dirs = [
    'comprobantes',
    'reportes', 
    'uploads',
    'temp',
]

for dir_name in media_dirs:
    dir_path = MEDIA_ROOT / dir_name
    os.makedirs(dir_path, exist_ok=True)

# ===========================================
# VARIABLES ESPECÍFICAS DESARROLLO
# ===========================================

# Configuración para desarrollo con datos ficticios
EMPRESA_CONFIG.update({
    'ruc': '20123456789',
    'razon_social': 'EMPRESA DEMO FELICITA SAC',
    'direccion': 'AV. DESARROLLO 123, SAN ISIDRO, LIMA',
    'telefono': '01-1234567',
    'email': 'demo@felicita.pe',
})

# Configuración para pruebas
TESTING_MODE = True
USE_SAMPLE_DATA = True

print("🔧 FELICITA - Configuración LOCAL cargada correctamente")
print(f"📍 Base de datos: {DATABASES['default']['NAME']}@{DATABASES['default']['HOST']}")
print(f"🔄 Cache Redis: {CACHES['default']['LOCATION']}")
print(f"🌐 CORS Origins: {CORS_ALLOWED_ORIGINS}")
print(f"📧 Email Backend: {EMAIL_BACKEND}")