"""
FELICITA - Configuración Django Completa
Sistema de Facturación Electrónica para Perú

Configuración completa con seguridad, JWT y todas las funcionalidades
"""

import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ===========================================
# CONFIGURACIÓN BÁSICA
# ===========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='tu_clave_secreta_super_segura_cambiar_en_produccion')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')

# ===========================================
# APLICACIONES DJANGO
# ===========================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_extensions',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'aplicaciones.core',
    'aplicaciones.usuarios',
    'aplicaciones.facturacion',
    'aplicaciones.inventario',
    'aplicaciones.contabilidad',
    'aplicaciones.integraciones',
    'aplicaciones.punto_venta',
    'aplicaciones.reportes',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ===========================================
# MIDDLEWARE
# ===========================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'aplicaciones.usuarios.middleware.AuditMiddleware',
    'aplicaciones.usuarios.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ===========================================
# TEMPLATES
# ===========================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ===========================================
# BASE DE DATOS
# ===========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NOMBRE', default='felicita_db'),
        'USER': config('DB_USUARIO', default='felicita_user'),
        'PASSWORD': config('DB_PASSWORD', default='felicita_pass'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'autocommit': True,
        },
        'CONN_MAX_AGE': 60,
    }
}

# ===========================================
# CACHE
# ===========================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,
        'KEY_PREFIX': 'felicita',
        'VERSION': 1,
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ===========================================
# VALIDADORES DE CONTRASEÑA
# ===========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'aplicaciones.usuarios.validators.CustomPasswordValidator',
    },
]

# ===========================================
# INTERNACIONALIZACIÓN
# ===========================================

LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# ===========================================
# ARCHIVOS ESTÁTICOS
# ===========================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===========================================
# ARCHIVOS DE MEDIA
# ===========================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================================
# CONFIGURACIÓN DEL MODELO USUARIO
# ===========================================

AUTH_USER_MODEL = 'usuarios.Usuario'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================
# DJANGO REST FRAMEWORK
# ===========================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': config('THROTTLE_ANON', default='100/hour'),
        'user': config('THROTTLE_USER', default='1000/hour'),
        'login': config('THROTTLE_LOGIN', default='10/min'),
        'password_reset': '5/min',
        'api': '2000/hour',
    },
    'EXCEPTION_HANDLER': 'aplicaciones.core.exceptions.custom_exception_handler',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
}

# ===========================================
# CONFIGURACIÓN JWT
# ===========================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=config('JWT_ACCESS_TOKEN_LIFETIME', default=1, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': config('JWT_ROTATE_REFRESH_TOKENS', default=True, cast=bool),
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'FELICITA',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ===========================================
# CORS HEADERS
# ===========================================

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=DEBUG, cast=bool)

CORS_ALLOWED_HEADERS = [
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
# CONFIGURACIÓN DE SEGURIDAD
# ===========================================

# Configuración HTTPS para producción
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuración de cookies
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 horas

CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Headers de seguridad
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# ===========================================
# CONFIGURACIÓN DE LOGGING
# ===========================================

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
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'felicita.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'audit.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'felicita': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'felicita.usuarios': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'felicita.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ===========================================
# CONFIGURACIÓN DE EMAIL
# ===========================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@felicita.pe')

# ===========================================
# CONFIGURACIÓN CELERY
# ===========================================

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
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
# API DOCUMENTATION
# ===========================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'FELICITA API',
    'DESCRIPTION': 'Sistema de Facturación Electrónica para Perú - API REST',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Servidor de Desarrollo'},
        {'url': 'https://api.felicita.pe', 'description': 'Servidor de Producción'},
    ],
    'EXTERNAL_DOCS': {
        'description': 'Documentación SUNAT',
        'url': 'https://www.sunat.gob.pe/ol-ti-itconsultaunificada/consultas.jsp',
    },
    'SECURITY': [
        {
            'Bearer Auth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    ],
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.contrib.djangorestframework_simplejwt.postprocess_schema',
    ],
}

# ===========================================
# CONFIGURACIONES ESPECÍFICAS FELICITA
# ===========================================

# Configuración de empresa por defecto
EMPRESA_CONFIG = {
    'ruc': config('EMPRESA_RUC', default='20123456789'),
    'razon_social': config('EMPRESA_RAZON_SOCIAL', default='EMPRESA DEMO SAC'),
    'direccion': config('EMPRESA_DIRECCION', default='AV. DEMO 123, LIMA, PERU'),
    'telefono': config('EMPRESA_TELEFONO', default='01-1234567'),
    'email': config('EMPRESA_EMAIL', default='demo@felicita.pe'),
}

# Configuración de facturación
FACTURACION_CONFIG = {
    'igv_porcentaje': config('IGV_PORCENTAJE', default=18.0, cast=float),
    'moneda_defecto': config('MONEDA_DEFECTO', default='PEN'),
    'numeracion_automatica': config('NUMERACION_AUTOMATICA', default=True, cast=bool),
    'envio_automatico_sunat': config('ENVIO_AUTOMATICO_SUNAT', default=True, cast=bool),
}

# Configuración de integraciones
NUBEFACT_CONFIG = {
    'base_url': config('NUBEFACT_BASE_URL', default='https://api.nubefact.com/api/v1'),
    'token': config('NUBEFACT_TOKEN', default=''),
    'ruc': config('NUBEFACT_RUC', default=''),
    'mode': config('NUBEFACT_MODE', default='demo'),
}

# Configuración de APIs Perú
APIS_PERU_CONFIG = {
    'reniec_url': config('RENIEC_API_URL', default=''),
    'sunat_url': config('SUNAT_API_URL', default=''),
    'reniec_token': config('RENIEC_API_TOKEN', default=''),
    'sunat_token': config('SUNAT_API_TOKEN', default=''),
}

# ===========================================
# CONFIGURACIÓN DE SEGURIDAD ADICIONAL
# ===========================================

# Rate limiting adicional
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_USE_CACHE = 'default'

# Configuración de seguridad de usuario
USER_SECURITY_CONFIG = {
    'max_login_attempts': config('MAX_LOGIN_ATTEMPTS', default=5, cast=int),
    'lockout_duration_minutes': config('LOCKOUT_DURATION_MINUTES', default=30, cast=int),
    'password_reset_timeout': config('PASSWORD_RESET_TIMEOUT', default=3600, cast=int),
    'session_timeout_minutes': config('SESSION_TIMEOUT_MINUTES', default=480, cast=int),
    'require_unique_passwords': config('REQUIRE_UNIQUE_PASSWORDS', default=True, cast=bool),
    'password_history_count': config('PASSWORD_HISTORY_COUNT', default=5, cast=int),
}

# ===========================================
# CONFIGURACIÓN DE DESARROLLO
# ===========================================

if DEBUG:
    # Configuraciones específicas para desarrollo
    CORS_ALLOW_ALL_ORIGINS = True
    
    # Desactivar HTTPS en desarrollo
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
    # Logging más detallado en desarrollo
    LOGGING['loggers']['felicita']['level'] = 'DEBUG'
    
    # Email en consola para desarrollo
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===========================================
# VALIDACIONES FINALES
# ===========================================

# Verificar configuraciones críticas en producción
if not DEBUG:
    required_settings = [
        'SECRET_KEY',
        'ALLOWED_HOSTS',
        'NUBEFACT_TOKEN',
        'EMAIL_HOST_USER',
    ]
    
    for setting in required_settings:
        if not config(setting, default=None):
            raise ValueError(f"{setting} es requerido en producción")

print(f"🚀 FELICITA - Configuración cargada correctamente")
print(f"🐛 DEBUG: {DEBUG}")
print(f"🔒 SSL Redirect: {SECURE_SSL_REDIRECT}")
print(f"🗄️  Base de datos: {DATABASES['default']['NAME']}")
print(f"📧 Email Backend: {EMAIL_BACKEND}")
print(f"🔄 Cache Backend: {CACHES['default']['BACKEND']}")
print(f"📁 Media Root: {MEDIA_ROOT}")
print(f"📊 Logging configurado correctamente")