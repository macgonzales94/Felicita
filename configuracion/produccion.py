"""
CONFIGURACIÓN PRODUCCIÓN - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú
"""

from .base import *
from decouple import config
import dj_database_url

# =============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN
# =============================================================================
DEBUG = False
ENVIRONMENT = 'production'

# Hosts permitidos en producción
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='api.felicita.pe,felicita.pe',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# =============================================================================
# BASE DE DATOS PRODUCCIÓN
# =============================================================================
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# =============================================================================
# CONFIGURACIÓN CORS PRODUCCIÓN
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://app.felicita.pe',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# CONFIGURACIÓN CACHE PRODUCCIÓN
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'felicita_prod',
        'TIMEOUT': config('CACHE_TTL', default=3600, cast=int),
    }
}

# =============================================================================
# CONFIGURACIÓN EMAIL PRODUCCIÓN
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='FELICITA <noreply@felicita.pe>')

# =============================================================================
# CONFIGURACIÓN SEGURIDAD PRODUCCIÓN
# =============================================================================
# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies seguras
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# =============================================================================
# CONFIGURACIÓN ARCHIVOS ESTÁTICOS PRODUCCIÓN
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración para AWS S3 (opcional)
if config('USE_S3_STORAGE', default=False, cast=bool):
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# =============================================================================
# CONFIGURACIÓN LOGGING PRODUCCIÓN
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
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/felicita/app.log',
            'maxBytes': 50 * 1024 * 1024,  # 50 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/felicita/error.log',
            'maxBytes': 50 * 1024 * 1024,  # 50 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['error_file', 'sentry'],
            'level': 'ERROR',
            'propagate': False,
        },
        'felicita': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'aplicaciones': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# CONFIGURACIÓN SENTRY (MONITOREO DE ERRORES)
# =============================================================================
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    # Configuración de Sentry
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            CeleryIntegration(monitor_beat_tasks=True),
            RedisIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
        release=config('APP_VERSION', default='1.0.0'),
    )

# =============================================================================
# CONFIGURACIÓN CELERY PRODUCCIÓN
# =============================================================================
CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = config('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Configuración de concurrencia
CELERY_WORKER_CONCURRENCY = config('CELERY_CONCURRENCY', default=4, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# Configuración de tareas
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_STORE_EAGER_RESULT = True

# =============================================================================
# CONFIGURACIÓN NUBEFACT PRODUCCIÓN
# =============================================================================
NUBEFACT_CONFIGURACION.update({
    'MODO': 'produccion',
    'API_URL': 'https://api.nubefact.com/api/v1',
    'TOKEN': config('NUBEFACT_TOKEN'),
    'RUC_EMISOR': config('NUBEFACT_RUC_EMISOR'),
})

# =============================================================================
# CONFIGURACIÓN APIS PERÚ PRODUCCIÓN
# =============================================================================
APIS_PERU.update({
    'RENIEC_TOKEN': config('RENIEC_API_TOKEN'),
    'SUNAT_TOKEN': config('SUNAT_API_TOKEN'),
})

# =============================================================================
# CONFIGURACIÓN PERFORMANCE
# =============================================================================
# Compresión de respuestas
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
] + MIDDLEWARE

# Configuración de base de datos optimizada
DATABASES['default'].update({
    'CONN_MAX_AGE': 600,
    'CONN_HEALTH_CHECKS': True,
    'OPTIONS': {
        'charset': 'utf8',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'isolation_level': 'read committed',
    },
})

# =============================================================================
# CONFIGURACIÓN BACKUP AUTOMÁTICO
# =============================================================================
BACKUP_ENABLED = config('BACKUP_ENABLED', default=True, cast=bool)
BACKUP_STORAGE = config('BACKUP_STORAGE', default='local')  # local, s3
BACKUP_RETENTION_DAYS = config('BACKUP_RETENTION_DAYS', default=30, cast=int)

# =============================================================================
# CONFIGURACIÓN ADICIONAL PRODUCCIÓN
# =============================================================================
# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Admin
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Tamaño máximo de archivo
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Configuración de whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# =============================================================================
# CONFIGURACIÓN HEALTH CHECKS
# =============================================================================
HEALTH_CHECKS = {
    'database': True,
    'cache': True,
    'storage': True,
    'external_apis': False,  # Puede ser lento
}

# =============================================================================
# CONFIGURACIÓN MONITORING
# =============================================================================
MONITORING = {
    'metrics_enabled': config('METRICS_ENABLED', default=True, cast=bool),
    'prometheus_endpoint': config('PROMETHEUS_ENDPOINT', default='/metrics'),
    'health_check_endpoint': config('HEALTH_ENDPOINT', default='/health'),
}

print("🚀 FELICITA - Configuración de producción cargada")
print(f"📊 Debug: {DEBUG}")
print(f"🗄️  Base de datos: PostgreSQL en la nube")
print(f"🔄 Cache: Redis en la nube")
print(f"📧 Email: SMTP configurado")
print(f"🔐 HTTPS: Habilitado")
print(f"📊 Sentry: {'Habilitado' if SENTRY_DSN else 'Deshabilitado'}")

import logging