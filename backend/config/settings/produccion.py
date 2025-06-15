"""
FELICITA - Configuración Producción Django
Sistema de Facturación Electrónica para Perú

Configuraciones específicas para ambiente de producción
"""

from .base import *
from decouple import config
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# ===========================================
# CONFIGURACIÓN PRODUCCIÓN
# ===========================================

DEBUG = False
ENVIRONMENT = 'production'

# Hosts permitidos en producción
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Asegurar que tengamos hosts configurados
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError("ALLOWED_HOSTS debe estar configurado en producción")

# ===========================================
# APLICACIONES PRODUCCIÓN
# ===========================================

INSTALLED_APPS += [
    'django_celery_beat',
    'django_celery_results',
    'cachalot',
    'compressor',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
]

# ===========================================
# BASE DE DATOS MYSQL PRODUCCIÓN
# ===========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_PRODUCCION_NOMBRE'),
        'USER': config('DB_PRODUCCION_USUARIO'),
        'PASSWORD': config('DB_PRODUCCION_PASSWORD'),
        'HOST': config('DB_PRODUCCION_HOST', default='localhost'),
        'PORT': config('DB_PRODUCCION_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
        'CONN_MAX_AGE': 60,  # Conexiones persistentes
        'ATOMIC_REQUESTS': True,  # Transacciones automáticas
    }
}

# ===========================================
# CACHE REDIS PRODUCCIÓN
# ===========================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'felicita_prod',
        'TIMEOUT': CACHE_TIMEOUT,
    }
}

# ===========================================
# SEGURIDAD PRODUCCIÓN
# ===========================================

# HTTPS Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")

# ===========================================
# CORS PRODUCCIÓN
# ===========================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True

# ===========================================
# ARCHIVOS ESTÁTICOS PRODUCCIÓN
# ===========================================

# WhiteNoise para servir archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Compresión de archivos estáticos
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

# ===========================================
# EMAIL PRODUCCIÓN
# ===========================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@felicita.pe')
SERVER_EMAIL = config('SERVER_EMAIL', default='admin@felicita.pe')

# ===========================================
# NUBEFACT PRODUCCIÓN
# ===========================================

NUBEFACT_CONFIG.update({
    'mode': 'production',
    'base_url': 'https://api.nubefact.com/api/v1',
    'token': config('NUBEFACT_TOKEN'),
    'ruc': config('NUBEFACT_RUC'),
    'usuario_secundario': config('NUBEFACT_USUARIO_SECUNDARIO', default=''),
    'clave_secundaria': config('NUBEFACT_CLAVE_SECUNDARIA', default=''),
})

# Validar configuración Nubefact
required_nubefact = ['token', 'ruc']
for key in required_nubefact:
    if not NUBEFACT_CONFIG.get(key):
        raise ValueError(f"NUBEFACT_{key.upper()} es requerido en producción")

# ===========================================
# SENTRY MONITORING
# ===========================================

SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=ENVIRONMENT,
        release=config('SENTRY_RELEASE', default='1.0.0'),
    )

# ===========================================
# LOGGING PRODUCCIÓN
# ===========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'felicita_produccion.log',
            'maxBytes': config('LOG_FILE_MAX_SIZE', default=10485760, cast=int),  # 10MB
            'backupCount': config('LOG_BACKUP_COUNT', default=10, cast=int),
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'felicita_errores.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file', 'mail_admins', 'sentry'],
            'level': 'WARNING',
            'propagate': False,
        },
        'felicita': {
            'handlers': ['file', 'error_file', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
        'aplicaciones.integraciones': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'aplicaciones.facturacion': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ===========================================
# CELERY PRODUCCIÓN
# ===========================================

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=config('REDIS_URL'))
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=config('REDIS_URL'))

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Configuración de tareas
CELERY_TASK_ROUTES = {
    'aplicaciones.integraciones.tasks.*': {'queue': 'integraciones'},
    'aplicaciones.reportes.tasks.*': {'queue': 'reportes'},
    'aplicaciones.facturacion.tasks.*': {'queue': 'facturacion'},
}

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ===========================================
# PERFORMANCE OPTIMIZACIÓN
# ===========================================

# ORM Query Cache
CACHALOT_ENABLED = True
CACHALOT_TIMEOUT = 3600
CACHALOT_CACHE = 'default'

# Template caching
TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Database optimizations
CONN_MAX_AGE = 60

# ===========================================
# HEALTH CHECKS
# ===========================================

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # 90% usage
    'MEMORY_MIN': 100,     # 100 MB
}

# ===========================================
# API DOCUMENTATION PRODUCCIÓN
# ===========================================

SPECTACULAR_SETTINGS.update({
    'SERVERS': [
        {'url': 'https://api.felicita.pe', 'description': 'Servidor de Producción'},
    ],
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SERVE_INCLUDE_SCHEMA': False,
})

# ===========================================
# BACKUP CONFIGURATION
# ===========================================

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR / 'backups'}

# ===========================================
# RATE LIMITING PRODUCCIÓN
# ===========================================

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '50/hour',
    'user': '500/hour',
    'login': '10/min',
    'api': '1000/hour',
}

# ===========================================
# VALIDACIONES FINALES
# ===========================================

# Validar variables críticas
required_settings = [
    'SECRET_KEY',
    'ALLOWED_HOSTS',
    'DB_PRODUCCION_NOMBRE',
    'DB_PRODUCCION_USUARIO', 
    'DB_PRODUCCION_PASSWORD',
]

for setting in required_settings:
    if not config(setting, default=None):
        raise ValueError(f"{setting} es requerido en producción")

# Validar que no estemos en debug
if DEBUG:
    raise ValueError("DEBUG no puede ser True en producción")

# Validar HTTPS
if not config('SECURE_SSL_REDIRECT', default=True, cast=bool):
    print("⚠️  ADVERTENCIA: SSL redirect deshabilitado en producción")

print("🚀 FELICITA - Configuración PRODUCCIÓN cargada correctamente")
print(f"🏢 Hosts permitidos: {ALLOWED_HOSTS}")
print(f"🔒 SSL Redirect: {SECURE_SSL_REDIRECT}")
print(f"📧 Email Host: {EMAIL_HOST}")
print(f"📊 Sentry configurado: {bool(SENTRY_DSN)}")