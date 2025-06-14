"""
CONFIGURACIÓN BASE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú
"""

import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# =============================================================================
# CONFIGURACIÓN DE RUTAS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# =============================================================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-felicita-dev-2024')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=lambda v: [s.strip() for s in v.split(',')])

# =============================================================================
# APLICACIONES DJANGO
# =============================================================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'import_export',  # Para admin import/export
    'drf_yasg',       # Para documentación API
    'drf_spectacular', # Documentación API mejorada
]

# Solo agregar en desarrollo
if DEBUG:
    THIRD_PARTY_APPS += [
        'django_extensions',
        'debug_toolbar',
    ]

LOCAL_APPS = [
    'aplicaciones.core',
    'aplicaciones.usuarios',
    'aplicaciones.inventario',
     'aplicaciones.contabilidad',
    'aplicaciones.facturacion', 
    # Comentados hasta que estén listos
    #'aplicaciones.punto_venta',
    #'aplicaciones.reportes',
    #'aplicaciones.integraciones',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE
# =============================================================================
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
    'django.middleware.locale.LocaleMiddleware',
]

# Middleware solo para desarrollo
if DEBUG:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',

    ]

# =============================================================================
# URLs Y WSGI
# =============================================================================
ROOT_URLCONF = 'felicita.urls'
WSGI_APPLICATION = 'felicita.wsgi.application'
ASGI_APPLICATION = 'felicita.asgi.application'

# =============================================================================
# TEMPLATES
# =============================================================================
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
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        },
    },
]

# =============================================================================
# BASE DE DATOS
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='felicita_db'),
        'USER': config('DB_USER', default='felicita_user'),
        'PASSWORD': config('DB_PASSWORD', default='felicita_2024_dev'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'charset': 'utf8',
        },
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
    }
}

# =============================================================================
# AUTENTICACIÓN Y AUTORIZACIÓN
# =============================================================================
AUTH_USER_MODEL = 'usuarios.Usuario'

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

# =============================================================================
# INTERNACIONALIZACIÓN (CONFIGURACIÓN PERÚ)
# =============================================================================
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Idiomas disponibles
LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]

# Configuración de localización peruana
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Formato de fechas peruano
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# =============================================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración WhiteNoise para archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# =============================================================================
# CONFIGURACIÓN DJANGO REST FRAMEWORK
# =============================================================================
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
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DATETIME_FORMAT': '%d/%m/%Y %H:%M',
    'DATE_FORMAT': '%d/%m/%Y',
    'TIME_FORMAT': '%H:%M',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# =============================================================================
# CONFIGURACIÓN JWT
# =============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# =============================================================================
# CONFIGURACIÓN CORS
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = config('DEBUG', default=False, cast=bool)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='http://localhost:3000,http://127.0.0.1:3000', 
    cast=lambda v: [s.strip() for s in v.split(',')]
)

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

# =============================================================================
# CONFIGURACIÓN CACHE (REDIS)
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
        },
        'KEY_PREFIX': 'felicita',
        'TIMEOUT': config('CACHE_TTL', default=3600, cast=int),
    }
}

# =============================================================================
# CONFIGURACIÓN EMAIL
# =============================================================================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='FELICITA <noreply@felicita.pe>')

# =============================================================================
# CONFIGURACIÓN IMPORT_EXPORT
# =============================================================================
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = False
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'import_export.tmp_storages.TempFolderStorage'

# Formatos permitidos para import/export
IMPORT_EXPORT_FORMATS = [
    'import_export.formats.base_formats.CSV',
    'import_export.formats.base_formats.XLS',
    'import_export.formats.base_formats.XLSX',
    'import_export.formats.base_formats.TSV',
    'import_export.formats.base_formats.JSON',
]

# =============================================================================
# CONFIGURACIÓN DRF SPECTACULAR (API DOCS)
# =============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'FELICITA API',
    'DESCRIPTION': 'Sistema de Facturación Electrónica para Perú',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
    },
}

# =============================================================================
# CONFIGURACIÓN DEBUG TOOLBAR (solo desarrollo)
# =============================================================================
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Para Docker
    import socket
    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']
    except:
        pass

# =============================================================================
# CONFIGURACIÓN LOGGING
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
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'felicita_dev.log'),
            'maxBytes': config('LOG_FILE_MAX_SIZE', default=10485760, cast=int),
            'backupCount': config('LOG_BACKUP_COUNT', default=5, cast=int),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'felicita': {
            'handlers': ['file', 'console'],
            'level': config('LOG_LEVEL', default='DEBUG'),
            'propagate': True,
        },
        'felicita.facturacion': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'felicita.contabilidad': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# =============================================================================
# CONFIGURACIÓN ESPECÍFICA PERÚ - FACTURACIÓN ELECTRÓNICA
# =============================================================================

# Configuración SUNAT
SUNAT_CONFIGURACION = {
    'IGV_PORCENTAJE': config('IGV_PORCENTAJE', default=18, cast=int),
    'MONEDA_BASE': config('MONEDA_BASE', default='PEN'),
    'PLAN_CUENTAS': config('PLAN_CUENTAS', default='PCGE'),
    'METODO_INVENTARIO': config('METODO_INVENTARIO', default='PEPS'),
    'IGV_TASA': 0.18,  # Para cálculos
    'MONEDAS_SOPORTADAS': ['PEN', 'USD', 'EUR'],
    'TIPOS_DOCUMENTO': {
        'DNI': '1',
        'CE': '4', 
        'RUC': '6',
        'PASSPORT': '7'
    },
    'CODIGOS_AFECTACION_IGV': {
        'gravado': '10',
        'exonerado': '20',
        'inafecto': '30',
        'exportacion': '40'
    },
    'TIPOS_COMPROBANTE': {
        'factura': '01',
        'boleta': '03',
        'nota_credito': '07',
        'nota_debito': '08',
        'guia_remision': '09'
    }
}

# Series de comprobantes
SERIES_COMPROBANTES = {
    'FACTURA': config('SERIE_FACTURA', default='F001'),
    'BOLETA': config('SERIE_BOLETA', default='B001'),
    'NOTA_CREDITO': config('SERIE_NOTA_CREDITO', default='FC01'),
    'NOTA_DEBITO': config('SERIE_NOTA_DEBITO', default='FD01'),
    'GUIA_REMISION': config('SERIE_GUIA_REMISION', default='T001'),
}

# Configuración empresa emisora
EMPRESA_CONFIGURACION = {
    'RUC': config('EMPRESA_RUC', default='20123456789'),
    'RAZON_SOCIAL': config('EMPRESA_RAZON_SOCIAL', default='EMPRESA DEMO FELICITA S.A.C.'),
    'NOMBRE_COMERCIAL': config('EMPRESA_NOMBRE_COMERCIAL', default='FELICITA DEMO'),
    'DIRECCION': config('EMPRESA_DIRECCION', default='AV. DEMO 123, SAN ISIDRO, LIMA'),
    'UBIGEO': config('EMPRESA_UBIGEO', default='150101'),
    'TELEFONO': config('EMPRESA_TELEFONO', default='01-2345678'),
    'EMAIL': config('EMPRESA_EMAIL', default='contacto@demo-felicita.pe'),
    'WEB': config('EMPRESA_WEB', default='https://demo-felicita.pe'),
}

# =============================================================================
# CONFIGURACIÓN APIS EXTERNAS
# =============================================================================

# Nubefact (OSE)
NUBEFACT_CONFIGURACION = {
    'MODO': config('NUBEFACT_MODO', default='demo'),
    'API_URL': config('NUBEFACT_API_URL', default='https://demo.nubefact.com/api/v1'),
    'TOKEN': config('NUBEFACT_TOKEN', default='demo_token'),
    'RUC_EMISOR': config('NUBEFACT_RUC_EMISOR', default='20123456789'),
    'USUARIO_SOL': config('NUBEFACT_USUARIO_SOL', default='MODDATOS'),
    'CLAVE_SOL': config('NUBEFACT_CLAVE_SOL', default='MODDATOS'),
    'AUTO_SEND': config('NUBEFACT_AUTO_SEND', default=True, cast=bool),
    'RETRY_ATTEMPTS': config('NUBEFACT_RETRY_ATTEMPTS', default=3, cast=int),
    'TIMEOUT': config('NUBEFACT_TIMEOUT', default=30, cast=int),
}

# APIs Perú (RENIEC/SUNAT)
APIS_PERU = {
    'RENIEC_URL': config('RENIEC_API_URL', default='https://api.apis.net.pe/v1/dni'),
    'RENIEC_TOKEN': config('RENIEC_API_TOKEN', default=''),
    'SUNAT_URL': config('SUNAT_API_URL', default='https://api.apis.net.pe/v1/ruc'),
    'SUNAT_TOKEN': config('SUNAT_API_TOKEN', default=''),
}

# =============================================================================
# CONFIGURACIÓN CONTABLE
# =============================================================================
CONTABILIDAD_CONFIGURACION = {
    'PLAN_CUENTAS_DEFAULT': 'PCGE',
    'GENERAR_ASIENTOS_AUTOMATICOS': config('CONTABILIDAD_ASIENTOS_AUTO', default=True, cast=bool),
    'PERMITIR_EDICION_ASIENTOS_CONTABILIZADOS': config('CONTABILIDAD_EDITAR_CONTABILIZADOS', default=False, cast=bool),
    'PERIODO_ACTUAL_AUTO': config('CONTABILIDAD_PERIODO_AUTO', default=True, cast=bool),
    'CERRAR_PERIODO_AUTOMATICO': config('CONTABILIDAD_CERRAR_AUTO', default=False, cast=bool),
}

# =============================================================================
# CONFIGURACIÓN ADICIONAL
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de sesiones
SESSION_COOKIE_AGE = config('SESSION_TIMEOUT', default=28800, cast=int)  # 8 horas
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_SAVE_EVERY_REQUEST = True

# Configuración CSRF
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# Configuración de archivos subidos
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Configuración de timezone
USE_TZ = True