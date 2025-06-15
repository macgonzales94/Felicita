"""
FELICITA - Configuración Base Django
Sistema de Facturación Electrónica para Perú

Configuraciones comunes para todos los ambientes
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

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

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
    'corsheaders',
    'django_filters',
    'drf_spectacular',
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
# Se configura en local.py y produccion.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ===========================================
# VALIDACIÓN DE CONTRASEÑAS
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

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===========================================
# ARCHIVOS MEDIA
# ===========================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================================
# MODELO DE USUARIO PERSONALIZADO
# ===========================================

AUTH_USER_MODEL = 'usuarios.Usuario'

# ===========================================
# DJANGO REST FRAMEWORK
# ===========================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
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
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# ===========================================
# JWT SETTINGS
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
}

# ===========================================
# CORS SETTINGS
# ===========================================

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Solo en desarrollo

# ===========================================
# API DOCUMENTATION
# ===========================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'FELICITA API',
    'DESCRIPTION': 'Sistema de Facturación Electrónica para Perú',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Desarrollo Local'},
    ],
    'TAGS': [
        {'name': 'auth', 'description': 'Autenticación y usuarios'},
        {'name': 'facturacion', 'description': 'Facturación electrónica'},
        {'name': 'inventario', 'description': 'Control de inventarios'},
        {'name': 'clientes', 'description': 'Gestión de clientes'},
        {'name': 'productos', 'description': 'Gestión de productos'},
        {'name': 'reportes', 'description': 'Reportes y analytics'},
    ],
}

# ===========================================
# CONFIGURACIÓN NUBEFACT
# ===========================================

NUBEFACT_CONFIG = {
    'mode': config('NUBEFACT_MODE', default='demo'),
    'token': config('NUBEFACT_TOKEN', default=''),
    'ruc': config('NUBEFACT_RUC', default=''),
    'usuario_secundario': config('NUBEFACT_USUARIO_SECUNDARIO', default=''),
    'clave_secundaria': config('NUBEFACT_CLAVE_SECUNDARIA', default=''),
    'base_url': 'https://api.nubefact.com/api/v1',
    'demo_url': 'https://demo-api.nubefact.com/api/v1',
}

# ===========================================
# CONFIGURACIÓN APIS PERÚ
# ===========================================

APIS_PERU_CONFIG = {
    'reniec_url': config('RENIEC_API_URL', default='https://api.reniec.cloud/dni'),
    'sunat_url': config('SUNAT_API_URL', default='https://api.sunat.cloud/ruc'),
    'reniec_token': config('RENIEC_API_TOKEN', default=''),
    'sunat_token': config('SUNAT_API_TOKEN', default=''),
}

# ===========================================
# CONFIGURACIÓN EMAIL
# ===========================================

EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@felicita.pe')
SERVER_EMAIL = config('SERVER_EMAIL', default='admin@felicita.pe')

# ===========================================
# CONFIGURACIÓN ARCHIVOS
# ===========================================

# Tamaño máximo de archivo (5MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE', default=5242880, cast=int)
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

# Tipos de archivo permitidos
ALLOWED_FILE_TYPES = config('ALLOWED_FILE_TYPES', default='pdf,png,jpg,jpeg,xlsx,xls').split(',')

# ===========================================
# CONFIGURACIÓN CACHE
# ===========================================

CACHE_TIMEOUT = config('CACHE_TIMEOUT', default=3600, cast=int)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
        },
        'KEY_PREFIX': 'felicita',
        'TIMEOUT': CACHE_TIMEOUT,
    }
}

# ===========================================
# CONFIGURACIÓN SESIONES
# ===========================================

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=86400, cast=int)  # 1 día
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ===========================================
# LOGGING
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
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': config('LOG_FILE_MAX_SIZE', default=10485760, cast=int),  # 10MB
            'backupCount': config('LOG_BACKUP_COUNT', default=5, cast=int),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'felicita': {
            'handlers': ['console', 'file'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'aplicaciones.integraciones': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ===========================================
# CONFIGURACIÓN EMPRESA
# ===========================================

EMPRESA_CONFIG = {
    'ruc': config('EMPRESA_RUC', default='20123456789'),
    'razon_social': config('EMPRESA_RAZON_SOCIAL', default='MI EMPRESA SAC'),
    'direccion': config('EMPRESA_DIRECCION', default='AV. EJEMPLO 123, LIMA, PERU'),
    'telefono': config('EMPRESA_TELEFONO', default='01-1234567'),
    'email': config('EMPRESA_EMAIL', default='contacto@miempresa.com'),
}

# ===========================================
# CONFIGURACIÓN FELICITA
# ===========================================

FELICITA_CONFIG = {
    'version': '1.0.0',
    'ambiente': config('ENVIRONMENT', default='local'),
    'timezone': TIME_ZONE,
    'moneda_defecto': 'PEN',
    'igv_porcentaje': 18.0,
    'metodo_inventario': 'PEPS',
    'numeracion_automatica': True,
}

# ===========================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ===========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'